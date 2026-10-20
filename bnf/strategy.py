# bnf/strategy.py
"""
BNF 역추세 전략 공통 모듈 (백테스트와 실시간 모니터링이 함께 사용)

- 감시 종목 (미국 시총 50위)
- 전략 모드별 파라미터
- 기술적 지표 및 매수/매도 신호 계산
"""

from dataclasses import dataclass

import pandas as pd

# 미국 시총 50위 종목 (티커 → 한글 이름)
TOP50_STOCKS = {
  'AAPL': '애플', 'MSFT': '마이크로소프트', 'GOOGL': '구글', 'AMZN': '아마존',
  'NVDA': '엔비디아', 'META': '메타', 'TSLA': '테슬라', 'BRK-B': '버크셔',
  'AVGO': '브로드컴', 'LLY': '일라이 릴리', 'JPM': 'JP모건', 'UNH': '유나이티드헬스',
  'XOM': '엑슨모빌', 'V': '비자', 'PG': '프록터앤갬블', 'JNJ': '존슨앤존슨',
  'MA': '마스터카드', 'HD': '홈디포', 'CVX': '쉐브론', 'MRK': '머크',
  'ABBV': '애브비', 'KO': '코카콜라', 'ADBE': '어도비', 'PEP': '펩시코',
  'COST': '코스트코', 'WMT': '월마트', 'BAC': '뱅크오브아메리카', 'CRM': '세일즈포스',
  'TMO': '써모피셔', 'NFLX': '넷플릭스', 'ACN': '액센추어', 'LIN': '린데',
  'MCD': '맥도날드', 'ABT': '애보트', 'CSCO': '시스코', 'AMD': 'AMD',
  'PM': '필립모리스', 'TXN': '텍사스인스트루먼츠', 'DHR': '다나허', 'DIS': '디즈니',
  'INTC': '인텔', 'VZ': '버라이즌', 'WFC': '웰스파고', 'COP': '코노코필립스',
  'BMY': '브리스톨마이어스', 'NOW': '서비스나우', 'CAT': '캐터필러', 'NEE': '넥스트에라',
  'UPS': 'UPS', 'RTX': 'RTX'
}


@dataclass(frozen=True)
class BNFParams:
  """BNF 전략 파라미터"""
  # 지표 기간
  rsi_period: int = 14
  williams_period: int = 14
  ema_short: int = 20
  ema_long: int = 25  # BNF가 사용한 25일 이동평균
  volume_ma_period: int = 20
  max_holding_days: int = 3  # BNF 스타일: 최대 3일

  # 신호 임계값 (기본값 = balanced)
  rsi_oversold: float = 35
  rsi_overbought: float = 65
  williams_oversold: float = -75
  williams_overbought: float = -25
  volume_threshold: float = 1.2
  ma_oversold_threshold: float = 0.80  # 25일 평균 대비 20% 하락

  @classmethod
  def for_mode(cls, strategy_mode: str) -> "BNFParams":
    """전략 모드별 파라미터 (알 수 없는 모드는 conservative)"""
    if strategy_mode == "aggressive":
      # 공격적: 더 빠른 진입
      return cls(rsi_oversold=40, rsi_overbought=60,
                 williams_oversold=-70, williams_overbought=-30,
                 volume_threshold=1.1,
                 ma_oversold_threshold=0.85)  # 15% 하락에서도 진입
    if strategy_mode == "balanced":
      # 균형: 실제 BNF에 가까운 설정
      return cls()
    # 보수적: 더 엄격한 기준
    return cls(rsi_oversold=30, rsi_overbought=70,
               williams_oversold=-80, williams_overbought=-20,
               volume_threshold=1.3,
               ma_oversold_threshold=0.75)  # 25% 하락


def calculate_bnf_indicators(data: pd.DataFrame, p: BNFParams) -> pd.DataFrame:
  """BNF 스타일 기술적 지표 및 매수/매도 신호 계산"""
  if len(data) < max(p.rsi_period, p.williams_period, p.ema_long):
    return data

  # RSI 계산
  delta = data['Close'].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=p.rsi_period).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=p.rsi_period).mean()
  rs = gain / loss
  data['RSI'] = 100 - (100 / (1 + rs))

  # Williams %R 계산
  high_max = data['High'].rolling(window=p.williams_period).max()
  low_min = data['Low'].rolling(window=p.williams_period).min()
  data['Williams_R'] = -100 * (high_max - data['Close']) / (high_max - low_min)

  # EMA 계산
  data['EMA_20'] = data['Close'].ewm(span=p.ema_short).mean()
  data['EMA_25'] = data['Close'].ewm(span=p.ema_long).mean()  # BNF의 25일

  # 거래량 분석
  data['Volume_MA'] = data['Volume'].rolling(
      p.volume_ma_period).mean() if 'Volume' in data.columns else 1
  data['Volume_Ratio'] = data['Volume'] / data[
    'Volume_MA'] if 'Volume' in data.columns else 1

  # 가격 모멘텀
  data['Price_Change_Pct'] = data['Close'].pct_change() * 100
  data['Price_MA_5'] = data['Close'].rolling(5).mean()

  # BNF 스타일: 25일 이동평균 대비 하락률
  data['MA25_Ratio'] = data['Close'] / data['EMA_25']
  data['MA25_Oversold'] = data['MA25_Ratio'] <= p.ma_oversold_threshold

  # 기본 과매수/과매도 조건
  data['RSI_Oversold'] = data['RSI'] <= p.rsi_oversold
  data['RSI_Overbought'] = data['RSI'] >= p.rsi_overbought
  data['Williams_Oversold'] = data['Williams_R'] <= p.williams_oversold
  data['Williams_Overbought'] = data['Williams_R'] >= p.williams_overbought

  # BNF 스타일 매수 신호 (OR 조건으로 완화)
  data['BNF_Buy_Signal'] = (
    # 조건 1: RSI 과매도 + 거래량 증가
      (data['RSI_Oversold'] & (data['Volume_Ratio'] > p.volume_threshold)) |

      # 조건 2: Williams %R 과매도 + 거래량 증가
      (data['Williams_Oversold'] & (data['Volume_Ratio'] > p.volume_threshold)) |

      # 조건 3: BNF 핵심 - 25일 평균 대비 큰 하락 + 반등 시작
      (data['MA25_Oversold'] &
       (data['Close'] > data['Close'].shift(1)) &  # 반등 시작
       (data['Volume_Ratio'] > 1.1))  # 거래량 증가
  )

  # BNF 스타일 매도 신호
  data['BNF_Sell_Signal'] = (
    # 조건 1: RSI 과매수
      data['RSI_Overbought'] |

      # 조건 2: Williams %R 과매수
      data['Williams_Overbought'] |

      # 조건 3: 25일 평균 대비 충분한 상승 (수익 실현)
      (data['MA25_Ratio'] >= 1.10)  # 25일 평균 대비 10% 상승시 수익실현
  )

  return data

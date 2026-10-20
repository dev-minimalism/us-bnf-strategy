# BNF 역추세 트레이딩 시스템 (타카시 코테가와 스타일)

[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![yfinance](https://img.shields.io/badge/yfinance-410093)](https://pypi.org/project/yfinance/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)

타카시 코테가와(BNF)의 전설적인 역추세 전략을 기반으로 한 자동 트레이딩 시스템입니다.

## 🎯 BNF 전략 개요

### "대중과 반대로 행동하라" - 타카시 코테가와

BNF는 $13,600을 $153 million으로 불린 일본의 전설적인 트레이더로, 과매수/과매도 반전을 노리는 역추세 전략의 대가입니다.

## 🚀 주요 기능

### 1. BNF 역추세 전략
- **과매수/과매도 반전 포착**: RSI + Williams %R 이중 확인
- **2-3일 단기 보유**: BNF의 특징적인 짧은 보유 기간
- **거래량 검증**: 반전 신호의 신뢰도 향상
- **고확률 셋업만 선별**: 엄격한 진입 조건

### 2. BNF 백테스트 모듈 (`bnf/backtest.py`)
- 미국 시총 50위 종목 자동 분석
- BNF 특화 성과 지표 (평균 보유 기간 포함)
- 시간 기반 강제 청산 (최대 3일)
- BNF 스타일 포트폴리오 관리
- 역추세 전용 리포트 생성

### 3. BNF 실시간 모니터링 (`bnf/monitor.py`)
- 실시간 반전 신호 감지
- BNF 특화 텔레그램 알림
- 포지션 자동 관리 (3일 강제 청산)
- 중복 알림 방지 시스템

## 📦 설치 방법

### 1. 필수 라이브러리 설치
```bash
# requirements.txt
yfinance>=0.2.18
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
requests>=2.31.0
python-telegram-bot>=20.0

pip install -r requirements.txt
```

### 2. 파일 구조
```
us-bnf-strategy/
├── bnf/                            # BNF 패키지
│   ├── __main__.py                 # 메인 실행 파일 (python -m bnf)
│   ├── strategy.py                 # 공통 전략: 지표·신호·파라미터·종목 목록
│   ├── backtest.py                 # 백테스트 모듈
│   └── monitor.py                  # 실시간 모니터링 모듈
├── scripts/                        # 백그라운드 실행·systemd 설치 스크립트
├── requirements.txt                # 필수 라이브러리
├── bnf_output_files/               # BNF 결과 저장 폴더
│   ├── results/                    # 백테스트 결과 CSV
│   ├── charts/                     # 성과 차트
│   ├── reports/                    # 투자 리포트
│   └── logs/                       # 시스템 로그
└── README.md                       # 이 파일
```

## 🔧 사용 방법

### 기본 실행
```bash
# BNF 백테스트만 실행
python -m bnf --mode backtest

# BNF 실시간 모니터링만 실행  
python -m bnf --mode monitor

# BNF 백그라운드 모니터링
python -m bnf --mode monitor-default

# 백테스트 후 모니터링 (기본값)
python -m bnf --mode both
```

### BNF 텔레그램 알림 설정

1. **봇 생성**: @BotFather에서 새 봇 생성
2. **토큰 획득**: 봇 토큰 복사
3. **채팅 ID 확인**: @userinfobot에서 chat_id 확인
4. **환경변수 설정**:
   ```bash
   export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export US_BNF_STRATEGY_TELEGRAM_CHAT_ID="your_chat_id_here"
   ```

### BNF 텔레그램 명령어
- `/ticker AAPL` - 개별 종목 BNF 분석
- `/status` - BNF 모니터링 상태 확인
- `/start` - BNF 도움말 보기

### 개별 모듈 사용

#### BNF 백테스트만 실행

```python
from bnf.backtest import BNFCounterTrendBacktest

backtest = BNFCounterTrendBacktest(
    initial_capital=10000,
    strategy_mode="balanced"  # conservative, balanced, aggressive
)
results = backtest.run_multi_stock_backtest("2022-01-01", "2024-01-01")
print(results)
```

#### BNF 실시간 모니터링만 실행

```python
from bnf.monitor import BNFCounterTrendMonitor

monitor = BNFCounterTrendMonitor(
    telegram_bot_token="your_token",
    telegram_chat_id="your_chat_id"
)
monitor.start_monitoring(scan_interval=300)  # 5분 간격
```

## 📊 BNF 매매 전략 상세

### 매수 조건 (역추세 진입)
- **과매도 조건**: RSI ≤ 30 AND Williams %R ≤ -80
- **반전 신호**: 가격 상승 시작 + 단기 평균 돌파
- **거래량 확인**: 평균 거래량의 1.2배 이상
- **추세 방향**: EMA 20/50 참고

### 매도 조건 (빠른 차익실현)
- **신호 매도**: RSI ≥ 70 AND Williams %R ≥ -20
- **시간 매도**: 최대 3일 보유 후 강제 청산
- **손절**: RSI < 30 (추가 하락 방지)

### BNF 기술적 지표
- **RSI**: 14일 (과매도: 30, 과매수: 70)
- **Williams %R**: 14일 (과매도: -80, 과매수: -20)
- **EMA**: 20일/50일 (추세 확인)
- **거래량**: 20일 이동평균 대비 비율

## 📈 BNF 백테스트 결과 예시

```
Symbol  Total_Return(%)  Win_Rate(%)  Avg_Holding_Days  Profit_Factor  Max_Drawdown(%)
AAPL           18.45         72.3           2.1            2.4            6.8
MSFT           15.67         69.8           2.3            2.1            5.9
NVDA           32.18         65.4           2.0            3.2           12.4
TSLA           28.91         58.7           2.4            2.8           18.7
```

## ⚠️ BNF 전략 주의사항

1. **역추세 특성**: 강한 추세 시장에서는 성과 제한
2. **단기 보유**: 2-3일 내 빠른 결정 필요
3. **거래량 중요**: 반전 신호의 신뢰도 확인 필수
4. **감정 배제**: BNF처럼 데이터 기반 결정
5. **분산 투자**: 여러 종목으로 리스크 분산

## 🛠️ BNF 설정 커스터마이징

### BNF 전략 파라미터 변경
백테스트와 실시간 모니터링은 `bnf/strategy.py`의 지표·신호 계산을 함께 사용합니다. 한 곳만 수정하면 양쪽에 반영됩니다.

```python
# bnf/strategy.py에서 수정
@dataclass(frozen=True)
class BNFParams:
  max_holding_days: int = 3          # 최대 보유 기간
  rsi_oversold: float = 35           # 기본값 = balanced 모드
  ...

  @classmethod
  def for_mode(cls, strategy_mode):  # conservative / balanced / aggressive 값
    ...
```

- 감시 종목: `bnf/strategy.py`의 `TOP50_STOCKS`
- 실시간 모니터링은 balanced 모드 파라미터를 사용합니다.
- 알림 쿨다운: `bnf/monitor.py`의 `self.alert_cooldown = 3600` (초)

## 📱 BNF 텔레그램 알림 예시

### BNF 매수 신호
```
🚀 BNF 역추세 매수 신호!

종목: AAPL (애플)
현재가: $150.25
반전 이유: 과매도 반전 + 거래량급증
RSI: 28.3 (과매도)
Williams %R: -82.1 (과매도)
거래량: 1.4x
목표 기간: 2-3일
시간: 2024-01-15 14:30:00

⚡ 타카시 코테가와 스타일 - 바닥에서 반등 포착!
```

### BNF 매도 신호
```
🔴 BNF 청산 신호!

종목: AAPL (애플)
현재가: $158.75
진입가: $150.25
보유기간: 2일
수익률: +5.7%
청산 이유: 수익 실현
RSI: 71.2
Williams %R: -18.5
시간: 2024-01-17 10:15:00

💰 BNF 스타일 - 빠른 차익실현!
```

## 🔍 문제 해결

### 1. BNF 모듈 import 오류
```bash
# 프로젝트 루트(bnf/ 폴더가 있는 곳)에서 실행하는지 확인
ls bnf/
python -m bnf --help

# Python 경로 확인
python -c "import sys; print(sys.path)"
```

### 2. BNF 데이터 다운로드 실패
```python
# yfinance 업데이트
pip install --upgrade yfinance

# BNF 네트워크 연결 확인
import yfinance as yf
stock = yf.Ticker("AAPL")
print(stock.history(period="5d"))
```

### 3. BNF 텔레그램 알림 실패
```python
# BNF 봇 토큰과 채팅 ID 확인
monitor.test_telegram_connection()

# 수동으로 테스트
import requests
url = f"https://api.telegram.org/bot{TOKEN}/getMe"
print(requests.get(url).json())
```

### 4. BNF 메모리 부족
```python
# BNF 백테스트 종목 수 줄이기
results = backtest.run_multi_stock_backtest(
    start_date, end_date, max_stocks=10  # 기본 20에서 10으로
)
```

## 📊 BNF 성과 지표 설명

- **Total_Return(%)**: 총 수익률 (초기 자본 대비)
- **Win_Rate(%)**: 승률 (수익 거래 / 전체 거래)
- **Avg_Holding_Days**: 평균 보유 기간 (BNF 특화 지표)
- **Profit_Factor**: 손익비 (평균 수익 / 평균 손실의 절댓값)
- **Max_Drawdown(%)**: 최대 낙폭 (고점 대비 최대 하락률)

## 🎯 BNF 전략의 핵심 철학

### 타카시 코테가와의 명언들
- **"대중과 반대로 행동하라"**
- **"바닥에서 사고, 천정에서 팔아라"**
- **"감정을 배제하고 데이터에 의존하라"**
- **"빠른 차익실현이 안전하다"**

### BNF 스타일 특징
1. **역추세 전문**: 추세 추종이 아닌 반전 포착
2. **단기 보유**: 2-3일 내 빠른 거래
3. **고확률 선별**: 엄격한 진입 조건
4. **리스크 관리**: 시간 기반 강제 청산

## 🔄 백그라운드 실행 (서버용)

### Ubuntu/Linux
```bash
# BNF 백그라운드 실행 / 상태 / 로그 / 종료
scripts/start_monitor.sh
scripts/status_monitor.sh
scripts/view_logs.sh
scripts/stop_monitor.sh

# systemd 서비스로 등록 (bnf-monitor)
scripts/install_service.sh
```

### Windows
```cmd
# BNF 백그라운드 실행
start /b python -m bnf --mode monitor-default

# 작업 관리자에서 python.exe 프로세스 종료
```

## 📊 BNF 포트폴리오 시뮬레이션

### 동적 자금 관리
- **최대 동시 보유**: 10개 종목
- **투자 우선순위**: RSI 낮은 순 (더 과매도)
- **자금 배분**: 신호 발생시 동적 투자
- **강제 청산**: 3일 후 자동 매도

### BNF 리스크 관리
- **분산 투자**: 여러 종목 동시 보유
- **시간 제한**: 최대 3일 보유
- **손절 규칙**: RSI < 30 추가 하락시
- **수익 실현**: 과매수 신호시 즉시 매도

## 🔄 버전 히스토리

### v2.0.0 (2024-12-01) - BNF Edition
- **전략 변경**: 볼린저 스퀴즈 → BNF 역추세
- **새로운 지표**: RSI + Williams %R 이중 확인
- **포지션 관리**: 2-3일 단기 보유 시스템
- **BNF 특화**: 타카시 코테가와 스타일 구현
- **알림 개선**: BNF 전용 텔레그램 메시지

### v1.0.0 (2024-01-01) - Legacy
- 초기 볼린저 스퀴즈 전략
- 기본 백테스트 및 모니터링

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/BNFFeature`)
3. Commit your changes (`git commit -m 'Add BNF Feature'`)
4. Push to the branch (`git push origin feature/BNFFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## ⚖️ 면책조항

본 소프트웨어는 교육 및 연구 목적으로만 제공됩니다. 타카시 코테가와(BNF)의 전략을 모델로 했지만, 실제 투자에 사용하여 발생하는 손실에 대해 개발자는 책임지지 않습니다. 투자는 본인의 책임 하에 신중하게 결정하시기 바랍니다.

**"대중과 반대로 행동하라"**의 철학을 잊지 마세요.

## 📞 지원

- 문제 신고: GitHub Issues
- 기능 요청: GitHub Discussions
- BNF 전략 문의: Discussions > BNF Strategy

---

**Happy Counter-Trend Trading! 🎯📈**

*"The best time to buy is when everyone else is selling, and the best time to sell is when everyone else is buying."* - BNF (Takashi Kotegawa)

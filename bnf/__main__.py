"""
BNF 역추세 트레이딩 시스템 - 메인 실행 파일
타카시 코테가와(BNF) 스타일 역추세 전략

사용법:
    python -m bnf --mode backtest      # BNF 백테스트만 실행
    python -m bnf --mode monitor       # BNF 실시간 모니터링만 실행
    python -m bnf --mode monitor-default  # BNF 백그라운드 모니터링
    python -m bnf --mode both          # 백테스트 후 모니터링 실행 (기본값)

텔레그램 설정:
    export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN="your_bot_token"
    export US_BNF_STRATEGY_TELEGRAM_CHAT_ID="your_chat_id"

BNF 전략 특징:
    - 과매수/과매도 반전 포착
    - 2-3일 단기 보유
    - RSI + Williams %R 이중 확인
    - 고확률 셋업만 선별
"""

import argparse
import logging
import os
import signal
import sys
from datetime import datetime, timedelta

from .backtest import BNFCounterTrendBacktest
from .monitor import BNFCounterTrendMonitor


# ===================================================================================
# 로깅 설정
# ===================================================================================

def setup_bnf_logging():
  """BNF 백그라운드 실행을 위한 로깅 설정"""
  log_dir = "bnf_output_files/logs"
  os.makedirs(log_dir, exist_ok=True)

  log_filename = os.path.join(log_dir,
                              f"bnf_monitor_{datetime.now().strftime('%Y%m%d')}.log")

  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s',
      handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
      ]
  )

  return logging.getLogger(__name__)


# ===================================================================================
# BNF 백그라운드 모니터링
# ===================================================================================

def run_bnf_monitor_default():
  """BNF 백그라운드 모니터링 실행 (환경변수 이름 통일)"""
  logger = setup_bnf_logging()

  print("=" * 80)
  print("📡 BNF 역추세 백그라운드 모니터링 (기본 설정)")
  print("=" * 80)

  # 환경변수 이름 통일
  telegram_bot_token = os.getenv('US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN')
  telegram_chat_id = os.getenv('US_BNF_STRATEGY_TELEGRAM_CHAT_ID')
  scan_interval = 300  # 5분 간격

  # 텔레그램 설정 검증 강화
  if not telegram_bot_token or not telegram_chat_id:
    print("❌ BNF 텔레그램 설정이 필요합니다!")
    print("💡 설정 방법:")
    print("   export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("   export US_BNF_STRATEGY_TELEGRAM_CHAT_ID='your_chat_id'")
    print("\n⚠️ 백그라운드 모니터링에는 텔레그램 알림이 필수입니다.")
    return

  logger.info("BNF 백그라운드 모니터링 시작")
  logger.info(f"스캔 간격: {scan_interval}초 ({scan_interval // 60}분)")
  logger.info(f"로그 파일: bnf_output_files/logs/bnf_monitor_{datetime.now().strftime('%Y%m%d')}.log")

  print(f"🎯 BNF 백그라운드 모니터링 설정:")
  print(f"   📊 감시 종목: 50개 (미국 시총 상위)")
  print(f"   ⏰ 스캔 간격: 5분")
  print(f"   📱 텔레그램 알림: 활성화")
  print(f"   📝 로그 파일: bnf_output_files/logs/bnf_monitor_{datetime.now().strftime('%Y%m%d')}.log")
  print(f"   🔄 자동 재시작: 활성화")
  print(f"   🎯 전략: 타카시 코테가와(BNF) 역추세")
  print(f"   🤖 텔레그램 명령어: /ticker, /status, /start")

  # 시그널 핸들러 설정
  def signal_handler(signum, frame):
    logger.info(f"BNF 종료 신호 수신: {signum}")
    print(f"\n⏹️ BNF 모니터링을 안전하게 종료합니다...")
    try:
      if 'monitor' in locals():
        monitor.stop_monitoring()
    except:
      pass
    sys.exit(0)

  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  # BNF 모니터링 시스템 초기화
  try:
    monitor = BNFCounterTrendMonitor(
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id
    )

    # 텔레그램 연결 테스트
    if monitor.telegram_bot_token:
      print(f"\n🤖 BNF 텔레그램 봇 연결 테스트 중...")
      if monitor.test_telegram_connection():
        print("✅ BNF 텔레그램 연결 성공")
        print("📱 사용 가능한 명령어:")
        print("   • /ticker AAPL - 개별 종목 BNF 분석")
        print("   • /status - BNF 모니터링 상태 확인")
        print("   • /start - BNF 도움말 보기")
      else:
        print("⚠️ BNF 텔레그램 연결 실패 - 로그만 출력")

    print(f"\n" + "=" * 80)
    print("🚀 BNF 백그라운드 모니터링 시작!")
    print("   - 타카시 코테가와 스타일 역추세 전략")
    print("   - 과매수/과매도 반전 신호 전문")
    print("   - 2-3일 단기 보유 목표")
    print("   - RSI + Williams %R 이중 확인")
    print("   - 신호 발생시 텔레그램으로 즉시 알림")
    print("   - 텔레그램에서 /ticker 명령어로 개별 종목 분석 가능")
    print("   - 5회 스캔마다 상태 요약을 전송합니다")
    print("   - 오류 발생시 자동으로 재시작합니다")
    print("   - 종료하려면: kill -TERM [PID] 또는 Ctrl+C")
    print("=" * 80)

    # BNF 연속 모니터링 실행
    monitor.run_continuous_monitoring(scan_interval)

  except Exception as e:
    logger.error(f"BNF 모니터링 초기화 실패: {e}")
    print(f"❌ BNF 모니터링 초기화 실패: {e}")
    print(f"💡 텔레그램 설정이나 네트워크 연결을 확인해주세요.")
    sys.exit(1)


# ===================================================================================
# BNF 백테스트 실행
# ===================================================================================

def run_bnf_backtest():
  """BNF 백테스트 실행 (전략 설명 개선)"""
  print("=" * 80)
  print("🚀 BNF 역추세 전략 백테스트")
  print("=" * 80)

  print("💡 타카시 코테가와(BNF) 전략이란?")
  print("   • 일본의 전설적 트레이더 (13,600달러 → 1억5천만달러)")
  print("   • 25일 이동평균 대비 20% 이상 하락한 주식 매수")
  print("   • 과매수/과매도 반전 신호 포착 전문")
  print("   • 2-3일 단기 보유 후 빠른 차익실현")
  print("   • '대중과 반대로 행동하라'는 철학")

  # 초기 자금 설정
  print(f"\n💰 초기 자금을 설정하세요:")
  print("1. $10,000 (1만 달러) - 개인 투자자")
  print("2. $50,000 (5만 달러) - 중급 투자자")
  print("3. $100,000 (10만 달러) - 고급 투자자")
  print("4. 사용자 정의")

  capital_options = {"1": 10000, "2": 50000, "3": 100000}

  try:
    capital_choice = input("\n초기 자금 선택 (1-4, 기본값: 1): ").strip() or "1"

    if capital_choice == "4":
      custom_capital = float(input("사용자 정의 금액 ($): "))
      initial_capital = custom_capital
    else:
      initial_capital = capital_options.get(capital_choice, 10000)

    print(f"✅ 선택된 초기 자금: ${initial_capital:,.2f}")

  except ValueError:
    print("잘못된 입력입니다. 기본값($10,000)으로 설정합니다.")
    initial_capital = 10000

  # BNF 전략 모드 선택 (설명 개선)
  print(f"\n🎯 BNF 전략 모드를 선택하세요:")
  print("1. 보수적 전략 (25% 하락에서 진입, RSI 30/70)")
  print("   → BNF 원조 스타일, 가장 안전한 설정")
  print("2. 균형 전략 (20% 하락에서 진입, RSI 35/65) ⭐ 추천")
  print("   → 실제 BNF와 가장 유사한 설정")
  print("3. 공격적 전략 (15% 하락에서 진입, RSI 40/60)")
  print("   → 더 많은 기회 포착, 리스크 증가")

  try:
    strategy_choice = input("\n전략 선택 (1-3, 기본값: 2): ").strip() or "2"
    strategy_map = {"1": "conservative", "2": "balanced", "3": "aggressive"}
    strategy_mode = strategy_map.get(strategy_choice, "balanced")

    strategy_names = {"1": "보수적", "2": "균형", "3": "공격적"}
    print(f"✅ 선택된 전략: {strategy_names.get(strategy_choice, '균형')} BNF 전략")
  except:
    strategy_mode = "balanced"
    print("✅ 기본 전략: 균형 BNF 전략")

  # BNF 백테스트 인스턴스 생성
  backtest = BNFCounterTrendBacktest(initial_capital=initial_capital, strategy_mode=strategy_mode)

  # 백테스트 기간 설정
  end_date = datetime.now().strftime('%Y-%m-%d')
  start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # 2년간

  print(f"📅 분석 기간: {start_date} ~ {end_date} (약 2년)")

  # 종목 수 선택
  print(f"\n📊 분석할 종목 수를 선택하세요:")
  print("1. 10개 종목 (빠름, 5분 소요)")
  print("2. 20개 종목 (표준, 10분 소요)")
  print("3. 30개 종목 (상세, 15분 소요)")
  print("4. 전체 50개 종목 (완전, 25분 소요)")

  stock_options = {"1": 10, "2": 20, "3": 30, "4": 50}

  try:
    stock_choice = input("\n종목 수 선택 (1-4, 기본값: 2): ").strip() or "2"
    max_stocks = stock_options.get(stock_choice, 20)
    print(f"✅ 선택된 종목 수: {max_stocks}개")
  except:
    max_stocks = 20

  # BNF 백테스트 유형 선택 (통합 포트폴리오 우선 권장)
  print(f"\n📊 BNF 백테스트 유형을 선택하세요:")
  print("1. BNF 통합 포트폴리오 (동적 자금 관리) ⭐ 강력 추천")
  print("   → 실제 BNF 방식과 동일한 자금 관리")
  print("2. 개별 종목 분석 (각 종목별 독립 분석)")
  print("   → 종목별 상세 성과 확인")
  print("3. 통합 + 개별 (둘 다 실행)")
  print("   → 완전 분석 (시간 오래 걸림)")

  try:
    backtest_choice = input("\n백테스트 유형 (1-3, 기본값: 1): ").strip() or "1"

    if backtest_choice == "1":
      run_individual = False
      run_portfolio = True
      print("✅ BNF 통합 포트폴리오 백테스트 선택")
    elif backtest_choice == "2":
      run_individual = True
      run_portfolio = False
      print("✅ 개별 종목 분석 선택")
    else:
      run_individual = True
      run_portfolio = True
      print("✅ 통합 + 개별 분석 선택")
  except:
    run_individual = False
    run_portfolio = True
    print("✅ 기본값: BNF 통합 포트폴리오 백테스트")

  if max_stocks >= 30:
    print(f"⚠️ {max_stocks}개 종목 분석은 시간이 오래 걸릴 수 있습니다.")
    confirm = input("계속 진행하시겠습니까? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
      print("백테스트를 취소합니다.")
      return

  try:
    if run_portfolio:
      print(f"\n🚀 BNF 통합 포트폴리오 백테스트 실행...")
      portfolio_result = backtest.run_bnf_portfolio_backtest(start_date,
                                                             end_date,
                                                             max_stocks=max_stocks)

      if portfolio_result:
        print(f"\n🎉 BNF 통합 포트폴리오 백테스트 완료!")
        print(f"📊 최종 수익률: {portfolio_result['total_return']:.2f}%")
        print(f"💰 최종 자산: ${portfolio_result['final_value']:,.2f}")
        print(f"⏰ 평균 보유기간: {portfolio_result['avg_holding_days']:.1f}일")
      else:
        print("❌ BNF 통합 포트폴리오 백테스트 실패")

    if run_individual:
      print(f"\n🔍 BNF 개별 종목 분석 실행...")
      comprehensive_results = backtest.run_comprehensive_analysis(
          start_date=start_date,
          end_date=end_date,
          max_stocks=max_stocks,
          detailed_analysis="top5",
          save_charts=False
      )

      if comprehensive_results:
        print(f"\n✅ BNF 개별 종목 분석 완료!")
        print(
          f"📊 총 {len(comprehensive_results.get('summary_results', []))}개 종목 분석")

        # BNF 투자 권장사항
        summary_results = comprehensive_results.get('summary_results')
        if not summary_results.empty:
          print(f"\n🏆 BNF 추천 종목 (상위 3개):")
          top_3 = summary_results.head(3)
          for i, (_, row) in enumerate(top_3.iterrows()):
            print(
              f"{i + 1}. {row['Symbol']}: {row['Total_Return(%)']}% (보유: {row['Avg_Holding_Days']}일)")
      else:
        print("❌ BNF 개별 종목 분석 실패")

  except KeyboardInterrupt:
    print(f"\n⏹️ 사용자에 의해 BNF 백테스트가 중단되었습니다.")
  except Exception as e:
    print(f"❌ BNF 백테스트 중 오류 발생: {e}")
    print(f"\n🔄 기본 BNF 백테스트를 실행합니다...")

    try:
      results_df = backtest.run_multi_stock_backtest(start_date, end_date,
                                                     max_stocks=10)
      if not results_df.empty:
        print(f"\n📊 기본 BNF 백테스트 결과 (상위 5개):")
        print(results_df.head().to_string(index=False))
        backtest.save_results_to_csv(results_df)

        avg_return = results_df['Total_Return(%)'].mean()
        avg_holding = results_df['Avg_Holding_Days'].mean()
        print(f"\n📈 BNF 간단 요약:")
        print(f"   평균 수익률: {avg_return:.2f}%")
        print(f"   평균 보유기간: {avg_holding:.1f}일")
      else:
        print("❌ 기본 BNF 백테스트 결과도 없습니다.")
    except Exception as fallback_error:
      print(f"❌ 기본 BNF 백테스트도 실패했습니다: {fallback_error}")


# ===================================================================================
# BNF 실시간 모니터링 실행
# ===================================================================================

def run_bnf_monitor():
  """BNF 실시간 모니터링 실행 (텔레그램 설정 검증 강화)"""
  print("=" * 80)
  print("📡 BNF 역추세 실시간 자동 모니터링")
  print("=" * 80)

  # 환경변수 이름 통일
  telegram_bot_token = os.getenv('US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN')
  telegram_chat_id = os.getenv('US_BNF_STRATEGY_TELEGRAM_CHAT_ID')

  if not telegram_bot_token or not telegram_chat_id:
    print("⚠️ BNF 텔레그램 설정이 필요합니다!")
    print("\n💡 설정 방법:")
    print("   1. @BotFather에서 봇 생성 후 토큰 획득")
    print("   2. @userinfobot에서 chat_id 확인")
    print("   3. 환경변수 설정:")
    print("      export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("      export US_BNF_STRATEGY_TELEGRAM_CHAT_ID='your_chat_id'")

    print("\n🔧 또는 다음 명령어로 설정:")
    print("   # Linux/Mac")
    print("   echo 'export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN=\"your_token\"' >> ~/.bashrc")
    print("   echo 'export US_BNF_STRATEGY_TELEGRAM_CHAT_ID=\"your_chat_id\"' >> ~/.bashrc")
    print("   source ~/.bashrc")

    print("\n   # Windows")
    print("   set US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN=your_token")
    print("   set US_BNF_STRATEGY_TELEGRAM_CHAT_ID=your_chat_id")

    print("\n❌ 텔레그램 설정 없이는 BNF 모니터링을 실행할 수 없습니다.")
    print("💡 설정 후 다시 실행해주세요.")
    return
  else:
    print("✅ BNF 텔레그램 설정 확인됨")

  print(f"\n⚙️ BNF 모니터링 설정:")
  print("1. 5분 간격 (기본값)")
  print("2. 10분 간격")
  print("3. 15분 간격")
  print("4. 30분 간격")
  print("5. 사용자 정의")

  interval_options = {"1": 300, "2": 600, "3": 900, "4": 1800}

  try:
    choice = input("\n스캔 간격 선택 (1-5, 기본값: 1): ").strip() or "1"

    if choice == "5":
      custom_minutes = int(input("사용자 정의 간격 (분): "))
      scan_interval = custom_minutes * 60
    else:
      scan_interval = interval_options.get(choice, 300)

    print(f"✅ 스캔 간격: {scan_interval}초 ({scan_interval // 60}분)")

  except ValueError:
    print("잘못된 입력입니다. 기본값(5분)으로 설정합니다.")
    scan_interval = 300

  monitor = BNFCounterTrendMonitor(
      telegram_bot_token=telegram_bot_token,
      telegram_chat_id=telegram_chat_id
  )

  print(f"\n🎯 BNF 모니터링 설정 완료:")
  print(f"   📊 감시 종목: {len(monitor.watchlist)}개 (미국 시총 50위)")
  print(f"   ⏰ 스캔 간격: {scan_interval // 60}분")
  print(f"   📱 텔레그램 알림: 활성화")
  print(f"   🕐 시장 시간 체크: 자동")
  print(f"   🎯 전략: 타카시 코테가와(BNF) 역추세")
  print(f"   🤖 텔레그램 명령어: /ticker, /status, /start")

  # 텔레그램 연결 테스트
  print(f"\n🤖 BNF 텔레그램 봇 연결 테스트 중...")
  if monitor.test_telegram_connection():
    print("✅ BNF 텔레그램 연결 성공")
    print("📱 사용 가능한 명령어:")
    print("   • /ticker AAPL - 개별 종목 BNF 분석")
    print("   • /status - BNF 모니터링 상태 확인")
    print("   • /start - BNF 도움말 보기")
  else:
    print("⚠️ BNF 텔레그램 연결 실패 - 로그만 출력")

  print(f"\n" + "=" * 80)
  print("🚀 BNF 자동 모니터링을 시작합니다!")
  print("   - 타카시 코테가와 스타일 역추세 전략")
  print("   - 과매수/과매도 반전 신호 전문")
  print("   - 2-3일 단기 보유 목표")
  print("   - RSI + Williams %R 이중 확인")
  print("   - 신호 발생시 텔레그램으로 즉시 알림")
  print("   - 텔레그램에서 /ticker 명령어로 개별 종목 분석 가능")
  print("   - 5회 스캔마다 상태 요약을 전송")
  print("   - 종료하려면 Ctrl+C를 누르세요")
  print("=" * 80)

  monitor.run_continuous_monitoring(scan_interval)


# ===================================================================================
# 메인 실행 함수
# ===================================================================================

def main():
  """BNF 메인 실행 함수"""
  parser = argparse.ArgumentParser(
      description='🚀 BNF 역추세 트레이딩 시스템 (타카시 코테가와 스타일)',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog="""
📖 사용 예시:
    python -m bnf --mode backtest         # BNF 백테스트만 실행
    python -m bnf --mode monitor          # BNF 실시간 모니터링 (대화형)
    python -m bnf --mode monitor-default  # BNF 백그라운드 모니터링
    python -m bnf --mode both             # 백테스트 후 모니터링 (기본값)

📱 BNF 텔레그램 설정 (통일된 환경변수):
    export US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN="your_bot_token"
    export US_BNF_STRATEGY_TELEGRAM_CHAT_ID="your_chat_id"

🎯 BNF 전략 개요 (타카시 코테가와 스타일):
    - 역추세 반전 신호 포착
    - 25일 이동평균 대비 20% 하락 시 매수
    - RSI + Williams %R 이중 확인
    - 2-3일 단기 보유 원칙
    - 거래량 증가 확인
    - 고확률 셋업만 선별

💡 BNF 철학:
    "대중과 반대로 행동하라. 대부분의 트레이더는 돈을 잃는다."
    - 바닥에서 매수, 천정에서 매도
    - 빠른 차익실현 (2-3일)
    - 감정 배제, 데이터 기반 결정
    - 25일 이동평균이 핵심 기준선

🔄 백그라운드 실행:
    # Linux/Mac
    nohup python -m bnf --mode monitor-default > /dev/null 2>&1 &
    
    # 프로세스 확인
    ps aux | grep 'bnf --mode'
    
    # 종료
    kill -TERM [PID]

📊 성과 기대치:
    - BNF 원본: 8년간 13,600달러 → 1억5천만달러
    - 연평균 수익률: 약 150%+ (전성기 기준)
    - 승률: 약 60% (BNF 스타일)
    - 보유기간: 평균 2-3일
        """
  )

  parser.add_argument(
      '--mode', '-m',
      choices=['backtest', 'monitor', 'monitor-default', 'both'],
      default='both',
      help='실행 모드 (기본값: both)'
  )

  args = parser.parse_args()

  print("🎯" + "=" * 78 + "🎯")
  print("     BNF 역추세 트레이딩 시스템 (타카시 코테가와 스타일)")
  print("🎯" + "=" * 78 + "🎯")
  print(f"⚙️ 실행 모드: {args.mode.upper()}")
  print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print(f"🐍 Python 버전: {sys.version.split()[0]}")
  print(f"🎯 전략: 타카시 코테가와(BNF) 역추세")
  print(f"📬 Telegram Commands: Use /ticker to analyze stocks")

  try:
    if args.mode in ['backtest', 'both']:
      run_bnf_backtest()

      if args.mode == 'both':
        print(f"\n" + "=" * 80)
        print("🎯 BNF 백테스트가 완료되었습니다!")
        print("📡 BNF 실시간 모니터링을 시작하려면 Enter를 누르세요...")
        print("🛑 종료하려면 Ctrl+C를 누르세요.")
        print("=" * 80)
        input()

    if args.mode in ['monitor', 'both']:
      run_bnf_monitor()

    elif args.mode == 'monitor-default':
      run_bnf_monitor_default()

  except KeyboardInterrupt:
    print(f"\n⏹️ 사용자에 의해 BNF 프로그램이 중단되었습니다.")

  except Exception as e:
    print(f"❌ 예상치 못한 BNF 오류가 발생했습니다: {e}")
    print(f"🔧 문제가 지속되면 GitHub Issues에 보고해주세요.")

  finally:
    print(f"\n🏁 BNF 프로그램을 종료합니다.")
    print(f"📅 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 BNF 스타일: \"대중과 반대로 행동하라\" - 타카시 코테가와")
    print(f"💖 Happy Counter-Trend Trading!")


if __name__ == "__main__":
  main()

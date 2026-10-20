# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A counter-trend (mean-reversion) trading system for the top 50 US stocks, modeled on Takashi Kotegawa (BNF). It has two parts: a yfinance-based backtester and a live monitor that sends Telegram alerts. It places no orders; it only produces signals and reports. User-facing text (console output, Telegram messages, reports, README) is in Korean.

## Commands

Run everything from the project root (the folder that contains `bnf/`).

```bash
pip install -r requirements.txt

python -m bnf --mode backtest         # interactive: asks for capital, strategy mode, stock count
python -m bnf --mode monitor          # interactive live monitor
python -m bnf --mode monitor-default  # non-interactive monitor (background/service use)
python -m bnf --mode both             # default: backtest, wait for Enter, then monitor

# Each module also runs on its own (must use -m because of relative imports)
python -m bnf.backtest
python -m bnf.monitor

# Background monitor / systemd service (the scripts cd to the project root themselves)
scripts/start_monitor.sh | stop_monitor.sh | status_monitor.sh | restart_monitor.sh | view_logs.sh
scripts/install_service.sh            # installs the bnf-monitor systemd unit
```

The Telegram environment variables are `US_BNF_STRATEGY_TELEGRAM_BOT_TOKEN` and `US_BNF_STRATEGY_TELEGRAM_CHAT_ID`. Without them the monitor still scans but sends no alerts.

There is no test suite, linter config or build step. To check a change, run a module directly or import a class in a REPL. For example, call `BNFCounterTrendBacktest(...).run_single_backtest("AAPL", start, end)`, or call `BNFCounterTrendMonitor().check_bnf_signals("AAPL")`. Both download live data from Yahoo Finance, so they need network access. `bnf.strategy.calculate_bnf_indicators` needs no network and can be checked on a synthetic OHLCV DataFrame.

## Architecture

- **`bnf/strategy.py`**: the single source of the trading rules, shared by the backtester and the monitor.
  - `TOP50_STOCKS`: the ticker → Korean name universe.
  - `BNFParams`: a frozen dataclass of indicator periods and thresholds. `BNFParams.for_mode()` returns the `conservative` / `balanced` / `aggressive` presets; the defaults are `balanced`.
  - `calculate_bnf_indicators(data, params)`: RSI(14), Williams %R(14), EMA 20/25, the volume ratio against a 20-day MA, and `MA25_Ratio` (close / EMA25). The buy signal is an **OR** of three conditions: RSI oversold + volume, Williams oversold + volume, or a deep discount to EMA25 + an up day + volume. The sell signal is RSI overbought, Williams overbought, or `MA25_Ratio >= 1.10`.
- **`bnf/__main__.py`**: an argparse CLI. It holds the interactive prompts (`input()`) for the backtest and monitor modes and sets up file logging for `monitor-default`.
- **`bnf/backtest.py`** → `BNFCounterTrendBacktest`. It stores its parameters as `self.params` (chosen by `strategy_mode`) and enforces a 3-day maximum hold. It runs per-stock backtests (`run_multi_stock_backtest`) and a shared-capital portfolio simulation (`run_bnf_portfolio_backtest`, up to 10 concurrent positions, ranked by lowest RSI). It writes CSVs, charts and a text report under `bnf_output_files/{results,charts,reports}/` in the project root (one level above the package). `setup_korean_font()` picks a matplotlib CJK font for each OS.
- **`bnf/monitor.py`** → `BNFCounterTrendMonitor`. It always uses the **balanced** preset. It runs three daemon threads:
  - a scan loop (`_auto_monitoring_loop`) that scans only during US market hours, with a holiday check in `_is_market_hours` / `_is_us_holiday`
  - a heartbeat thread
  - a python-telegram-bot polling thread with its own asyncio loop, serving `/start`, `/ticker <SYM>` and `/status`

  Positions (`self.positions`) and alert cooldowns (`self.last_alerts`, 1 hour) are kept only in memory and are lost on restart.

Change signal logic or thresholds only in `bnf/strategy.py`, so the backtest keeps matching what the live monitor does.

## Notes

- The README's strategy overview section is out of date. It describes an RSI **AND** Williams %R entry. Treat `bnf/strategy.py` as the source of truth.
- Logs: `--mode monitor-default` writes `bnf_output_files/logs/bnf_monitor_YYYYMMDD.log`, which the scripts read. In other modes the monitor's own `logging.basicConfig` takes effect and writes `bnf_trading_monitor.log` in the working directory.
- Python files use 2-space indentation.

#!/bin/bash
# status_monitor.sh

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "📊 BNF 모니터링 상태"
echo "========================"

# PID 파일 경로
PID_FILE="bnf_output_files/monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 모니터링이 실행되지 않고 있습니다."
    echo "🚀 시작하려면: scripts/start_monitor.sh"
    exit 1
fi

# PID 읽기
PID=$(cat "$PID_FILE")

# 프로세스 상태 확인
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ 모니터링이 정상 실행 중입니다."
    echo "📊 PID: $PID"

    # 실행 시간 계산
    START_TIME=$(ps -o lstart= -p "$PID" 2>/dev/null)
    if [ ! -z "$START_TIME" ]; then
        echo "⏰ 시작 시간: $START_TIME"
    fi

    # 메모리 사용량
    MEMORY=$(ps -o rss= -p "$PID" 2>/dev/null)
    if [ ! -z "$MEMORY" ]; then
        MEMORY_MB=$((MEMORY / 1024))
        echo "💾 메모리 사용량: ${MEMORY_MB}MB"
    fi

    # CPU 사용률
    CPU=$(ps -o %cpu= -p "$PID" 2>/dev/null)
    if [ ! -z "$CPU" ]; then
        echo "🖥️  CPU 사용률: ${CPU}%"
    fi

    echo ""
    echo "📂 로그 파일들:"
    if [ -d "bnf_output_files/logs" ]; then
        ls -la bnf_output_files/logs/ | grep "bnf_monitor"
    fi

    echo ""
    echo "📋 최근 로그 (마지막 5줄):"
    LOG_FILE="bnf_output_files/logs/bnf_monitor_$(date +%Y%m%d).log"
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE"
    else
        echo "   로그 파일을 찾을 수 없습니다."
    fi

else
    echo "❌ PID $PID 프로세스가 실행되지 않고 있습니다."
    rm -f "$PID_FILE"
    echo "🚀 시작하려면: scripts/start_monitor.sh"
fi

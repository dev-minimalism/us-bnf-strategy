#!/bin/bash
# view_logs.sh

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "📋 BNF 모니터링 로그 실시간 조회"
echo "=================================="

# 로그 파일 경로
LOG_FILE="bnf_output_files/logs/bnf_monitor_$(date +%Y%m%d).log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 오늘 날짜의 로그 파일을 찾을 수 없습니다: $LOG_FILE"
    echo "📂 사용 가능한 로그 파일들:"
    if [ -d "bnf_output_files/logs" ]; then
        ls -la bnf_output_files/logs/ | grep "bnf_monitor"
    else
        echo "   로그 디렉토리가 없습니다."
    fi
    exit 1
fi

echo "📊 로그 파일: $LOG_FILE"
echo "🔄 실시간 모니터링 중... (Ctrl+C로 종료)"
echo "=================================="

# 실시간 로그 조회
tail -f "$LOG_FILE"

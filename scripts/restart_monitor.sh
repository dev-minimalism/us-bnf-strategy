#!/bin/bash
# restart_monitor.sh

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "🔄 BNF 모니터링 재시작"
echo "=========================="

# 현재 실행 중인 모니터링 중지
echo "1️⃣ 기존 모니터링 중지 중..."
scripts/stop_monitor.sh

# 잠시 대기
echo "⏳ 2초 대기 중..."
sleep 2

# 새로 시작
echo "2️⃣ 모니터링 새로 시작 중..."
scripts/start_monitor.sh

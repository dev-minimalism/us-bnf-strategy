#!/bin/bash
# install_service.sh

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "🔧 systemd 서비스 설치"
echo "===================="

# 현재 디렉토리
CURRENT_DIR="$(pwd)"
mkdir -p "$CURRENT_DIR/bnf_output_files/logs"
USER_NAME="$(whoami)"

# 서비스 파일 생성
SERVICE_FILE="/tmp/bnf-monitor.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=BNF Counter-Trend Monitor
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 -m bnf --mode monitor-default
Restart=always
RestartSec=30
StandardOutput=append:$CURRENT_DIR/bnf_output_files/logs/service.log
StandardError=append:$CURRENT_DIR/bnf_output_files/logs/service_error.log

[Install]
WantedBy=multi-user.target
EOF

echo "📝 서비스 파일 생성됨: $SERVICE_FILE"
echo "🔐 sudo 권한이 필요합니다..."

# 서비스 설치
sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bnf-monitor.service

echo "✅ 서비스가 설치되었습니다!"
echo ""
echo "📖 사용법:"
echo "   sudo systemctl start bnf-monitor    # 서비스 시작"
echo "   sudo systemctl stop bnf-monitor     # 서비스 중지"
echo "   sudo systemctl status bnf-monitor   # 서비스 상태"
echo "   sudo systemctl restart bnf-monitor  # 서비스 재시작"
echo ""
echo "🚀 서비스 시작하려면: sudo systemctl start bnf-monitor"

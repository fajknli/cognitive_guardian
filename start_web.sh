#!/bin/bash
# 启动Web界面

cd ~/Project/Python/cognitive_guardian
source .venv/bin/activate
export PYTHONPATH=.

echo "=========================================="
echo "   认知姿态守护者 v3.1 - Web界面"
echo "=========================================="
echo ""
echo "启动中..."

python3 web_app.py

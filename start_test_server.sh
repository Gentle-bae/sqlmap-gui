#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║              SQL注入测试靶场 - 启动器                    ║"
echo "║                                                          ║"
echo "║                    作者: bae                             ║"
echo "║                    日期: 2026/2/28                       ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到python3，请确保Python已安装"
    exit 1
fi

# 检查Flask
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[信息] 正在安装Flask..."
    pip3 install flask
fi

echo "[信息] 正在启动测试靶场服务器..."
echo "[信息] 访问地址: http://127.0.0.1:5000"
echo "[信息] 按Ctrl+C停止服务器"
echo ""

python3 test_sqli_server.py

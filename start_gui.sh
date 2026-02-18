#!/bin/bash

echo "============================================"
echo "  SQLMap Pro GUI v2.0 - 启动器"
echo "============================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到python3，请确保Python已安装"
    exit 1
fi

echo "[信息] Python版本:"
python3 --version
echo ""

# 检查sqlmap.py
if [ ! -f "sqlmap.py" ]; then
    echo "[警告] 未找到sqlmap.py，请确保sqlmap已下载"
    echo "[提示] 可以从 https://github.com/sqlmapproject/sqlmap 下载"
    read -p "按Enter键继续..."
fi

echo "[信息] 正在启动 SQLMap Pro GUI v2.0..."
echo ""

# 启动GUI
python3 sqlmap_gui_modern.py

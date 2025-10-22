#!/bin/bash
# 安装 playwright-stealth 反检测库

echo "======================================"
echo "安装 playwright-stealth 反检测库"
echo "======================================"
echo ""

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

echo ""
echo "正在安装 playwright-stealth..."
pip3 install playwright-stealth

echo ""
echo "======================================"
echo "✓ 安装完成！"
echo "======================================"
echo ""
echo "现在可以使用增强的反检测功能了"
echo ""

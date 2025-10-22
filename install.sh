#!/bin/bash

# jable_downloader 一键安装脚本
# 适用于 macOS 和 Linux

set -e  # 遇到错误立即退出

echo "=================================="
echo "  Jable Downloader 安装脚本"
echo "=================================="
echo ""

# 检查 Python 版本
echo "[1/6] 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "    ✓ Python 版本: $PYTHON_VERSION"
echo ""

# 创建虚拟环境
echo "[2/6] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "    虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "    ✓ 虚拟环境创建成功"
fi
echo ""

# 激活虚拟环境
echo "[3/6] 激活虚拟环境..."
source venv/bin/activate
echo "    ✓ 虚拟环境已激活"
echo ""

# 升级 pip
echo "[4/6] 升级 pip..."
pip install --upgrade pip -q
echo "    ✓ pip 已升级到最新版本"
echo ""

# 安装依赖
echo "[5/6] 安装 Python 依赖..."
pip install -r requirements.txt -q
echo "    ✓ Python 依赖安装完成"
echo ""

# 安装 Playwright 浏览器
echo "[6/6] 安装 Playwright Chromium 浏览器..."
playwright install chromium
echo "    ✓ Chromium 浏览器安装完成"
echo ""

# 运行测试
echo "=================================="
echo "  运行测试验证安装"
echo "=================================="
echo ""

if python test_playwright.py; then
    echo ""
    echo "=================================="
    echo "  ✓ 安装成功！"
    echo "=================================="
    echo ""
    echo "使用方法:"
    echo "  1. 激活虚拟环境:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. 下载视频:"
    echo "     python main.py videos https://jable.tv/videos/xxxxx/"
    echo ""
    echo "  3. 查看帮助:"
    echo "     python main.py --help"
    echo ""
    echo "详细文档:"
    echo "  - 快速开始: cat QUICKSTART.md"
    echo "  - 迁移说明: cat PLAYWRIGHT_MIGRATION.md"
    echo ""
else
    echo ""
    echo "=================================="
    echo "  ✗ 测试失败"
    echo "=================================="
    echo ""
    echo "请运行以下命令进行调试:"
    echo "  python test_playwright_debug.py"
    echo ""
    exit 1
fi

#!/bin/bash
# 使用虚拟显示运行程序（有头模式）
#
# 用法:
#   ./run_with_display.sh python3 test_browser_simulation.py
#   ./run_with_display.sh python3 main.py subscription --sync-videos

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}虚拟显示启动器（有头模式）${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否提供了命令
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ 错误: 未提供命令${NC}"
    echo ""
    echo "用法:"
    echo "  $0 <command> [args...]"
    echo ""
    echo "示例:"
    echo "  $0 python3 test_browser_simulation.py"
    echo "  $0 python3 main.py subscription --sync-videos"
    echo ""
    exit 1
fi

# 检查 config.json 中的 playwright_headless 设置
if [ -f "config.json" ]; then
    HEADLESS=$(grep -o '"playwright_headless"[[:space:]]*:[[:space:]]*[a-z]*' config.json | grep -o '[a-z]*$' || echo "true")

    if [ "$HEADLESS" = "true" ]; then
        echo -e "${YELLOW}⚠️  注意: config.json 中 playwright_headless 设置为 true（无头模式）${NC}"
        echo -e "${YELLOW}   建议修改为 false 以使用有头模式${NC}"
        echo ""
        echo "是否继续？(y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo -e "${RED}已取消${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ playwright_headless = false (有头模式)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到 config.json${NC}"
fi

echo ""

# 检查 Xvfb 是否安装
if ! command -v xvfb-run &> /dev/null; then
    echo -e "${RED}❌ Xvfb 未安装${NC}"
    echo ""
    echo "Xvfb 用于在无图形界面的服务器上运行有头模式浏览器"
    echo ""
    echo "是否现在安装？(y/N)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}正在安装 Xvfb 和依赖...${NC}"

        sudo apt-get update
        sudo apt-get install -y \
            xvfb \
            libxkbcommon0 \
            libxdamage1 \
            libgbm1 \
            libpango-1.0-0 \
            libcairo2 \
            libatk1.0-0 \
            libatk-bridge2.0-0 \
            libcups2 \
            libdrm2 \
            libxcomposite1 \
            libxrandr2

        echo ""
        echo -e "${GREEN}✅ Xvfb 安装完成${NC}"
    else
        echo -e "${RED}已取消。请手动安装 Xvfb:${NC}"
        echo "  sudo apt-get install -y xvfb"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Xvfb 已安装${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}运行命令: $@${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 使用 Xvfb 运行命令
# -a: 自动选择显示编号
# --server-args: 设置虚拟显示参数
#   -screen 0 1920x1080x24: 1920x1080 分辨率，24位色深
xvfb-run -a --server-args="-screen 0 1920x1080x24" "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 命令执行成功${NC}"
else
    echo -e "${RED}❌ 命令执行失败 (退出码: $EXIT_CODE)${NC}"
fi

exit $EXIT_CODE

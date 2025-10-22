#!/bin/bash

# jable_downloader 一键安装脚本
# 适用于 macOS 和 Linux

echo "=================================="
echo "  Jable Downloader 安装脚本"
echo "=================================="
echo ""

# 获取实际用户（即使使用sudo也能获取）
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

if [ "$ACTUAL_USER" = "root" ]; then
    echo "⚠ 警告: 正在以 root 用户运行"
    echo ""
else
    echo "当前用户: $ACTUAL_USER"
    echo ""
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    OS=$(uname -s)
fi

echo "检测到操作系统: $OS"
echo ""

# 检查 Python 版本
echo "[1/7] 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "    ✗ 未找到 python3，请先安装 Python 3.6+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_VERSION_NUM=$(python3 -c 'import sys; print(sys.version_info[0] * 10 + sys.version_info[1])')

echo "    ✓ Python 版本: $PYTHON_VERSION"

# 检查 Python 版本是否 >= 3.6
if [ "$PYTHON_VERSION_NUM" -lt 36 ]; then
    echo "    ✗ Python 版本过低 (需要 3.6+，当前 $PYTHON_VERSION)"
    echo ""
    echo "请升级 Python 版本:"
    echo "  Ubuntu/Debian: sudo apt install python3.8"
    echo "  CentOS/RHEL: sudo yum install python38"
    echo ""
    exit 1
fi
echo ""

# 检查并安装系统依赖
echo "[2/7] 检查系统依赖..."
MISSING_DEPS=()

# 检查 python3-venv
if ! python3 -m venv --help &> /dev/null; then
    MISSING_DEPS+=("python3-venv")
fi

# 检查 pip
if ! python3 -m pip --version &> /dev/null; then
    MISSING_DEPS+=("python3-pip")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "    ⚠ 缺少以下系统依赖: ${MISSING_DEPS[*]}"
    echo ""

    # 根据操作系统安装依赖
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        echo "    正在安装依赖 (需要 sudo 权限)..."
        PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

        # 更新包列表
        if ! sudo apt-get update -qq; then
            echo "    ✗ 更新包列表失败"
            exit 1
        fi

        # 安装缺失的包
        for dep in "${MISSING_DEPS[@]}"; do
            if [[ "$dep" == "python3-venv" ]]; then
                PKG="python${PYTHON_VER}-venv"
                if ! apt-cache show "$PKG" &> /dev/null; then
                    PKG="python3-venv"
                fi
            elif [[ "$dep" == "python3-pip" ]]; then
                PKG="python${PYTHON_VER}-pip"
                if ! apt-cache show "$PKG" &> /dev/null; then
                    PKG="python3-pip"
                fi
            else
                PKG="$dep"
            fi

            echo "    安装 $PKG..."
            if ! sudo apt-get install -y -qq "$PKG"; then
                echo "    ✗ 安装 $PKG 失败"
                exit 1
            fi
        done

        echo "    ✓ 系统依赖安装完成"
    elif [[ "$OS" == "centos" || "$OS" == "rhel" || "$OS" == "fedora" ]]; then
        echo "    正在安装依赖 (需要 sudo 权限)..."
        PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')

        for dep in "${MISSING_DEPS[@]}"; do
            if [[ "$dep" == "python3-venv" ]]; then
                PKG="python${PYTHON_VER}-venv"
            elif [[ "$dep" == "python3-pip" ]]; then
                PKG="python${PYTHON_VER}-pip"
            else
                PKG="$dep"
            fi

            echo "    安装 $PKG..."
            if command -v dnf &> /dev/null; then
                sudo dnf install -y -q "$PKG"
            else
                sudo yum install -y -q "$PKG"
            fi
        done

        echo "    ✓ 系统依赖安装完成"
    elif [[ "$OS" == "Darwin" ]]; then
        echo "    macOS 系统通常已包含所需依赖"
        echo "    如果遇到问题，请运行: brew install python3"
    else
        echo "    ✗ 不支持的操作系统: $OS"
        echo ""
        echo "请手动安装以下依赖:"
        for dep in "${MISSING_DEPS[@]}"; do
            echo "    - $dep"
        done
        echo ""
        echo "例如 (Ubuntu/Debian):"
        echo "    sudo apt install python3-venv python3-pip"
        echo ""
        exit 1
    fi
else
    echo "    ✓ 系统依赖已满足"
fi
echo ""

# 创建虚拟环境
echo "[3/7] 创建虚拟环境..."
if [ -d "venv" ]; then
    # 检查虚拟环境所有者
    VENV_OWNER=$(stat -c '%U' venv 2>/dev/null || stat -f '%Su' venv 2>/dev/null)
    if [ "$VENV_OWNER" != "$ACTUAL_USER" ] && [ "$ACTUAL_USER" != "root" ]; then
        echo "    ⚠ 虚拟环境属于其他用户 ($VENV_OWNER)，需要重新创建"
        echo "    正在删除旧的虚拟环境..."
        rm -rf venv
    else
        echo "    虚拟环境已存在，跳过创建"
    fi
fi

if [ ! -d "venv" ]; then
    # 如果是通过 sudo 运行，以实际用户身份创建虚拟环境
    if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
        echo "    以用户 $SUDO_USER 身份创建虚拟环境..."
        if ! sudo -u "$SUDO_USER" python3 -m venv venv; then
            echo "    ✗ 虚拟环境创建失败"
            echo ""
            echo "请尝试不使用 sudo 运行安装脚本:"
            echo "    ./install.sh"
            echo ""
            exit 1
        fi
    else
        if ! python3 -m venv venv; then
            echo "    ✗ 虚拟环境创建失败"
            echo ""
            echo "请尝试手动创建:"
            echo "    python3 -m venv venv"
            echo ""
            exit 1
        fi
    fi
    echo "    ✓ 虚拟环境创建成功"
fi
echo ""

# 激活虚拟环境
echo "[4/7] 激活虚拟环境..."
source venv/bin/activate
echo "    ✓ 虚拟环境已激活"
echo ""

# 升级 pip
echo "[5/7] 升级 pip..."
pip install --upgrade pip -q
echo "    ✓ pip 已升级到最新版本"
echo ""

# 安装依赖
echo "[6/7] 安装 Python 依赖..."
echo "    这可能需要几分钟时间，请耐心等待..."
if ! pip install -r requirements.txt -q; then
    echo "    ✗ Python 依赖安装失败"
    echo ""
    echo "请尝试手动安装:"
    echo "    source venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo ""
    exit 1
fi
echo "    ✓ Python 依赖安装完成"
echo ""

# 安装 Playwright 浏览器
echo "[7/7] 安装 Playwright Chromium 浏览器..."
echo "    这可能需要下载约 100MB 数据，请耐心等待..."
if ! playwright install chromium; then
    echo "    ✗ Chromium 浏览器安装失败"
    echo ""
    echo "请尝试手动安装:"
    echo "    source venv/bin/activate"
    echo "    playwright install chromium"
    echo ""
    exit 1
fi

# 可选：安装浏览器系统依赖（Linux）
if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
    echo "    正在安装浏览器系统依赖..."
    if ! playwright install-deps chromium 2>/dev/null; then
        echo "    ⚠ 浏览器系统依赖安装失败（可以忽略）"
    fi
fi

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

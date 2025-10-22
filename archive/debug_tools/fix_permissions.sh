#!/bin/bash

# 修复虚拟环境权限问题
# 当使用 sudo 运行安装脚本后，虚拟环境属于 root，普通用户无法使用

echo "=================================="
echo "  修复虚拟环境权限"
echo "=================================="
echo ""

CURRENT_USER="${SUDO_USER:-$USER}"

if [ "$CURRENT_USER" = "root" ]; then
    echo "⚠ 警告: 请使用 sudo 运行此脚本"
    echo ""
    echo "用法:"
    echo "  sudo ./fix_permissions.sh"
    echo ""
    exit 1
fi

echo "当前用户: $CURRENT_USER"
echo ""

# 检查 venv 目录是否存在
if [ ! -d "venv" ]; then
    echo "✗ venv 目录不存在"
    echo ""
    echo "请先运行安装脚本:"
    echo "  sudo ./install.sh"
    echo ""
    exit 1
fi

# 获取 venv 所有者
VENV_OWNER=$(stat -c '%U' venv 2>/dev/null || stat -f '%Su' venv 2>/dev/null)

echo "虚拟环境所有者: $VENV_OWNER"
echo "需要更改为: $CURRENT_USER"
echo ""

if [ "$VENV_OWNER" = "$CURRENT_USER" ]; then
    echo "✓ 权限已正确，无需修复"
    echo ""
    echo "可以直接使用:"
    echo "  source venv/bin/activate"
    echo ""
    exit 0
fi

# 修复权限
echo "正在修复权限..."
if chown -R "$CURRENT_USER:$CURRENT_USER" venv/; then
    echo "✓ 权限修复完成"
    echo ""
    echo "现在可以使用:"
    echo "  source venv/bin/activate"
    echo "  python main.py --help"
    echo ""
else
    echo "✗ 权限修复失败"
    echo ""
    echo "请尝试手动修复:"
    echo "  sudo chown -R $CURRENT_USER:$CURRENT_USER venv/"
    echo ""
    exit 1
fi

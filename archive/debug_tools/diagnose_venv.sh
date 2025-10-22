#!/bin/bash

# 虚拟环境诊断脚本

echo "=================================="
echo "  虚拟环境诊断工具"
echo "=================================="
echo ""

echo "=== 系统信息 ==="
echo "操作系统: $(uname -a)"
echo "当前用户: $USER"
echo "当前目录: $(pwd)"
echo ""

echo "=== Python 信息 ==="
echo "python 位置: $(which python 2>/dev/null || echo '未找到')"
echo "python 版本: $(python --version 2>&1 || echo '未找到')"
echo ""
echo "python3 位置: $(which python3)"
echo "python3 版本: $(python3 --version)"
echo ""

echo "=== Python 模块检查 ==="
echo -n "venv 模块: "
if python3 -m venv --help >/dev/null 2>&1; then
    echo "✓ 已安装"
else
    echo "✗ 未安装"
fi

echo -n "pip 模块: "
if python3 -m pip --version >/dev/null 2>&1; then
    echo "✓ 已安装"
else
    echo "✗ 未安装"
fi
echo ""

echo "=== 检查现有 venv 目录 ==="
if [ -d "venv" ]; then
    echo "venv 目录存在"
    echo ""
    echo "目录权限:"
    ls -ld venv
    echo ""
    echo "目录内容:"
    ls -la venv/
    echo ""
    if [ -d "venv/bin" ]; then
        echo "bin 目录内容:"
        ls -la venv/bin/
        echo ""

        echo "关键文件检查:"
        for file in activate python python3 pip pip3; do
            if [ -f "venv/bin/$file" ]; then
                echo "  ✓ $file 存在"
            else
                echo "  ✗ $file 不存在"
            fi
        done
    else
        echo "✗ bin 目录不存在"
    fi
else
    echo "venv 目录不存在"
fi
echo ""

echo "=== 尝试创建测试虚拟环境 ==="
TEST_VENV="venv_test_$$"
echo "创建测试环境: $TEST_VENV"

if python3 -m venv "$TEST_VENV" 2>&1; then
    echo "✓ 创建成功"
    echo ""
    echo "测试环境内容:"
    ls -la "$TEST_VENV/bin/" 2>/dev/null || echo "bin 目录为空"
    echo ""

    if [ -f "$TEST_VENV/bin/activate" ]; then
        echo "✓ activate 文件已创建"
    else
        echo "✗ activate 文件未创建"
        echo ""
        echo "这表明 python3-venv 安装不完整"
        echo "请尝试重新安装:"
        echo "  sudo apt-get install --reinstall python3-venv python3.8-venv"
    fi

    # 清理测试环境
    rm -rf "$TEST_VENV"
else
    echo "✗ 创建失败"
    echo ""
    echo "请检查 python3-venv 是否正确安装:"
    echo "  dpkg -l | grep python3-venv"
fi
echo ""

echo "=== dpkg 包信息 ==="
dpkg -l | grep -E "python3.*venv"
echo ""

echo "=== 建议 ==="
echo "如果 activate 文件不存在，可能的原因："
echo "1. python3-venv 包安装不完整"
echo "2. 磁盘空间不足"
echo "3. 文件系统权限问题"
echo ""
echo "建议操作："
echo "1. 重新安装 venv:"
echo "   sudo apt-get install --reinstall python3.8-venv"
echo ""
echo "2. 删除并重建虚拟环境:"
echo "   rm -rf venv/"
echo "   python3 -m venv venv"
echo ""
echo "3. 检查磁盘空间:"
echo "   df -h ."
echo ""

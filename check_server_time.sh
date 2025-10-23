#!/bin/bash
# 检查服务器时间是否准确

echo "========================================"
echo "检查服务器时间"
echo "========================================"
echo ""

# 显示当前系统时间
echo "当前系统时间:"
date
echo ""

# 显示当前时区
echo "当前时区:"
timedatectl 2>/dev/null || echo "时区: $(date +%Z)"
echo ""

# 检查 NTP 同步状态
echo "检查 NTP 同步状态:"
if command -v timedatectl &> /dev/null; then
    timedatectl status | grep -i "ntp\|synchronized"
elif command -v ntpstat &> /dev/null; then
    ntpstat
else
    echo "未安装 NTP 工具"
fi
echo ""

# 从网络获取准确时间
echo "从网络获取准确时间:"
if command -v curl &> /dev/null; then
    echo "  方法 1: 从 HTTP 响应获取"
    NETWORK_TIME=$(curl -sI https://www.google.com 2>/dev/null | grep -i "^date:" | sed 's/date: //i')
    if [ ! -z "$NETWORK_TIME" ]; then
        echo "  网络时间: $NETWORK_TIME"
    else
        echo "  ✗ 获取失败"
    fi
fi
echo ""

# 比较时间差异
echo "========================================"
echo "建议的操作:"
echo "========================================"
echo ""
echo "如果时间不准确，请执行以下命令同步时间:"
echo ""
echo "1. 安装 NTP（如果未安装）:"
echo "   Ubuntu/Debian:"
echo "     sudo apt-get update"
echo "     sudo apt-get install -y ntp ntpdate"
echo ""
echo "   CentOS/RHEL:"
echo "     sudo yum install -y ntp ntpdate"
echo ""
echo "2. 同步时间:"
echo "   sudo ntpdate -u time.nist.gov"
echo "   或"
echo "   sudo ntpdate -u pool.ntp.org"
echo ""
echo "3. 启用自动同步:"
echo "   sudo systemctl enable ntp"
echo "   sudo systemctl start ntp"
echo ""
echo "4. 验证:"
echo "   date"
echo ""

#!/bin/bash

# ============================================================================
# Cron 任务快速配置脚本
# 帮助用户快速设置每日自动分析任务
# ============================================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="$PROJECT_DIR/daily_analysis.sh"

echo "=========================================="
echo "📅 每日自动分析任务配置"
echo "=========================================="
echo ""

# 检查脚本是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ 错误：找不到 daily_analysis.sh 脚本"
    exit 1
fi

# 检查脚本是否可执行
if [ ! -x "$SCRIPT_PATH" ]; then
    echo "⚠️  脚本不可执行，正在设置权限..."
    chmod +x "$SCRIPT_PATH"
    echo "✓ 权限设置完成"
fi

echo "项目路径: $PROJECT_DIR"
echo "脚本路径: $SCRIPT_PATH"
echo ""

# ============================================================================
# 询问执行时间
# ============================================================================
echo "请选择每天执行的时间："
echo "  1) 凌晨 02:00（推荐）"
echo "  2) 凌晨 03:00"
echo "  3) 早上 08:00"
echo "  4) 晚上 23:00"
echo "  5) 自定义时间"
echo ""
read -p "请输入选项 [1-5]: " choice

case $choice in
    1)
        CRON_TIME="0 2 * * *"
        TIME_DESC="每天凌晨 02:00"
        ;;
    2)
        CRON_TIME="0 3 * * *"
        TIME_DESC="每天凌晨 03:00"
        ;;
    3)
        CRON_TIME="0 8 * * *"
        TIME_DESC="每天早上 08:00"
        ;;
    4)
        CRON_TIME="0 23 * * *"
        TIME_DESC="每天晚上 23:00"
        ;;
    5)
        read -p "请输入小时 (0-23): " hour
        read -p "请输入分钟 (0-59): " minute
        CRON_TIME="$minute $hour * * *"
        TIME_DESC="每天 $(printf "%02d:%02d" $hour $minute)"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "✓ 已选择: $TIME_DESC"
echo ""

# ============================================================================
# 生成 cron 任务
# ============================================================================
CRON_JOB="$CRON_TIME $SCRIPT_PATH"

echo "将要添加的 cron 任务："
echo "----------------------------------------"
echo "$CRON_JOB"
echo "----------------------------------------"
echo ""

# ============================================================================
# 确认添加
# ============================================================================
read -p "是否添加此任务到 crontab? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 已取消"
    exit 0
fi

# ============================================================================
# 添加到 crontab
# ============================================================================
echo ""
echo "正在添加 cron 任务..."

# 获取当前 crontab
CURRENT_CRON=$(crontab -l 2>/dev/null)

# 检查是否已存在相同任务
if echo "$CURRENT_CRON" | grep -q "$SCRIPT_PATH"; then
    echo "⚠️  检测到已存在相同任务："
    echo "$CURRENT_CRON" | grep "$SCRIPT_PATH"
    echo ""
    read -p "是否替换现有任务? (y/n): " replace

    if [ "$replace" = "y" ] || [ "$replace" = "Y" ]; then
        # 删除旧任务
        echo "$CURRENT_CRON" | grep -v "$SCRIPT_PATH" | crontab -
        echo "✓ 已删除旧任务"
    else
        echo "❌ 已取消"
        exit 0
    fi
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Cron 任务添加成功！"
    echo "=========================================="
    echo ""
    echo "任务详情："
    echo "  执行时间: $TIME_DESC"
    echo "  脚本路径: $SCRIPT_PATH"
    echo "  日志目录: $PROJECT_DIR/logs/"
    echo ""
    echo "查看当前所有任务:"
    echo "  crontab -l"
    echo ""
    echo "查看执行日志:"
    echo "  tail -f $PROJECT_DIR/logs/daily_analysis_\$(date +%Y%m%d).log"
    echo ""
    echo "手动测试执行:"
    echo "  $SCRIPT_PATH"
    echo ""
else
    echo "❌ 添加失败，请检查 crontab 权限"
    exit 1
fi

# ============================================================================
# macOS 特殊提醒
# ============================================================================
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "⚠️  macOS 特别提醒："
    echo "----------------------------------------"
    echo "需要给 cron 授予完全磁盘访问权限："
    echo ""
    echo "1. 打开 系统偏好设置 → 安全性与隐私 → 隐私"
    echo "2. 选择 完全磁盘访问权限"
    echo "3. 点击 + 添加 /usr/sbin/cron"
    echo "4. 重启 cron 服务："
    echo "   sudo launchctl stop com.vix.cron"
    echo "   sudo launchctl start com.vix.cron"
    echo ""
fi

echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="

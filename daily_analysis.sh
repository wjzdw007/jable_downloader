#!/bin/bash

# ============================================================================
# 每日热门视频分析自动执行脚本
# 功能：1. 更新热门视频数据  2. 生成增长报告  3. 推送到 Telegram
# ============================================================================

# 项目路径（自动检测脚本所在目录）
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
fi

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 日志文件（按日期命名）
LOG_FILE="$PROJECT_DIR/logs/daily_analysis_$(date +%Y%m%d).log"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 开始计时
START_TIME=$(date +%s)

# ============================================================================
# 1. 每日更新热门视频数据
# ============================================================================
echo "" >> "$LOG_FILE"
echo "【步骤1】更新热门视频数据" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"

python3 main.py analyze update --db analytics.db 2>&1 | tee -a "$LOG_FILE"
UPDATE_STATUS=$?

if [ $UPDATE_STATUS -eq 0 ]; then
    echo "✓ 数据更新成功" >> "$LOG_FILE"
else
    echo "✗ 数据更新失败（退出码：$UPDATE_STATUS）" >> "$LOG_FILE"

    # 发送失败通知到 Telegram
    python3 -c "
from telegram_notifier import send_message
send_message('⚠️ 每日分析任务失败！\\n数据更新错误，请检查日志。')
    " 2>/dev/null || echo "⚠️ 无法发送 Telegram 通知" >> "$LOG_FILE"

    # 退出
    exit $UPDATE_STATUS
fi

# ============================================================================
# 2. 生成并发送报告
# ============================================================================
echo "" >> "$LOG_FILE"
echo "【步骤2】生成并发送报告" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"

python3 main.py report --send --top 50 2>&1 | tee -a "$LOG_FILE"
REPORT_STATUS=$?

if [ $REPORT_STATUS -eq 0 ]; then
    echo "✓ 报告发送成功" >> "$LOG_FILE"
else
    echo "✗ 报告发送失败（退出码：$REPORT_STATUS）" >> "$LOG_FILE"
fi

# ============================================================================
# 记录执行信息
# ============================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "执行耗时: ${DURATION}秒 ($(($DURATION / 60))分钟)" >> "$LOG_FILE"
echo "数据更新: $([ $UPDATE_STATUS -eq 0 ] && echo '成功 ✓' || echo '失败 ✗')" >> "$LOG_FILE"
echo "报告发送: $([ $REPORT_STATUS -eq 0 ] && echo '成功 ✓' || echo '失败 ✗')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# ============================================================================
# 保存执行状态（JSON 格式）
# ============================================================================
cat > "$PROJECT_DIR/last_run_status.json" <<EOF
{
  "last_run": "$(date -Iseconds)",
  "duration_seconds": $DURATION,
  "update_status": $UPDATE_STATUS,
  "report_status": $REPORT_STATUS,
  "success": $([ $UPDATE_STATUS -eq 0 ] && [ $REPORT_STATUS -eq 0 ] && echo "true" || echo "false")
}
EOF

# ============================================================================
# 清理旧日志（保留最近30天）
# ============================================================================
find "$PROJECT_DIR/logs" -name "daily_analysis_*.log" -mtime +30 -delete 2>/dev/null

# 退出虚拟环境
deactivate 2>/dev/null || true

# 返回状态（如果数据更新失败，返回失败状态）
exit $UPDATE_STATUS

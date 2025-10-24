# 📅 每日自动分析配置指南

## 🎯 目标

每天自动执行：
1. 爬取热门视频数据（更新）
2. 生成增长报告
3. 推送到 Telegram

---

## 📋 配置步骤

### 1️⃣ 创建自动执行脚本

创建 `daily_analysis.sh` 脚本：

```bash
#!/bin/bash

# 项目路径（请修改为你的实际路径）
PROJECT_DIR="/Users/daweizheng/Desktop/ai/jable_downloader"
cd "$PROJECT_DIR" || exit 1

# 激活虚拟环境（如果使用）
source venv/bin/activate 2>/dev/null || true

# 日志文件
LOG_FILE="$PROJECT_DIR/logs/daily_analysis_$(date +%Y%m%d).log"
mkdir -p "$PROJECT_DIR/logs"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. 每日更新热门视频数据
echo "1. 更新热门视频数据..." >> "$LOG_FILE"
python3 main.py analyze update --db analytics.db 2>&1 | tee -a "$LOG_FILE"
UPDATE_STATUS=$?

if [ $UPDATE_STATUS -eq 0 ]; then
    echo "✓ 数据更新成功" >> "$LOG_FILE"

    # 2. 生成并发送报告
    echo "2. 生成并发送报告..." >> "$LOG_FILE"
    python3 main.py report --send --top 50 2>&1 | tee -a "$LOG_FILE"
    REPORT_STATUS=$?

    if [ $REPORT_STATUS -eq 0 ]; then
        echo "✓ 报告发送成功" >> "$LOG_FILE"
    else
        echo "✗ 报告发送失败" >> "$LOG_FILE"
    fi
else
    echo "✗ 数据更新失败，跳过报告生成" >> "$LOG_FILE"
fi

# 记录结束时间
echo "========================================" >> "$LOG_FILE"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 清理旧日志（保留最近30天）
find "$PROJECT_DIR/logs" -name "daily_analysis_*.log" -mtime +30 -delete

# 退出虚拟环境
deactivate 2>/dev/null || true
```

---

### 2️⃣ 设置脚本权限

```bash
chmod +x daily_analysis.sh
```

---

### 3️⃣ 配置 Cron 任务

#### 方法1：使用 crontab（推荐）

编辑 cron 任务：
```bash
crontab -e
```

添加以下行（每天凌晨2点执行）：
```bash
# 每天凌晨2点执行热门视频分析
0 2 * * * /Users/daweizheng/Desktop/ai/jable_downloader/daily_analysis.sh

# 或者指定完整路径和Python解释器
0 2 * * * cd /Users/daweizheng/Desktop/ai/jable_downloader && /usr/bin/python3 main.py analyze update && /usr/bin/python3 main.py report --send
```

**Cron 时间格式说明**：
```
分 时 日 月 周
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0和7都是周日)
│ │ │ └────── 月份 (1-12)
│ │ └──────── 日期 (1-31)
│ └────────── 小时 (0-23)
└──────────── 分钟 (0-59)
```

**常用时间示例**：
```bash
# 每天凌晨2点
0 2 * * *

# 每天早上8点
0 8 * * *

# 每天晚上23点
0 23 * * *

# 每天凌晨3点30分
30 3 * * *

# 每周一凌晨2点
0 2 * * 1

# 每月1号凌晨2点
0 2 1 * *
```

---

### 4️⃣ 查看和管理 Cron 任务

**查看当前任务**：
```bash
crontab -l
```

**删除所有任务**：
```bash
crontab -r
```

**编辑任务**：
```bash
crontab -e
```

---

### 5️⃣ macOS 特殊配置

macOS 需要给 cron 授予完全磁盘访问权限：

1. 打开 **系统偏好设置** → **安全性与隐私** → **隐私**
2. 选择 **完全磁盘访问权限**
3. 点击 **+** 添加 `/usr/sbin/cron`
4. 重启 cron 服务：
   ```bash
   sudo launchctl stop com.vix.cron
   sudo launchctl start com.vix.cron
   ```

---

## 🧪 测试自动任务

### 方法1：手动执行脚本
```bash
cd /Users/daweizheng/Desktop/ai/jable_downloader
./daily_analysis.sh
```

### 方法2：设置测试 cron（5分钟后执行）
```bash
# 假设现在是 14:25，设置 14:30 执行
30 14 * * * /Users/daweizheng/Desktop/ai/jable_downloader/daily_analysis.sh
```

### 方法3：查看执行日志
```bash
# 查看今天的日志
tail -f logs/daily_analysis_$(date +%Y%m%d).log

# 查看所有日志
ls -lh logs/
```

---

## 📊 查看执行历史

### 方法1：查看日志文件
```bash
# 查看最近的日志
ls -lt logs/ | head -10

# 查看某天的日志
cat logs/daily_analysis_20251025.log
```

### 方法2：查看 cron 执行记录（macOS）
```bash
# 查看系统日志
log show --predicate 'process == "cron"' --last 1d

# 或者
grep CRON /var/log/system.log
```

### 方法3：邮件通知（可选）
```bash
# 在 crontab 中添加邮箱变量
MAILTO=your_email@example.com

0 2 * * * /Users/daweizheng/Desktop/ai/jable_downloader/daily_analysis.sh
```

---

## 🔧 进阶配置

### 1. 错误监控和告警

修改 `daily_analysis.sh`，添加错误通知：

```bash
# 如果失败，发送 Telegram 告警
if [ $UPDATE_STATUS -ne 0 ]; then
    # 使用你的 Telegram Bot 发送告警
    python3 -c "
from telegram_notifier import send_message
send_message('⚠️ 每日分析任务失败！请检查日志。')
    "
fi
```

### 2. 执行状态记录

创建 `status.json` 记录每次执行：

```bash
# 在脚本末尾添加
echo "{\"last_run\": \"$(date -Iseconds)\", \"status\": $UPDATE_STATUS}" > status.json
```

### 3. 性能监控

记录执行时间：

```bash
START_TIME=$(date +%s)
# ... 执行任务 ...
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "执行耗时: ${DURATION}秒" >> "$LOG_FILE"
```

---

## ⚠️ 常见问题

### 1. Cron 任务没有执行

**检查 cron 服务是否运行**：
```bash
# macOS
sudo launchctl list | grep cron

# Linux
sudo systemctl status cron
```

**检查路径是否正确**：
```bash
# 在 cron 中使用绝对路径
/usr/bin/python3 /Users/daweizheng/Desktop/ai/jable_downloader/main.py
```

### 2. 环境变量问题

Cron 运行时环境变量较少，在脚本开头添加：

```bash
#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin
export PYTHONPATH=/Users/daweizheng/Desktop/ai/jable_downloader
```

### 3. 虚拟环境未激活

确保脚本中正确激活：
```bash
source /Users/daweizheng/Desktop/ai/jable_downloader/venv/bin/activate
```

### 4. 日志查看

如果任务执行但无输出，检查：
```bash
# 确保日志目录存在
mkdir -p logs

# 确保有写权限
chmod 755 logs
```

### 5. 初次执行

**首次使用需要先运行初始化**：
```bash
# 手动执行一次初始化（爬取所有1424页）
python main.py analyze init --db analytics.db

# 之后每天自动执行更新即可
```

---

## 📝 推荐配置方案

### 方案A：简单方案（直接用 cron）
```bash
# crontab -e
0 2 * * * cd /Users/daweizheng/Desktop/ai/jable_downloader && python3 main.py analyze update && python3 main.py report --send >> logs/daily.log 2>&1
```

### 方案B：完整方案（使用脚本）
```bash
# crontab -e
0 2 * * * /Users/daweizheng/Desktop/ai/jable_downloader/daily_analysis.sh
```

### 方案C：分步执行
```bash
# 凌晨2点：更新数据
0 2 * * * cd /Users/daweizheng/Desktop/ai/jable_downloader && python3 main.py analyze update

# 凌晨3点：生成报告（确保数据更新完成）
0 3 * * * cd /Users/daweizheng/Desktop/ai/jable_downloader && python3 main.py report --send
```

---

## ✅ 验证配置成功

1. ✅ cron 任务已添加：`crontab -l`
2. ✅ 脚本可执行：`ls -l daily_analysis.sh`
3. ✅ 手动测试通过：`./daily_analysis.sh`
4. ✅ 日志正常生成：`ls logs/`
5. ✅ Telegram 能收到消息

---

**下一步**：
1. 创建 `daily_analysis.sh` 脚本
2. 设置 cron 任务
3. 等待明天凌晨2点自动执行
4. 检查日志和 Telegram 消息

---

**生成时间**: 2025-10-25
**适用系统**: macOS / Linux

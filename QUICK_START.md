# 🚀 快速开始指南

## 📋 每日自动分析配置（3步完成）

### 第1步：首次初始化（必须）

```bash
# 爬取所有1424页热门视频数据（只需执行一次）
python main.py analyze init --db analytics.db
```

**预计耗时**: 25-30分钟（已优化）

**这一步做什么**:
- 爬取所有热门页面的视频数据
- 提取排名前200的视频的演员信息
- 保存到数据库 `analytics.db`

---

### 第2步：配置自动任务（推荐方式）

```bash
# 运行交互式配置脚本
./setup_cron.sh
```

**按提示操作**:
1. 选择执行时间（推荐：凌晨2点）
2. 确认添加任务
3. 完成！

---

### 第3步：验证配置

```bash
# 查看 cron 任务
crontab -l

# 手动测试执行
./daily_analysis.sh

# 查看执行日志
tail -f logs/daily_analysis_$(date +%Y%m%d).log
```

---

## 🎯 手动配置方式（可选）

如果你更喜欢手动配置，使用以下命令：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨2点执行）
0 2 * * * /Users/daweizheng/Desktop/ai/jable_downloader/daily_analysis.sh
```

---

## 📊 每日自动流程

配置完成后，系统将每天自动执行：

1. **更新数据** - 爬取最新的热门视频数据
2. **生成报告** - 计算点赞数增长前50的视频和演员
3. **推送 Telegram** - 发送增长报告到你的 Telegram

---

## 🔍 查看执行结果

### 方法1：查看日志
```bash
# 查看今天的日志
cat logs/daily_analysis_$(date +%Y%m%d).log

# 实时监控
tail -f logs/daily_analysis_*.log
```

### 方法2：查看状态文件
```bash
# 查看上次执行状态
cat last_run_status.json
```

### 方法3：Telegram 消息
每天会自动收到报告，包含：
- 点赞增长前50的视频
- 点赞增长前50的演员

---

## 🛠️ 常用命令

### 查看数据库
```bash
# 手动生成报告（今天 vs 昨天）
python main.py report --top 50

# 发送报告到 Telegram
python main.py report --send --top 50

# 指定日期生成报告
python main.py report --date 2025-10-25 --top 50
```

### 手动更新数据
```bash
# 每日更新（只爬必要的页面）
python main.py analyze update

# 完整初始化（爬所有1424页）
python main.py analyze init
```

### 查看 Cron 任务
```bash
# 列出所有任务
crontab -l

# 编辑任务
crontab -e

# 删除所有任务
crontab -r
```

---

## ⚠️ macOS 用户特别提醒

macOS 需要给 cron 授予权限：

1. 打开 **系统偏好设置** → **安全性与隐私** → **隐私**
2. 选择 **完全磁盘访问权限**
3. 点击 **+** 添加 `/usr/sbin/cron`
4. 重启 cron 服务：
   ```bash
   sudo launchctl stop com.vix.cron
   sudo launchctl start com.vix.cron
   ```

---

## 📝 配置文件说明

| 文件 | 说明 |
|------|------|
| `analytics.db` | 数据库文件（存储所有数据） |
| `progress.json` | 爬取进度（支持断点续传） |
| `last_run_status.json` | 最近一次执行状态 |
| `logs/` | 日志目录 |

---

## 🐛 故障排查

### 问题1: Cron 任务没执行

**检查**:
```bash
# 查看 cron 是否运行
ps aux | grep cron

# 查看任务列表
crontab -l
```

### 问题2: 日志没生成

**检查**:
```bash
# 确保日志目录存在
mkdir -p logs

# 检查脚本权限
ls -l daily_analysis.sh
```

### 问题3: Telegram 没收到消息

**检查**:
```bash
# 测试 Telegram 配置
python -c "from telegram_notifier import send_message; send_message('测试消息')"

# 检查 .env 配置
cat .env | grep TELEGRAM
```

---

## 📚 更多文档

- **详细配置**: 查看 `CRON_SETUP.md`
- **性能优化**: 查看 `OPTIMIZATION_SUMMARY.md`
- **优化方案**: 查看 `OPTIMIZATION_IDEAS.md`

---

## ✅ 快速检查清单

- [ ] 已执行首次初始化（`python main.py analyze init`）
- [ ] 已配置 cron 任务（`./setup_cron.sh` 或手动配置）
- [ ] 已验证任务添加成功（`crontab -l`）
- [ ] macOS 用户已授予 cron 权限
- [ ] Telegram 配置正确（`.env` 文件）
- [ ] 已手动测试执行（`./daily_analysis.sh`）

---

**下一步**: 等待明天凌晨2点，检查是否收到 Telegram 报告！🎉

---

**创建时间**: 2025-10-25

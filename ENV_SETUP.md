# 环境变量设置快速指南

## 🎯 为什么使用 .env 文件？

✅ **安全**：敏感信息不会被提交到 Git
✅ **方便**：修改配置不需要改代码
✅ **清晰**：配置和代码分离

## 📝 快速开始（3 步）

### 1. 复制示例文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

```bash
nano .env  # 或使用你喜欢的编辑器
```

填入你的配置：
```bash
# Telegram 通知配置
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # 从 @BotFather 获取
TELEGRAM_CHAT_ID=123456789  # 从 @userinfobot 获取
```

### 3. 运行程序

**方法 A：使用加载脚本（推荐）**
```bash
source load_env.sh && python3 main.py
```

**方法 B：手动加载**
```bash
export $(grep -v '^#' .env | xargs)
python3 main.py
```

**方法 C：直接运行（程序会自动读取）**
```bash
python3 main.py
```
*注意：Python 代码已经支持直接从 os.environ 读取，不需要额外加载*

## 🔧 详细步骤

### 获取 Telegram Bot Token

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示设置 bot 名称和用户名
4. 复制获得的 token 到 `.env` 文件

### 获取 Chat ID

1. 在 Telegram 搜索 `@userinfobot`
2. 点击 Start
3. 复制显示的 ID 到 `.env` 文件

## 📋 配置选项

`.env` 文件支持的配置：

```bash
# Telegram 通知（必填，如果要使用通知功能）
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 其他配置（可选）
# SCRAPINGANT_TOKEN=your_token
```

## 🔒 安全检查

在使用前，确认：

```bash
# 1. 检查 .env 是否在 .gitignore 中
cat .gitignore | grep .env

# 2. 确认 .env 不会被 Git 追踪
git status | grep .env
# 应该看不到 .env 文件

# 3. 测试配置
python3 telegram_notifier.py
```

## ❓ 常见问题

### Q: .env 文件会被提交到 Git 吗？

A: 不会，`.env` 已经在 `.gitignore` 中，Git 会忽略它。

### Q: 可以不用 .env 文件吗？

A: 可以，程序支持三种配置方式（优先级从高到低）：
1. 环境变量（手动 export）
2. .env 文件
3. config.json

### Q: 如何在服务器上使用？

A:
```bash
# 方法 1：创建 .env 文件
vim .env

# 方法 2：在系统环境变量中设置
echo 'export TELEGRAM_BOT_TOKEN="xxx"' >> ~/.bashrc
source ~/.bashrc

# 方法 3：使用 systemd 服务（推荐生产环境）
```

### Q: Windows 上如何使用？

A: Windows 不支持 .env 文件自动加载，建议：

**方法 1：使用系统环境变量**
```cmd
# CMD
setx TELEGRAM_BOT_TOKEN "your_token"
setx TELEGRAM_CHAT_ID "your_chat_id"

# PowerShell
$env:TELEGRAM_BOT_TOKEN="your_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"
```

**方法 2：使用 python-dotenv**
```bash
pip install python-dotenv
# 程序会自动加载 .env 文件
```

### Q: 如何验证配置是否生效？

A:
```bash
# 方法 1：查看环境变量
echo $TELEGRAM_BOT_TOKEN

# 方法 2：运行测试脚本
python3 telegram_notifier.py
```

## 🚀 生产环境部署

### 使用 Systemd

创建服务文件 `/etc/systemd/system/jable-downloader.service`：

```ini
[Unit]
Description=Jable Downloader
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/jable_downloader
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="TELEGRAM_CHAT_ID=your_chat_id"
ExecStart=/usr/bin/python3 /path/to/jable_downloader/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable jable-downloader
sudo systemctl start jable-downloader
```

### 使用 Docker

在 `docker-compose.yml` 中：

```yaml
version: '3'
services:
  jable-downloader:
    image: jable-downloader
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    env_file:
      - .env
```

## 📚 相关文档

- [SECURITY.md](SECURITY.md) - 完整的安全指南
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Telegram Bot 设置指南
- [README.md](README.md) - 项目总览

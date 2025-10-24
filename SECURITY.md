# 安全配置指南

## ⚠️ 重要提醒

**永远不要将敏感信息提交到 Git 仓库！**

本项目包含以下敏感信息需要保护：
- Telegram Bot Token
- Telegram Chat ID
- ScrapingAnt API Token
- 代理服务器配置

## 🔒 安全配置方案

### 方案 1：使用环境变量（推荐）⭐

**最安全的方式**，敏感信息不会出现在任何文件中。

#### Linux/macOS

```bash
# 临时设置（当前会话有效）
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export TELEGRAM_BOT_TOKEN="your_token"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)

```powershell
# 临时设置
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID="123456789"

# 永久设置（系统环境变量）
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "your_token", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", "your_chat_id", "User")
```

#### 验证环境变量

```bash
echo $TELEGRAM_BOT_TOKEN  # Linux/macOS
echo $env:TELEGRAM_BOT_TOKEN  # Windows PowerShell
```

### 方案 2：使用 config.json（需谨慎）

如果使用 `config.json` 存储敏感信息：

#### ✅ 必须确认的事项

1. **检查 .gitignore**
   ```bash
   cat .gitignore | grep config.json
   ```
   确保输出包含 `config.json`

2. **检查 Git 状态**
   ```bash
   git status
   ```
   确保 `config.json` **不在** "Changes to be committed" 列表中

3. **如果已经提交了敏感信息**（紧急处理）
   ```bash
   # 从 Git 历史中删除敏感文件
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config.json" \
     --prune-empty --tag-name-filter cat -- --all

   # 强制推送（会重写历史，谨慎操作）
   git push origin --force --all

   # 立即更换泄露的 Token
   # 1. 去 @BotFather 重新生成 Bot Token
   # 2. 使用新的 Token 更新配置
   ```

### 方案 3：使用 .env 文件

创建 `.env` 文件（需要 python-dotenv 库）：

```bash
# .env 文件内容
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

确保 `.env` 在 `.gitignore` 中：
```bash
echo ".env" >> .gitignore
```

## 🔍 安全检查清单

在提交代码前，请检查：

- [ ] `config.json` 在 `.gitignore` 中
- [ ] `git status` 不显示 `config.json`
- [ ] 没有在代码中硬编码 Token
- [ ] `.env` 文件（如果使用）在 `.gitignore` 中
- [ ] 没有在日志中打印敏感信息

## 🛡️ 最佳实践

### 1. 使用配置模板

```bash
# 复制示例配置
cp config.example.json config.json

# 编辑配置，填入你的信息
nano config.json  # 或使用你喜欢的编辑器
```

### 2. 环境变量 + 配置文件结合

推荐做法：
- **敏感信息**（Token、密码）→ 环境变量
- **非敏感配置**（路径、选项）→ config.json

```json
{
  "downloadVideoCover": true,
  "outputDir": "./download",
  "telegram": {
    "enabled": true
    // bot_token 和 chat_id 通过环境变量提供
  }
}
```

### 3. 定期轮换凭证

- 每 3-6 个月更换一次 Bot Token
- 如果怀疑泄露，立即更换
- 在 @BotFather 中使用 `/revoke` 撤销旧 Token

### 4. 限制 Bot 权限

在 @BotFather 中：
- 禁用不需要的功能
- 设置 Bot 只能接收消息（不能加入群组等）

## 📋 快速参考

### 优先级顺序

程序读取配置的优先级：
1. **环境变量** ⭐ （最高优先级，最安全）
2. `config.json` （次优先级，需谨慎）
3. 默认值 （最低优先级）

### 推荐配置方式

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 个人开发 | 环境变量 | 最安全，不会误提交 |
| 服务器部署 | 环境变量 | 便于管理多环境 |
| Docker 容器 | 环境变量 | Docker 原生支持 |
| 快速测试 | config.json | 方便，但注意不要提交 |

## 🆘 如果 Token 泄露了怎么办？

1. **立即撤销 Token**
   - 在 Telegram 中找到 @BotFather
   - 发送 `/mybots`
   - 选择你的 bot
   - 选择 "API Token" → "Revoke current token"

2. **生成新 Token**
   - 在同一界面中生成新 Token
   - 更新你的配置（使用新 Token）

3. **检查 Git 历史**
   - 如果已提交到 Git，需要清理历史记录
   - 或者创建新仓库（简单但会失去历史）

4. **监控异常活动**
   - 检查 bot 是否被用于发送未授权消息
   - 在 @BotFather 中查看 bot 统计信息

## 📚 相关资源

- [GitHub: 从历史中删除敏感数据](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Telegram: Bot 安全最佳实践](https://core.telegram.org/bots/security)
- [12-Factor App: 配置管理](https://12factor.net/config)

## ❓ 常见问题

**Q: 我可以在多台机器上使用相同的 Bot 吗？**
A: 可以，只要每台机器都正确配置了 Token 和 Chat ID。

**Q: 环境变量会被其他用户看到吗？**
A: 在 Linux/macOS 上，同一用户的进程可以看到。避免在共享账户上使用。

**Q: 如何在 Docker 中使用环境变量？**
A: 使用 `docker run -e TELEGRAM_BOT_TOKEN="xxx" ...` 或在 `docker-compose.yml` 中配置。

**Q: 可以把 Token 放在源代码中吗？**
A: **绝对不可以！** 这是最不安全的做法。

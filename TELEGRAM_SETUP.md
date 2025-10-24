# Telegram 通知设置指南

## 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示输入 bot 名称（如：`Jable Downloader Bot`）
4. 按提示输入 bot 用户名（必须以 `bot` 结尾，如：`jable_downloader_bot`）
5. 创建成功后会得到 **Bot Token**，格式类似：
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567
   ```
   **重要：保存好这个 token，不要泄露给他人！**

### 2. 获取你的 Chat ID

**方法 1：使用 @userinfobot**
1. 在 Telegram 中搜索 `@userinfobot`
2. 点击 Start 按钮
3. Bot 会回复你的用户信息，包含你的 **ID**（一串数字）

**方法 2：使用 @getidsbot**
1. 在 Telegram 中搜索 `@getidsbot`
2. 点击 Start 按钮
3. 获取你的 Chat ID

### 3. 配置 config.json

在 `config.json` 中添加 `telegram` 配置：

```json
{
  "downloadVideoCover": true,
  "outputDir": "./download",
  "outputFileFormat": "id/title.mp4",
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567",
    "chat_id": "你的chat_id"
  }
}
```

**配置说明**：
- `enabled`: 是否启用 Telegram 通知（`true` 或 `false`）
- `bot_token`: 你的 Bot Token（从 @BotFather 获取）
- `chat_id`: 你的 Chat ID（从 @userinfobot 获取）

### 4. 测试通知

运行测试脚本验证配置：

```bash
python3 telegram_notifier.py
```

如果配置正确，你会在 Telegram 收到测试消息。

## 通知功能

### 支持的通知类型

1. **单个视频下载成功**
   - 视频 ID
   - 视频标题
   - 文件大小
   - 下载耗时

2. **单个视频下载失败**
   - 视频 ID
   - 视频标题
   - 错误信息

3. **批量下载完成**（future feature）
   - 总数、成功数、失败数
   - 总耗时
   - 成功率

### 通知示例

**下载成功通知**：
```
✅ 视频下载完成

ID: abf-274
标题: ABF-274 只要忍耐超過10分鐘...
大小: 1234.56 MB
耗时: 15分30秒
```

**下载失败通知**：
```
❌ 视频下载失败

ID: ssni-193
标题: SSNI-193 天使萌...
错误: 获取下载链接失败
```

## 高级配置

### 发送到群组

如果想把通知发送到群组：

1. 创建一个 Telegram 群组
2. 把你的 bot 添加到群组
3. 获取群组的 Chat ID：
   - 在群组中发送一条消息
   - 访问：`https://api.telegram.org/bot<你的bot_token>/getUpdates`
   - 查找 `"chat":{"id":-123456789,...}` 中的 ID（负数）
4. 将群组 ID 填入 `config.json` 的 `chat_id`

### 禁用通知

临时禁用通知，有两种方法：

**方法 1**：修改 config.json
```json
"telegram": {
  "enabled": false,
  ...
}
```

**方法 2**：删除 telegram 配置
```json
{
  "downloadVideoCover": true,
  ...
  // 不包含 telegram 配置
}
```

## 故障排查

### 无法收到通知

1. **检查配置**
   ```bash
   python3 telegram_notifier.py
   ```

2. **确认 bot 可以发送消息**
   - 在 Telegram 中搜索你的 bot
   - 点击 Start 按钮
   - 尝试与 bot 对话

3. **检查 Chat ID 是否正确**
   - 确认 Chat ID 是数字
   - 如果是群组，确认 ID 是负数

4. **检查网络连接**
   - 确认可以访问 `api.telegram.org`
   - 如果在国内，可能需要代理

### 错误：403 Forbidden

Bot 没有权限发送消息给你：
1. 在 Telegram 中搜索你的 bot
2. 点击 Start 按钮
3. 这会允许 bot 给你发消息

### 错误：Chat not found

Chat ID 不正确：
1. 重新获取 Chat ID
2. 确认 ID 是纯数字（群组是负数）
3. 不要包含引号或其他字符

## 安全建议

1. **不要公开 Bot Token**
   - Bot Token 就像密码，不要提交到 Git
   - 可以使用 `.gitignore` 排除 config.json

2. **使用环境变量**（可选）
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

3. **定期检查 Bot 活动**
   - 在 @BotFather 中可以查看 bot 状态
   - 如果 token 泄露，可以重新生成

## 更多资源

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [BotFather 使用指南](https://core.telegram.org/bots#6-botfather)
- [Python Telegram Bot 库](https://github.com/python-telegram-bot/python-telegram-bot)

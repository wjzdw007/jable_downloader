# 快速开始指南

## 一键安装脚本

### macOS/Linux

```bash
#!/bin/bash

# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 升级 pip
pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装 Playwright 浏览器
playwright install chromium

# 6. 运行测试
python test_playwright.py

echo "✓ 安装完成！现在可以使用 jable_downloader 了"
```

### Windows

```batch
@echo off

REM 1. 创建虚拟环境
python -m venv venv

REM 2. 激活虚拟环境
call venv\Scripts\activate

REM 3. 升级 pip
pip install --upgrade pip

REM 4. 安装依赖
pip install -r requirements.txt

REM 5. 安装 Playwright 浏览器
playwright install chromium

REM 6. 运行测试
python test_playwright.py

echo 安装完成！现在可以使用 jable_downloader 了
```

## 使用示例

### 1. 下载单个视频

```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 下载视频
python main.py videos https://jable.tv/videos/xxxxx/
```

### 2. 下载多个视频

```bash
python main.py videos \
  https://jable.tv/videos/video1/ \
  https://jable.tv/videos/video2/ \
  https://jable.tv/videos/video3/
```

### 3. 订阅管理

```bash
# 添加订阅（单个类别）
python main.py subscription --add https://jable.tv/models/sakura-momo/

# 添加订阅（多个类别交集，如"某女优的中文字幕"）
python main.py subscription --add \
  https://jable.tv/models/sakura-momo/ \
  https://jable.tv/categories/chinese-subtitle/

# 查看所有订阅
python main.py subscription --get

# 同步所有订阅的视频
python main.py subscription --sync-videos

# 只同步指定订阅（例如订阅号 1 和 3）
python main.py subscription --sync-videos --ids 1 3
```

### 4. 配置文件示例

创建或编辑 `config.json`：

```json
{
    "downloadVideoCover": false,
    "downloadInterval": 0,
    "outputDir": "./downloads",
    "outputFileFormat": "title.mp4",
    "proxies": {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
    "save_vpn_traffic": false,
    "videoIdBlockList": [],
    "subscriptions": [],
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://jable.tv"
    },
    "sa_token": "",
    "sa_mode": "browser"
}
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `downloadVideoCover` | 是否下载封面 | `false` |
| `downloadInterval` | 下载间隔（秒） | `0` |
| `outputDir` | 输出目录 | `./` |
| `outputFileFormat` | 文件命名格式 | `title.mp4` |
| `proxies` | 代理配置 | `{}` |
| `save_vpn_traffic` | 节省VPN流量 | `false` |
| `videoIdBlockList` | 跳过的视频ID列表 | `[]` |
| `sa_token` | ScrapingAnt Token | `""` (留空使用本地 Playwright) |

### 文件命名格式

- `title.mp4`: 视频标题.mp4 (推荐)
- `id.mp4`: 番号.mp4
- `id/title.mp4`: 番号目录/视频标题.mp4
- `id/id.mp4`: 番号目录/番号.mp4

## 常见问题

### Q1: 如何使用代理？

A: 在 `config.json` 中配置：

```json
{
    "proxies": {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
}
```

### Q2: 下载的视频无法播放？

A: 尝试以下方法：
1. 使用 [mpv 播放器](https://mpv.io/)
2. 使用 ffmpeg 重新编码：
   ```bash
   ffmpeg -i input.mp4 -c:v libx264 -c:a copy output.mp4
   ```

### Q3: 如何压缩视频？

A: 使用 h265 编码可以将体积减少到原来的 1/3：

```bash
ffmpeg -i input.mp4 -c:v libx265 -vtag hvc1 -c:a copy output.mkv
```

### Q4: 如何避免重复下载？

A: 程序会自动检测已下载的视频并跳过。如需手动跳过某些视频，添加到 `videoIdBlockList`：

```json
{
    "videoIdBlockList": ["abc-123", "def-456"]
}
```

### Q5: Playwright 启动失败？

A: 运行诊断脚本：

```bash
python test_playwright_debug.py
```

如果仍有问题，尝试重新安装：

```bash
pip install --upgrade playwright
playwright install chromium
```

## 性能优化建议

1. **使用本地 Playwright**：免费且稳定，适合个人使用
2. **配置下载间隔**：避免被服务器限流
3. **开启 VPN 流量节省**：`"save_vpn_traffic": true`
4. **使用订阅功能**：自动化下载，无需手动查找

## 进阶技巧

### 批量添加订阅

创建脚本 `add_subscriptions.sh`：

```bash
#!/bin/bash
source venv/bin/activate

python main.py subscription --add https://jable.tv/models/model1/
python main.py subscription --add https://jable.tv/models/model2/
python main.py subscription --add https://jable.tv/tags/tag1/
```

### 定时同步（使用 cron）

编辑 crontab：

```bash
crontab -e
```

添加定时任务（每天凌晨 2 点同步）：

```
0 2 * * * cd /path/to/jable_downloader && source venv/bin/activate && python main.py subscription --sync-videos
```

### Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install chromium --with-deps

COPY . .
CMD ["python", "main.py", "subscription", "--sync-videos"]
```

## 获取帮助

```bash
# 查看主帮助
python main.py --help

# 查看视频下载帮助
python main.py videos --help

# 查看订阅管理帮助
python main.py subscription --help
```

## 更新日志

### v2.0 (Playwright 版本)
- ✅ 迁移到 Playwright，无需 Go 环境
- ✅ 纯 Python 实现，简化部署
- ✅ 改进错误处理和重试机制
- ✅ 添加详细的测试和文档

### v1.0 (ChromeDP 版本)
- 基础视频下载功能
- 订阅管理功能
- 使用 Go ChromeDP

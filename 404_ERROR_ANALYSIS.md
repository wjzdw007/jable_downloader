# 404 错误分析

## 问题现象

```
[4/5] 正在解析视频播放列表...
  - 正在下载 m3u8 文件...
    ⚠ HTTP错误 (尝试 1/5): 状态码 404
    ⏳ 10秒后重试...
```

## 可能的原因

### 1. ❌ m3u8 URL 提取不完整

**原因**: 正则表达式 `https://.+m3u8` 是贪婪匹配，可能会匹配到多余的内容

**示例**:
```
正确: https://cdn.example.com/video/playlist.m3u8
错误: https://cdn.example.com/video/playlist.m3u8?param=value&other=data
```

**解决方案**: 使用非贪婪匹配
```python
# 旧的
result = re.search("https://.+m3u8", page_str)

# 新的
result = re.search(r"https://.+?\.m3u8", page_str)
```

### 2. ❌ URL 包含引号或其他字符

**原因**: HTML 中的 URL 可能被引号包围

**示例**:
```html
<script>
var videoUrl = "https://cdn.example.com/video.m3u8";
</script>
```

提取结果可能是: `https://cdn.example.com/video.m3u8";` （包含引号）

**解决方案**: 提取后清理 URL
```python
m3u8url = result[0].strip('"\'')
```

### 3. ❌ 视频有时效性限制

**原因**: 某些视频网站的 m3u8 URL 包含时间戳或签名

**示例**:
```
https://cdn.example.com/video.m3u8?expires=1234567890&signature=abc123
```

这类 URL 可能在几分钟后就失效。

**解决方案**: 需要在获取 URL 后立即下载

### 4. ❌ 需要特定的请求头

**原因**: CDN 可能检查 Referer、User-Agent 等请求头

**当前配置**:
```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Referer": "https://jable.tv"
}
```

**可能需要**: 视频页面的完整 URL 作为 Referer

### 5. ❌ 需要代理访问 CDN

**原因**: 视频 CDN 可能有地区限制

**当前配置**:
```json
"proxies": {}  // 空的
```

**解决方案**: 配置代理
```json
"proxies": {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081"
}
```

### 6. ❌ 网站更新了视频加载方式

**原因**: 网站可能改用了新的视频播放技术

**可能性**:
- 改用了加密的 URL
- 改用了动态加载
- 改用了其他视频格式

---

## 诊断步骤

### 步骤 1: 运行调试脚本

```bash
source venv/bin/activate
python debug_video_url.py
```

这个脚本会：
1. 获取视频页面
2. 提取 m3u8 URL
3. 显示完整的 URL
4. 尝试访问并显示状态码
5. 如果成功，显示 m3u8 内容预览

### 步骤 2: 检查 URL 格式

调试脚本会输出类似：
```
✓ 找到 m3u8 URL:
  https://assets-cdn.jable.tv/contents/videos_screenshots/...

URL分析:
  [0] https:
  [1]
  [2] assets-cdn.jable.tv
  [3] contents
  [4] videos_screenshots
  ...
```

检查：
- URL 是否完整
- 是否包含奇怪的字符
- 路径是否正确

### 步骤 3: 检查网络连接

```bash
python test_network.py
```

查看：
- CDN 是否可访问
- 是否需要代理

### 步骤 4: 手动测试 URL

如果调试脚本输出了完整的 m3u8 URL，可以：

1. **使用浏览器访问**: 在浏览器中打开 URL 看是否能下载
2. **使用 curl 测试**:
   ```bash
   curl -I "https://assets-cdn.jable.tv/path/to/video.m3u8"
   ```
3. **使用代理测试**:
   ```bash
   curl -x http://127.0.0.1:1081 -I "URL"
   ```

---

## 快速修复尝试

### 修复 1: 改进正则表达式

编辑 `video_crawler.py`:

```python
# 旧的
result = re.search("https://.+m3u8", page_str)

# 新的 - 非贪婪匹配，并确保以.m3u8结尾
result = re.search(r'https://[^\s"\']+\.m3u8(?:\?[^\s"\']*)?', page_str)
```

### 修复 2: 添加完整的请求头

编辑 `utils.py` 的 `requests_with_retry` 函数调用：

```python
response = utils.requests_with_retry(
    m3u8url,
    headers={
        **HEADERS,
        'Referer': url  # 使用视频页面URL作为Referer
    },
    retry=5
)
```

### 修复 3: 配置代理

编辑 `config.json`:

```json
{
    "proxies": {
        "http": "http://127.0.0.1:1081",
        "https": "http://127.0.0.1:1081"
    }
}
```

---

## 预期的正常输出

如果修复成功，应该看到：

```
[4/5] 正在解析视频播放列表...
  - 正在下载 m3u8 文件: playlist.m3u8
  ✓ m3u8 文件下载成功
  - 正在解析播放列表...
  ✓ 找到 450 个视频片段
```

---

## 下一步行动

1. **立即运行**: `python debug_video_url.py` 查看详细信息
2. **检查输出**: 看 m3u8 URL 是否正确
3. **根据结果**: 应用相应的修复方案
4. **重新测试**: 运行下载命令

---

**创建日期**: 2025-10-23
**用途**: 诊断和修复 m3u8 下载 404 错误

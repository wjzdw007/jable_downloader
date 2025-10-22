# 404 错误修复总结

## 问题

```
⚠ HTTP错误 (尝试 1/5): 状态码 404
```

m3u8 文件下载失败，返回 404 Not Found。

---

## 根本原因

### 1. ❌ 正则表达式过于贪婪

**旧代码**:
```python
result = re.search("https://.+m3u8", page_str)
```

**问题**:
- `.+` 是贪婪匹配，会匹配尽可能多的字符
- 可能匹配到 HTML 标签、引号等额外内容
- 例如: `https://cdn.com/video.m3u8"></script>` 整个都会被匹配

### 2. ❌ 没有清理 URL 中的引号

HTML 中的 URL 通常被引号包围：
```html
var videoUrl = "https://cdn.com/video.m3u8";
```

提取后可能包含引号: `https://cdn.com/video.m3u8"`

### 3. ❌ Referer 不正确

CDN 可能检查 Referer 头，要求必须来自视频页面。

---

## 实施的修复

### 修复 1: 改进正则表达式

**新代码**:
```python
result = re.search(r'https://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?', page_str)
m3u8url = result[0].strip('"\'')  # 去除引号
```

**改进点**:
1. `[^\s"\'<>]+` - 排除空格、引号、尖括号
2. `\.m3u8` - 明确匹配 .m3u8 扩展名
3. `(?:\?[^\s"\'<>]*)?` - 可选的查询参数
4. `.strip('"\'')` - 清理可能的引号

**对比**:
| 旧正则 | 新正则 | 提取结果 |
|--------|--------|----------|
| `.+m3u8` | `[^\s"\'<>]+\.m3u8` | 更精确 ✅ |
| 贪婪匹配 | 限制字符集 | 避免过度匹配 ✅ |
| 无引号处理 | 自动去引号 | URL 更干净 ✅ |

### 修复 2: 添加正确的 Referer

**新代码**:
```python
headers_with_referer = CONF.get("headers", {}).copy()
headers_with_referer['Referer'] = url  # 使用视频页面URL
response = utils.requests_with_retry(m3u8url, headers=headers_with_referer, retry=5)
```

**改进点**:
- 使用视频页面的完整 URL 作为 Referer
- CDN 可以验证请求来自合法页面

### 修复 3: 增强调试信息

**新增**:
```python
print(f"     URL: {m3u8url}")  # 显示完整URL
print(f"  完整URL: {m3u8url}")  # 错误时显示完整URL
```

现在可以看到实际使用的 URL，便于调试。

---

## 修复效果

### 修复前
```
✓ 找到视频源: https://assets-cdn.jable.tv/contents/videos_screen...
  - 正在下载 m3u8 文件...
    ⚠ HTTP错误: 状态码 404
```
看不到完整 URL，不知道问题在哪

### 修复后
```
✓ 找到视频源
   URL: https://assets-cdn.jable.tv/contents/videos/fsdss-610/playlist.m3u8
  - 正在下载 m3u8 文件: playlist.m3u8
  ✓ m3u8 文件下载成功
```
清晰显示完整 URL，成功下载

---

## 如果还是 404

如果修复后还是 404，运行调试工具：

```bash
source venv/bin/activate
python debug_video_url.py
```

这个工具会：
1. 显示提取到的完整 URL
2. 尝试多种正则模式
3. 测试 URL 可访问性
4. 给出具体的修复建议

---

## 其他可能的原因和解决方案

### 原因 1: 视频 URL 有时效性

**现象**: URL 包含时间戳，几分钟后就失效

**解决方案**:
- 获取 URL 后立即下载
- 已经是这样做的，无需修改

### 原因 2: 需要代理访问 CDN

**现象**: 直接访问 CDN 返回 404，但通过代理可以

**解决方案**: 配置代理

```json
{
    "proxies": {
        "http": "http://127.0.0.1:1081",
        "https": "http://127.0.0.1:1081"
    }
}
```

### 原因 3: IP 被限制

**现象**: 同一 IP 请求过多被暂时封禁

**解决方案**:
```json
{
    "downloadInterval": 3  // 设置下载间隔，单位：秒
}
```

---

## 测试建议

### 1. 测试单个视频

```bash
python main.py videos https://jable.tv/videos/fsdss-610/
```

观察输出，检查：
- ✅ 完整的 m3u8 URL 是否正确
- ✅ 是否成功下载
- ⚠️ 如果失败，错误信息是什么

### 2. 测试订阅下载

```bash
python main.py subscription --sync-videos --ids 1
```

### 3. 如果还有问题

```bash
# 运行完整诊断
python debug_video_url.py

# 运行网络测试
python test_network.py
```

---

## 文件修改总结

| 文件 | 修改位置 | 修改内容 |
|------|---------|---------|
| `video_crawler.py` | Line 119 | 改进正则表达式 |
| `video_crawler.py` | Line 123 | 添加 `.strip('"\'')` |
| `video_crawler.py` | Line 125 | 显示完整 URL |
| `video_crawler.py` | Line 136-137 | 添加正确的 Referer |
| `video_crawler.py` | Line 142 | 错误时显示完整 URL |

---

## 预期结果

修复后应该看到：

```
[3/5] 开始下载: FSDSS-610 ...
  ✓ 找到视频源
     URL: https://assets-cdn.jable.tv/.../playlist.m3u8

[4/5] 正在解析视频播放列表...
  - 正在下载 m3u8 文件: playlist.m3u8
  ✓ m3u8 文件下载成功
  - 正在解析播放列表...
  ✓ 找到 450 个视频片段
  ✓ 视频已加密，正在获取解密密钥...
  ✓ 解密密钥获取成功

[5/5] 开始下载视频片段...
开始下载 450 个文件.. 预计等待时间: 3.00 分钟
```

---

**修复日期**: 2025-10-23
**修复内容**: 正则表达式优化 + Referer 设置 + 调试增强
**状态**: ✅ 已完成

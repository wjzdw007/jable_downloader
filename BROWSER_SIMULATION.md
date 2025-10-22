# 浏览器模拟和反检测技术说明

## 📋 概述

本项目使用 Playwright 模拟真实浏览器行为，以绕过 Cloudflare 等反爬虫检测。本文档详细说明了实现的所有反检测技术。

---

## 🎯 实现的反检测技术

### 1. HTTP 头部完全模拟 ✅

#### Sec-Ch-Ua 系列（Client Hints）
```
sec-ch-ua: "Chromium";v="131", "Not_A Brand";v="24"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
```

**作用**: 让服务器识别为 Chrome 131 浏览器，运行在 macOS 上

#### Sec-Fetch 系列（Fetch Metadata）
```
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
```

**作用**: 告诉服务器这是用户主动导航到页面（而不是脚本请求）

#### 标准 HTTP 头部
```
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
accept-encoding: gzip, deflate, br, zstd
upgrade-insecure-requests: 1
dnt: 1
```

**作用**: 模拟真实浏览器的接受类型和语言偏好

---

### 2. Cookie 持久化管理 ✅

#### 工作原理
1. **首次访问**: 保存 Cloudflare 和网站的所有 Cookie 到 `.jable_cookies.json`
2. **后续访问**: 自动加载并使用之前保存的 Cookie
3. **验证通过**: Cloudflare 验证通过后立即更新保存的 Cookie

#### 好处
- Cloudflare 识别为"回头客"而不是新访问者
- 减少验证频率和难度
- 保持会话连续性

#### Cookie 管理工具
```bash
# 查看保存的 Cookie
python3 manage_cookies.py show

# 删除保存的 Cookie（重新开始）
python3 manage_cookies.py delete

# 导出 Cookie 为 Netscape 格式（用于 curl）
python3 manage_cookies.py export
```

---

### 3. JavaScript 自动化特征隐藏 ✅

#### 隐藏 WebDriver 特征
```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
delete navigator.__proto__.webdriver;
```

**作用**: 让 `navigator.webdriver` 返回 `undefined` 而不是 `true`

#### 伪造 Chrome 对象
```javascript
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};
```

**作用**: 添加 Chrome 浏览器特有的全局对象

#### 伪造 Plugins
```javascript
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
```

**作用**: 模拟浏览器插件存在

#### 伪造 Battery API
```javascript
Object.defineProperty(navigator, 'getBattery', {
    get: () => () => Promise.resolve({
        charging: true,
        chargingTime: 0,
        dischargingTime: Infinity,
        level: 1
    })
});
```

**作用**: 添加电池 API（自动化脚本通常没有）

#### 伪造网络连接信息
```javascript
Object.defineProperty(navigator, 'connection', {
    get: () => ({
        effectiveType: '4g',
        rtt: 50,
        downlink: 10,
        saveData: false
    })
});
```

**作用**: 模拟 4G 网络连接

#### 修复 Permissions API
```javascript
Object.defineProperty(navigator, 'permissions', {
    get: () => ({
        query: () => Promise.resolve({ state: 'granted' })
    })
});
```

**作用**: 防止通过权限 API 检测自动化

---

### 4. 真实用户行为模拟 ✅

#### 随机视口大小
```python
viewport_width = random.randint(1366, 1920)
viewport_height = random.randint(768, 1080)
page.set_viewport_size({'width': viewport_width, 'height': viewport_height})
```

**作用**: 每次访问使用不同的窗口大小

#### 随机鼠标移动
```python
for _ in range(random.randint(2, 4)):
    x = random.randint(100, viewport_width - 100)
    y = random.randint(100, viewport_height - 100)
    page.mouse.move(x, y)
    page.wait_for_timeout(random.randint(100, 300))
```

**作用**: 模拟真实用户移动鼠标

#### 随机滚动
```python
for _ in range(random.randint(1, 3)):
    page.mouse.wheel(0, random.randint(100, 300))
    page.wait_for_timeout(random.randint(500, 1000))
```

**作用**: 模拟真实用户滚动页面

#### 智能等待
- 页面加载后等待关键元素
- 遇到 Cloudflare 验证时持续模拟用户行为
- 每 3 秒检查一次验证状态

---

### 5. 浏览器配置优化 ✅

#### 启动参数
```python
'--disable-blink-features=AutomationControlled'  # 禁用自动化特征
'--no-sandbox'                                   # 沙箱模式
'--disable-dev-shm-usage'                        # 共享内存
'--disable-web-security'                         # 禁用同源策略限制
'--disable-features=IsolateOrigins,site-per-process'
```

#### 上下文配置
```python
'locale': 'zh-TW',              # 台湾中文
'timezone_id': 'Asia/Taipei',   # 台北时区
'device_scale_factor': 1,       # 设备缩放
'java_script_enabled': True,    # 启用 JavaScript
```

---

## 🧪 测试

### 测试浏览器模拟
```bash
python3 test_browser_simulation.py
```

这个脚本会：
1. 显示当前的所有配置
2. 测试访问演员页面
3. 检查是否成功绕过 Cloudflare
4. 分析页面内容和 Cookie
5. 显示详细的测试结果

### 测试头部对比
```bash
python3 test_headers.py
```

对比真实浏览器和 Playwright 的 HTTP 头部差异

---

## 📊 检测对比

### 改进前 ❌
| 特征 | 状态 | 说明 |
|------|------|------|
| `navigator.webdriver` | `true` | 明显的自动化特征 |
| Sec-Ch-Ua 头部 | ❌ 缺失 | 没有 Client Hints |
| Sec-Fetch-* 头部 | ❌ 缺失 | 没有 Fetch Metadata |
| Accept-Language | `en-US,en;q=0.9` | 单一语言 |
| window.chrome | ❌ 不存在 | 不像 Chrome 浏览器 |
| Cookie | ❌ 不保存 | 每次都是新访问者 |
| 用户行为 | ❌ 无 | 没有鼠标和滚动 |

### 改进后 ✅
| 特征 | 状态 | 说明 |
|------|------|------|
| `navigator.webdriver` | `undefined` | ✅ 已隐藏 |
| Sec-Ch-Ua 头部 | ✅ 完整 | Chrome 131 on macOS |
| Sec-Fetch-* 头部 | ✅ 完整 | 用户导航 |
| Accept-Language | `zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7` | ✅ 多语言 |
| window.chrome | ✅ 存在 | 完整的 Chrome 对象 |
| Cookie | ✅ 持久化 | 自动保存和加载 |
| 用户行为 | ✅ 模拟 | 鼠标移动和滚动 |

---

## 🔍 调试

### 查看发送的请求
```bash
# 使用 Chrome DevTools Protocol
PWDEBUG=1 python3 test_browser_simulation.py
```

### 查看保存的 Cookie
```bash
python3 manage_cookies.py show
```

### 检查 Cloudflare 状态
```bash
python3 check_proxy.py
```

### 调试演员页面解析
```bash
python3 debug_model_page.py https://jable.tv/models/xxx/
```

---

## 💡 如果仍然被检测

### 方案 1: 使用住宅代理（推荐）⭐
```json
{
  "proxies": {
    "http": "http://user:pass@proxy.provider.com:port",
    "https": "http://user:pass@proxy.provider.com:port"
  }
}
```

**优势**:
- 真实的住宅 IP
- 地理位置匹配（台湾）
- 成功率最高

**推荐服务商**:
- Bright Data
- Smartproxy
- Oxylabs

### 方案 2: 使用 ScrapingAnt
```json
{
  "sa_token": "your_scrapingant_token",
  "sa_mode": "browser"
}
```

**优势**:
- 专业的反检测服务
- 自动处理 Cloudflare
- 按请求计费

### 方案 3: 本地运行
在本地 macOS/Windows 环境运行，通常检测更少

### 方案 4: 定期更换 Cookie
```bash
# 删除旧 Cookie，让程序获取新的
python3 manage_cookies.py delete
```

---

## 📝 检测原理说明

### Cloudflare 的检测方法

1. **TLS 指纹识别**
   - 检查 TLS ClientHello 特征
   - 自动化工具的 TLS 特征与真实浏览器不同

2. **HTTP/2 指纹识别**
   - 检查 HTTP/2 帧顺序和优先级
   - 不同浏览器有不同的特征

3. **JavaScript 环境检测**
   - 检查 `navigator.webdriver`
   - 检查 `window.chrome` 对象
   - 检查各种 API 的存在性和行为

4. **行为分析**
   - 鼠标移动轨迹
   - 页面停留时间
   - 滚动行为
   - 键盘输入特征

5. **HTTP 头部分析**
   - 检查 Sec-Ch-Ua, Sec-Fetch-* 等现代头部
   - 检查 Accept-Language 等标准头部
   - 检查头部顺序和组合

6. **Cookie 和会话分析**
   - 新访问者 vs 回头客
   - 会话连续性
   - Cookie 的完整性

### 我们的应对策略

| 检测方法 | 我们的应对 | 效果 |
|----------|------------|------|
| TLS 指纹 | 使用真实 Chromium 浏览器 | ✅ 完全匹配 |
| HTTP/2 指纹 | Playwright 使用真实引擎 | ✅ 完全匹配 |
| JavaScript 检测 | 完整的特征隐藏和伪造 | ✅ 高效 |
| 行为分析 | 随机鼠标和滚动模拟 | ✅ 较好 |
| HTTP 头部 | 完整的头部模拟 | ✅ 完全匹配 |
| Cookie 分析 | Cookie 持久化 | ✅ 高效 |

---

## 📚 相关资源

### 官方文档
- [Playwright 文档](https://playwright.dev/python/)
- [Cloudflare Bot Management](https://developers.cloudflare.com/bots/)

### 检测工具
- [Fingerprint.com](https://fingerprint.com/demo/) - 浏览器指纹检测
- [BrowserLeaks](https://browserleaks.com/) - 浏览器特征泄露检测
- [CreepJS](https://abrahamjuliot.github.io/creepjs/) - JavaScript 环境检测

### 参考项目
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [playwright-stealth](https://github.com/AtuboDad/playwright_stealth)
- [puppeteer-extra-plugin-stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth)

---

## ⚖️ 免责声明

本项目仅供学习和研究使用。使用者应遵守目标网站的服务条款和 robots.txt 规定。

- 不要过于频繁地请求
- 尊重网站的访问限制
- 考虑使用官方 API（如果有）
- 注意版权和隐私问题

---

## 🆘 故障排除

### 问题 1: 仍然遇到 Cloudflare 验证
**原因**:
- 服务器 IP 被标记为可疑
- 请求频率过高
- JavaScript 执行环境仍有特征

**解决方案**:
1. 使用住宅代理
2. 降低请求频率
3. 删除旧 Cookie 重试
4. 在本地环境测试

### 问题 2: Cookie 加载失败
**原因**: Cookie 文件损坏或格式错误

**解决方案**:
```bash
python3 manage_cookies.py delete
# 重新运行程序获取新 Cookie
```

### 问题 3: 演员名称提取失败
**原因**: 页面结构变化或 Cloudflare 拦截

**解决方案**:
```bash
# 调试页面内容
python3 debug_model_page.py <URL>
# 检查保存的 HTML 文件
```

### 问题 4: 请求超时
**原因**: 网络问题或代理配置错误

**解决方案**:
```bash
# 检查代理和网络
python3 check_proxy.py
```

---

**最后更新**: 2025-10-23
**版本**: 2.0 (完整浏览器模拟)

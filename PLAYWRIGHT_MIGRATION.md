# Playwright 迁移说明

## 概述

本项目已从 Go 的 ChromeDP 迁移到 Python 的 Playwright，实现了纯 Python 解决方案，无需再下载和维护多平台的二进制可执行文件。

## 变更内容

### 1. 依赖变更

**之前**：需要下载对应平台的 `chromedp_jable` 二进制文件
**现在**：使用 Python 的 Playwright 库

### 2. 优势

- ✅ **纯 Python 实现**：无需 Go 环境和跨平台编译
- ✅ **统一依赖管理**：所有依赖通过 pip 安装
- ✅ **更好的维护性**：Playwright 由微软官方维护，更新活跃
- ✅ **更强大的功能**：支持更多浏览器特性和调试选项
- ✅ **简化部署**：不再需要根据系统架构下载不同的二进制文件

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 3. 配置（可选）

编辑 `config.json` 文件，可以选择：

**方式一：使用 ScrapingAnt API（推荐用于生产环境）**
```json
{
    "sa_token": "your_scrapingant_token",
    "sa_mode": "browser"
}
```

**方式二：使用本地 Playwright（免费，适合个人使用）**
```json
{
    "sa_token": "",
    ...
}
```

如果 `sa_token` 为空，程序将自动使用本地 Playwright。

## 使用方法

使用方法与之前完全相同：

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 下载单个视频
python main.py videos https://jable.tv/videos/xxxxx/

# 添加订阅
python main.py subscription --add https://jable.tv/models/xxx/

# 同步订阅
python main.py subscription --sync-videos
```

## 测试

运行测试脚本验证 Playwright 是否正常工作：

```bash
# 基础测试
python test_playwright.py

# 详细调试测试
python test_playwright_debug.py
```

## 系统要求

- Python 3.8+
- 支持的操作系统：
  - macOS 10.13+
  - Ubuntu 18.04+
  - Windows 10+

## 故障排除

### 问题 1: Playwright 安装失败

```bash
# 尝试重新安装 Playwright
pip install --upgrade playwright
playwright install chromium
```

### 问题 2: 浏览器启动失败

```bash
# 安装系统依赖（仅 Linux）
playwright install-deps chromium
```

### 问题 3: 代理配置问题

确保 `config.json` 中的代理格式正确：

```json
{
    "proxies": {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
}
```

## 技术细节

### 实现文件

- `utils.py`: 新增 `get_response_from_playwright()` 函数
- `requirements.txt`: 添加 `playwright>=1.48.0` 依赖

### 关键特性

1. **超时控制**：浏览器启动超时 60 秒，页面加载超时 30 秒
2. **重试机制**：失败后自动重试 3 次，间隔递增
3. **代理支持**：完全兼容原有代理配置
4. **User-Agent 模拟**：使用自定义 User-Agent 避免检测
5. **资源清理**：使用 try-finally 确保浏览器正常关闭

## 性能对比

| 指标 | ChromeDP (Go) | Playwright (Python) |
|------|---------------|---------------------|
| 启动速度 | ~1s | ~1.5s |
| 内存占用 | ~150MB | ~200MB |
| 维护成本 | 高（多平台编译） | 低（pip 安装） |
| 功能丰富度 | 中 | 高 |

## 迁移清单

- [x] 添加 Playwright 依赖到 requirements.txt
- [x] 实现 `get_response_from_playwright()` 函数
- [x] 移除 platform、subprocess 等不再需要的导入
- [x] 删除 `get_chromdp_binary_by_cpu_info()` 等 ChromeDP 相关函数
- [x] 创建测试脚本验证功能
- [x] 更新使用文档

## 向后兼容性

✅ **完全兼容**：迁移后的代码与原有功能完全兼容，无需修改配置文件或使用方式。

## 反馈与支持

如遇到问题，请在 GitHub Issues 中反馈。

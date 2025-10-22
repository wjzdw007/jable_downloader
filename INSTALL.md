# 安装指南

本文档详细说明如何在不同环境下安装 Jable Downloader。

---

## 一键安装（推荐）

### Linux / macOS

```bash
# 克隆或下载项目后，进入项目目录
cd jable_downloader

# 运行安装脚本
sudo ./install.sh
```

**脚本会自动完成:**
1. ✅ 检测操作系统
2. ✅ 检查 Python 版本
3. ✅ 自动安装系统依赖（python3-venv, python3-pip）
4. ✅ 创建虚拟环境
5. ✅ 安装 Python 依赖包
6. ✅ 下载 Playwright Chromium 浏览器
7. ✅ 运行测试验证安装

### Windows

```cmd
# 双击运行或在命令行执行
install.bat
```

---

## 手动安装

如果一键安装失败，请按以下步骤手动安装：

### 1. 安装系统依赖

#### Ubuntu / Debian

```bash
# 更新包列表
sudo apt-get update

# 安装 Python 虚拟环境和 pip
sudo apt-get install -y python3-venv python3-pip

# 可选：安装浏览器依赖
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

#### CentOS / RHEL / Fedora

```bash
# CentOS 8+ / Fedora
sudo dnf install -y python3-venv python3-pip

# CentOS 7
sudo yum install -y python3-venv python3-pip
```

#### macOS

```bash
# 使用 Homebrew
brew install python3

# Python 3 自带 venv，无需额外安装
```

### 2. 创建虚拟环境

```bash
# 进入项目目录
cd jable_downloader

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖包
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
# 安装 Chromium 浏览器
playwright install chromium

# Linux: 安装浏览器系统依赖
playwright install-deps chromium
```

### 5. 验证安装

```bash
# 运行测试脚本
python test_playwright.py
```

如果看到以下输出，说明安装成功：

```
测试 Playwright 基本功能
正在安装 Chromium (如果需要)...
正在启动浏览器...
✓ 成功访问 jable.tv
✓ 标题: Jable TV...
✓ 找到视频元素
✓ Playwright 工作正常！
```

---

## 远程服务器安装

### 场景 1: 通过 SSH 连接的远程服务器

安装脚本已经优化，可以直接使用：

```bash
# 方式 1: 使用 sudo（推荐）
sudo ./install.sh

# 方式 2: 使用 root 用户
./install.sh
```

**注意事项:**
- 脚本会自动检测操作系统并安装依赖
- 需要 sudo 权限来安装系统包（python3-venv, python3-pip）
- Playwright 下载浏览器需要约 100MB 网络流量

### 场景 2: 无 sudo 权限的受限环境

如果您没有 sudo 权限，需要请管理员先安装系统依赖：

```bash
# 管理员需要运行:
sudo apt-get install python3-venv python3-pip

# 然后您可以运行:
./install.sh
```

或者完全手动安装（参考上面的手动安装步骤）。

### 场景 3: 无互联网或受限网络

如果服务器无法访问外网，需要：

1. **在有网络的机器上下载依赖:**
```bash
# 下载 Python 包
pip download -r requirements.txt -d packages/

# 下载 Playwright 浏览器
playwright install chromium
# 浏览器位置: ~/.cache/ms-playwright/
```

2. **上传到远程服务器并安装:**
```bash
# 安装 Python 包
pip install --no-index --find-links=packages/ -r requirements.txt

# 复制浏览器文件
cp -r ~/.cache/ms-playwright/ /path/to/remote/home/.cache/
```

---

## 常见问题

### 问题 1: `ensurepip is not available`

**错误信息:**
```
The virtual environment was not created successfully because ensurepip is not
available. On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.8-venv
```

**解决方案:**

优化后的安装脚本会自动处理这个问题。如果仍然遇到，手动安装：

```bash
# Ubuntu/Debian
sudo apt-get install python3-venv python3-pip

# 注意：根据您的 Python 版本，可能需要:
sudo apt-get install python3.8-venv  # Python 3.8
sudo apt-get install python3.9-venv  # Python 3.9
sudo apt-get install python3.10-venv # Python 3.10
```

### 问题 2: Playwright 浏览器下载失败

**错误信息:**
```
✗ Chromium 浏览器安装失败
```

**解决方案:**

1. **检查网络连接:**
```bash
# 测试网络
curl -I https://playwright.azureedge.net

# 如果无法访问，可能需要配置代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

2. **手动下载并安装:**
```bash
# 使用代理下载
HTTP_PROXY=http://proxy:port playwright install chromium

# 或者使用环境变量
export PLAYWRIGHT_DOWNLOAD_HOST=https://mirrors.huaweicloud.com/playwright/
playwright install chromium
```

3. **使用国内镜像（中国大陆用户）:**
```bash
# 设置镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 问题 3: 浏览器启动失败

**错误信息:**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**解决方案:**

```bash
# 重新安装浏览器
playwright install chromium

# Linux: 安装系统依赖
sudo playwright install-deps chromium

# 检查浏览器是否存在
ls ~/.cache/ms-playwright/
```

### 问题 4: 权限问题

**错误信息:**
```
Permission denied: '/path/to/venv'
```

**解决方案:**

```bash
# 检查当前目录权限
ls -la

# 修改项目目录权限
sudo chown -R $USER:$USER .

# 或者使用其他目录
cd ~/projects
git clone <repository>
cd jable_downloader
./install.sh
```

### 问题 5: Python 版本过低

**错误信息:**
```
错误: 未找到 python3，请先安装 Python 3.8+
```

**解决方案:**

```bash
# Ubuntu/Debian: 安装 Python 3.8+
sudo apt-get install python3.8 python3.8-venv python3.8-pip

# 或使用 deadsnakes PPA（Ubuntu）
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3.10-pip

# CentOS/RHEL: 启用额外仓库
sudo yum install epel-release
sudo yum install python38
```

---

## 验证安装

### 快速测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行基础测试
python test_playwright.py
```

### 完整测试

```bash
# 功能测试（模拟数据）
python test_functionality.py

# 真实网站测试
python test_real_site.py
```

### 下载测试视频

```bash
# 下载单个视频
python main.py videos https://jable.tv/videos/fsdss-610/

# 查看帮助
python main.py --help
```

---

## 卸载

```bash
# 删除虚拟环境
rm -rf venv/

# 删除 Playwright 浏览器
rm -rf ~/.cache/ms-playwright/

# 删除项目
cd ..
rm -rf jable_downloader/
```

---

## 获取帮助

如果安装过程中遇到问题：

1. **查看详细文档:**
   - `cat QUICKSTART.md` - 快速开始指南
   - `cat PLAYWRIGHT_MIGRATION.md` - Playwright 迁移说明

2. **运行调试脚本:**
   ```bash
   python test_playwright_debug.py
   python test_network.py
   ```

3. **查看日志:**
   ```bash
   # 安装日志
   ./install.sh 2>&1 | tee install.log
   ```

4. **提交 Issue:**
   - GitHub: https://github.com/wjzdw007/jable_downloader/issues

---

**最后更新:** 2025-10-23
**适用版本:** Playwright 1.48.0+

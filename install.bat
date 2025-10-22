@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM jable_downloader 一键安装脚本 (Windows)

echo ==================================
echo   Jable Downloader 安装脚本
echo ==================================
echo.

REM 检查 Python 版本
echo [1/6] 检查 Python 版本...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 python，请先安装 Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set PYTHON_VERSION=%%i
echo     √ Python 版本: %PYTHON_VERSION%
echo.

REM 创建虚拟环境
echo [2/6] 创建虚拟环境...
if exist venv\ (
    echo     虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo     √ 虚拟环境创建成功
)
echo.

REM 激活虚拟环境
echo [3/6] 激活虚拟环境...
call venv\Scripts\activate
echo     √ 虚拟环境已激活
echo.

REM 升级 pip
echo [4/6] 升级 pip...
pip install --upgrade pip -q
echo     √ pip 已升级到最新版本
echo.

REM 安装依赖
echo [5/6] 安装 Python 依赖...
pip install -r requirements.txt -q
echo     √ Python 依赖安装完成
echo.

REM 安装 Playwright 浏览器
echo [6/6] 安装 Playwright Chromium 浏览器...
playwright install chromium
echo     √ Chromium 浏览器安装完成
echo.

REM 运行测试
echo ==================================
echo   运行测试验证安装
echo ==================================
echo.

python test_playwright.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================
    echo   √ 安装成功！
    echo ==================================
    echo.
    echo 使用方法:
    echo   1. 激活虚拟环境:
    echo      venv\Scripts\activate
    echo.
    echo   2. 下载视频:
    echo      python main.py videos https://jable.tv/videos/xxxxx/
    echo.
    echo   3. 查看帮助:
    echo      python main.py --help
    echo.
    echo 详细文档:
    echo   - 快速开始: type QUICKSTART.md
    echo   - 迁移说明: type PLAYWRIGHT_MIGRATION.md
    echo.
) else (
    echo.
    echo ==================================
    echo   × 测试失败
    echo ==================================
    echo.
    echo 请运行以下命令进行调试:
    echo   python test_playwright_debug.py
    echo.
    pause
    exit /b 1
)

pause

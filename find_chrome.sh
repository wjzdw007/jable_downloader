#!/bin/bash
# 查找系统中已安装的 Chrome/Chromium

echo "======================================"
echo "查找系统中的 Chrome/Chromium"
echo "======================================"
echo ""

# 常见的 Chrome/Chromium 路径
CHROME_PATHS=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium"
    "/usr/bin/chromium-browser"
    "/snap/bin/chromium"
    "/opt/google/chrome/chrome"
    "/opt/google/chrome/google-chrome"
)

echo "🔍 搜索 Chrome/Chromium..."
echo ""

FOUND_CHROME=""

for path in "${CHROME_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "✓ 找到: $path"

        # 获取版本号
        VERSION=$("$path" --version 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "  版本: $VERSION"
            FOUND_CHROME="$path"
        fi
        echo ""
    fi
done

if [ -z "$FOUND_CHROME" ]; then
    echo "❌ 未找到系统 Chrome/Chromium"
    echo ""
    echo "安装方法："
    echo "  Ubuntu/Debian:"
    echo "    sudo apt-get update"
    echo "    sudo apt-get install -y chromium-browser"
    echo "  或者："
    echo "    sudo apt-get install -y google-chrome-stable"
    echo ""
else
    echo "======================================"
    echo "✓ 推荐使用: $FOUND_CHROME"
    echo "======================================"
    echo ""
    echo "将此路径添加到 config.json:"
    echo "{"
    echo "  \"chrome_path\": \"$FOUND_CHROME\""
    echo "}"
fi

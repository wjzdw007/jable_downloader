#!/bin/bash
# 切换到最原始的简单模式

echo "======================================"
echo "切换到最原始的简单模式"
echo "======================================"
echo ""

# 备份当前的 utils.py
if [ -f "utils.py" ] && [ ! -f "utils_advanced.py" ]; then
    echo "📦 备份当前的 utils.py -> utils_advanced.py"
    cp utils.py utils_advanced.py
fi

# 使用简单版本
echo "🔄 使用最原始的简单版本..."
cp utils_simple.py utils.py

echo ""
echo "✅ 已切换到简单模式！"
echo ""
echo "简单模式特点："
echo "  - 不设置任何额外的 HTTP 头部"
echo "  - 不注入任何 JavaScript"
echo "  - 不做任何浏览器指纹伪装"
echo "  - 完全像真实浏览器一样运行"
echo ""
echo "现在可以测试了："
echo "  xvfb-run -a python3 test_browser_simulation.py"
echo ""
echo "如果要切换回高级模式："
echo "  cp utils_advanced.py utils.py"
echo ""

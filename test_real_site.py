#!/usr/bin/env python3
# coding: utf-8

"""
真实网站测试 - 使用实际的 jable.tv 网站测试
"""

import sys
from utils import get_response_from_playwright

def test_jable_homepage():
    """测试访问 jable.tv 主页"""
    print("=" * 60)
    print("真实网站测试 - jable.tv")
    print("=" * 60)
    print()

    test_url = "https://jable.tv/"

    print(f"[测试] 访问 jable.tv 主页")
    print(f"URL: {test_url}")
    print()

    try:
        print("正在使用 Playwright 获取页面...")
        html = get_response_from_playwright(test_url)

        if html and len(html) > 0:
            print(f"✓ 成功获取页面内容")
            print(f"✓ HTML 长度: {len(html)} 字符")
            print()

            # 检查关键元素
            checks = [
                ("site-header", "网站头部"),
                ("jable.tv", "网站名称"),
                ("models", "模特页面"),
                ("videos", "视频"),
            ]

            print("检查页面关键元素:")
            for keyword, desc in checks:
                if keyword in html:
                    print(f"  ✓ {desc} ({keyword}) - 找到")
                else:
                    print(f"  ✗ {desc} ({keyword}) - 未找到")

            print()

            # 显示HTML片段（前500字符）
            print("HTML 预览（前500字符）:")
            print("-" * 60)
            print(html[:500])
            print("-" * 60)

            return True
        else:
            print("✗ 未获取到页面内容")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_jable_homepage()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# coding: utf-8

"""
测试 Playwright 实现是否正常工作
"""

import sys
import config
from utils import get_response_from_playwright

def test_playwright():
    """测试 Playwright 获取网页"""

    # 使用一个简单的测试URL
    test_url = "https://example.com"

    print(f"正在测试 Playwright 访问: {test_url}")
    print("-" * 60)

    try:
        html = get_response_from_playwright(test_url)

        if html and len(html) > 0:
            print("✓ Playwright 测试成功!")
            print(f"✓ 获取到的HTML长度: {len(html)} 字符")
            print(f"✓ HTML预览 (前200字符):")
            print("-" * 60)
            print(html[:200])
            print("-" * 60)
            return True
        else:
            print("✗ 测试失败: 未获取到HTML内容")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_playwright()
    sys.exit(0 if success else 1)

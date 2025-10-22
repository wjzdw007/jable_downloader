#!/usr/bin/env python3
# coding: utf-8

"""
调试 Playwright 问题
"""

import sys
import traceback

def test_basic_playwright():
    """测试基础 Playwright 功能"""
    print("=" * 60)
    print("测试 1: 基础 Playwright 导入")
    print("=" * 60)

    try:
        from playwright.sync_api import sync_playwright
        print("✓ Playwright 导入成功")
    except Exception as e:
        print(f"✗ Playwright 导入失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("测试 2: 启动浏览器 (使用最简配置)")
    print("=" * 60)

    try:
        with sync_playwright() as p:
            print("  - 正在启动 Chromium...")
            browser = p.chromium.launch(
                headless=True,
                timeout=60000  # 增加超时时间
            )
            print("  ✓ 浏览器启动成功")

            print("  - 创建上下文...")
            context = browser.new_context()
            print("  ✓ 上下文创建成功")

            print("  - 创建页面...")
            page = context.new_page()
            print("  ✓ 页面创建成功")

            print("  - 访问 example.com...")
            page.goto("https://example.com", timeout=30000)
            print("  ✓ 页面访问成功")

            title = page.title()
            print(f"  ✓ 页面标题: {title}")

            html = page.content()
            print(f"  ✓ HTML长度: {len(html)} 字符")

            browser.close()
            print("  ✓ 浏览器关闭成功")

        print("\n✓ 所有测试通过!")
        return True

    except Exception as e:
        print(f"\n✗ 测试失败:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        print("\n完整堆栈:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_playwright()
    sys.exit(0 if success else 1)

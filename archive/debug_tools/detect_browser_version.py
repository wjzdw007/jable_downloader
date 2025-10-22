#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测 Playwright 实际使用的浏览器版本
"""

from playwright.sync_api import sync_playwright
import re

def detect_browser_version():
    """检测 Playwright 的 Chromium 版本"""

    print("="*70)
    print("🔍 检测 Playwright Chromium 版本")
    print("="*70)
    print()

    with sync_playwright() as p:
        # 启动浏览器
        print("🚀 启动浏览器...")
        browser = p.chromium.launch(headless=True)

        # 获取版本信息
        version = browser.version
        print(f"✅ Playwright Chromium 版本: {version}")
        print()

        # 创建页面并获取 User-Agent
        context = browser.new_context()
        page = context.new_page()

        # 访问一个测试页面来查看实际的请求头部
        page.goto("about:blank")

        # 获取真实的 navigator 信息
        user_agent = page.evaluate("() => navigator.userAgent")
        app_version = page.evaluate("() => navigator.appVersion")
        nav_platform = page.evaluate("() => navigator.platform")

        print("-"*70)
        print("🌐 真实的 navigator 信息：")
        print("-"*70)
        print()
        print(f"navigator.userAgent:")
        print(f"  {user_agent}")
        print()
        print(f"navigator.platform:")
        print(f"  {nav_platform}")
        print()
        print(f"navigator.appVersion:")
        print(f"  {app_version}")
        print()

        # 提取 Chrome 版本号
        chrome_match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', user_agent)
        if chrome_match:
            chrome_version = chrome_match.group(1)
            chrome_major = chrome_match.group(1).split('.')[0]
            print(f"🔢 检测到的 Chrome 版本:")
            print(f"  完整版本: {chrome_version}")
            print(f"  主版本号: {chrome_major}")
        else:
            print("⚠️  未能检测到 Chrome 版本")

        browser.close()

    print()
    print("="*70)
    print("💡 建议")
    print("="*70)
    print()

    if chrome_match:
        print(f"✅ 应该在 User-Agent 中使用 Chrome/{chrome_version}")
        print()
        print("当前 utils.py 中硬编码的版本:")
        print("  Chrome/131.0.0.0")
        print()
        print("❌ 版本不匹配可能导致 Cloudflare 检测！")
        print()
        print("解决方案：")
        print("  1. 让 User-Agent 使用真实的浏览器版本号")
        print("  2. 或者不要覆盖 User-Agent，使用浏览器默认的")
        print()

        # 生成正确的 User-Agent
        import platform
        system = platform.system()

        if system == 'Linux':
            correct_ua = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        elif system == 'Darwin':
            correct_ua = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        elif system == 'Windows':
            correct_ua = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        else:
            correct_ua = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'

        print("✅ 正确的 User-Agent 应该是:")
        print(f"  {correct_ua}")
        print()


if __name__ == '__main__':
    detect_browser_version()

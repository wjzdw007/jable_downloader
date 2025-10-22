#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比测试：无头模式 vs 有头模式的 User-Agent 差异
"""

from playwright.sync_api import sync_playwright

def test_mode(headless, mode_name):
    """测试指定模式的 User-Agent"""

    print(f"\n{'='*70}")
    print(f"🔍 测试 {mode_name}")
    print(f"{'='*70}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context()
        page = context.new_page()
        page.goto("about:blank")

        # 获取 User-Agent
        user_agent = page.evaluate("() => navigator.userAgent")

        print(f"navigator.userAgent:")
        print(f"  {user_agent}")
        print()

        # 检查是否包含 "HeadlessChrome"
        if "HeadlessChrome" in user_agent:
            print("❌ 检测到 'HeadlessChrome' - Cloudflare 会识别为无头浏览器！")
        elif "Chrome" in user_agent:
            print("✅ 正常的 Chrome User-Agent - 看起来像真实浏览器")

        browser.close()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 无头模式 vs 有头模式 User-Agent 对比测试")
    print("="*70)

    # 测试无头模式
    test_mode(headless=True, mode_name="无头模式 (headless=True)")

    # 测试有头模式
    test_mode(headless=False, mode_name="有头模式 (headless=False)")

    print("\n" + "="*70)
    print("📊 结论")
    print("="*70)
    print()
    print("无头模式:")
    print("  ❌ User-Agent 包含 'HeadlessChrome'")
    print("  ❌ Cloudflare 可以直接检测")
    print("  ❌ 必定被拦截")
    print()
    print("有头模式:")
    print("  ✅ User-Agent 只包含 'Chrome'（不包含 'Headless'）")
    print("  ✅ 看起来像真实的 Chrome 浏览器")
    print("  ✅ 更难被 Cloudflare 检测")
    print()
    print("💡 建议:")
    print("  1. 设置 config.json: \"playwright_headless\": false")
    print("  2. 在远程服务器使用: xvfb-run -a python3 ...")
    print("  3. Xvfb 提供虚拟显示，User-Agent 不会显示 'Headless'")
    print()

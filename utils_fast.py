#!/usr/bin/env python3
"""
优化版的页面获取工具
主要优化：
1. 复用浏览器实例
2. 禁用图片、CSS、字体等资源加载
3. 移除不必要的固定等待
4. 降低超时时间
5. 支持并发爬取
"""

import time
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional

import config

CONF = config.CONF

# 全局浏览器实例（复用）
_playwright = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None


def get_browser_instance():
    """
    获取或创建浏览器实例（复用）
    """
    global _playwright, _browser, _context

    if _browser is None:
        _playwright = sync_playwright().start()

        chrome_path = CONF.get('chrome_path', None)
        use_system_chrome = False

        if chrome_path:
            import os
            if os.path.exists(chrome_path):
                use_system_chrome = True
                print(f"  [Fast] ✓ 使用系统浏览器: {chrome_path}")
            else:
                print(f"  [Fast] ⚠️  chrome_path 路径不存在，使用 Playwright 自带浏览器")

        # 启动浏览器
        if use_system_chrome:
            _browser = _playwright.chromium.launch(
                headless=False,
                executable_path=chrome_path
            )
        else:
            _browser = _playwright.chromium.launch(headless=False)

        print(f"  [Fast] ✓ 浏览器已启动（将复用此实例）")

        # 创建上下文
        _context = _browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    return _browser, _context


def close_browser_instance():
    """
    关闭浏览器实例
    """
    global _playwright, _browser, _context

    if _context:
        _context.close()
        _context = None

    if _browser:
        _browser.close()
        _browser = None

    if _playwright:
        _playwright.stop()
        _playwright = None

    print("  [Fast] ✓ 浏览器已关闭")


def fast_requests_get(url: str, retry: int = 3) -> str:
    """
    快速获取页面内容（优化版）

    优化点：
    1. 复用浏览器实例
    2. 禁用图片、CSS、字体等资源
    3. 移除固定等待
    4. 降低超时时间

    Args:
        url: 页面 URL
        retry: 重试次数

    Returns:
        页面 HTML 内容
    """
    for attempt in range(1, retry + 1):
        try:
            # 获取浏览器实例（复用）
            browser, context = get_browser_instance()

            # 创建新页面
            page = context.new_page()

            # 禁用不必要的资源加载（图片、CSS、字体等）
            page.route("**/*", lambda route: (
                route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"]
                else route.continue_()
            ))

            if attempt == 1:
                print(f"  [Fast] 正在访问: {url}")

            # 使用 domcontentloaded 策略，30秒超时
            page.goto(url, wait_until='domcontentloaded', timeout=30000)

            if attempt == 1:
                print(f"  [Fast] ✓ 页面加载完成")

            # 移除固定等待 - 直接获取内容
            html = page.content()

            # 检查是否遇到 Cloudflare
            if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
                if attempt == 1:
                    print(f"  [Fast] 检测到 Cloudflare 验证，等待...")

                # 等待 Cloudflare 验证
                max_wait = 30  # 最多等待 30 秒
                for i in range(max_wait):
                    time.sleep(1)
                    html = page.content()

                    if 'Just a moment' not in html and 'Verify you are human' not in html and '請稍候' not in html:
                        print(f"  [Fast] ✓ Cloudflare 验证通过 ({i+1}秒)")
                        break

                    if (i + 1) % 10 == 0:
                        print(f"  [Fast] 仍在等待... ({i+1}/{max_wait}秒)")

            # 关闭页面（但保留浏览器）
            page.close()

            return html

        except Exception as e:
            print(f"  [Fast] ✗ 错误 (尝试 {attempt}/{retry}): {str(e)[:100]}")

            if attempt == retry:
                raise Exception(f"Fast request failed after {retry} attempts: {str(e)}")

            # 重试前等待
            wait_time = 3 * attempt
            print(f"  [Fast] 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

    raise Exception(f"Fast request failed: {url}")


# 测试对比
if __name__ == '__main__':
    import utils

    test_url = "https://jable.tv/hot/"

    print("=" * 80)
    print("性能对比测试")
    print("=" * 80)

    # 测试原版
    print("\n【测试1】原版 scrapingant_requests_get")
    print("-" * 80)
    start_time = time.time()
    html1 = utils.scrapingant_requests_get(test_url, retry=1)
    time1 = time.time() - start_time
    print(f"✓ 耗时: {time1:.2f} 秒")
    print(f"✓ HTML 长度: {len(html1)}")

    # 测试优化版（第一次，需要启动浏览器）
    print("\n【测试2】优化版 fast_requests_get（首次，需启动浏览器）")
    print("-" * 80)
    start_time = time.time()
    html2 = fast_requests_get(test_url, retry=1)
    time2 = time.time() - start_time
    print(f"✓ 耗时: {time2:.2f} 秒")
    print(f"✓ HTML 长度: {len(html2)}")

    # 测试优化版（第二次，复用浏览器）
    print("\n【测试3】优化版 fast_requests_get（第二次，复用浏览器）")
    print("-" * 80)
    test_url2 = "https://jable.tv/hot/2/"
    start_time = time.time()
    html3 = fast_requests_get(test_url2, retry=1)
    time3 = time.time() - start_time
    print(f"✓ 耗时: {time3:.2f} 秒")
    print(f"✓ HTML 长度: {len(html3)}")

    # 关闭浏览器
    close_browser_instance()

    # 总结
    print("\n" + "=" * 80)
    print("性能对比总结")
    print("=" * 80)
    print(f"原版首次请求: {time1:.2f} 秒")
    print(f"优化版首次请求: {time2:.2f} 秒  (提升: {(time1-time2)/time1*100:.1f}%)")
    print(f"优化版第二次请求: {time3:.2f} 秒  (提升: {(time1-time3)/time1*100:.1f}%)")
    print("=" * 80)

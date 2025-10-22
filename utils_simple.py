"""
最原始、最简单的 Playwright 使用方案
不做任何伪装、不设置头部、不注入 JavaScript
完全模拟真实用户使用浏览器的行为

使用方法：
1. 在 main.py 或其他文件中：
   from utils_simple import get_response_from_playwright_simple as get_response_from_playwright

2. 或者直接替换 utils.py 中的函数
"""

import json
import os
import time

from config import CONF


def get_response_from_playwright_simple(url, retry=3):
    """
    最原始的 Playwright 使用方案

    原则：
    - 不设置任何额外的 HTTP 头部
    - 不注入任何 JavaScript 代码
    - 不做任何浏览器指纹伪装
    - 不强制设置 User-Agent
    - 让浏览器完全按照默认行为运行
    - 唯一做的：使用系统浏览器（如果配置了）

    Args:
        url: 目标 URL
        retry: 重试次数

    Returns:
        str: 网页 HTML 内容
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    proxy = CONF.get('proxies', {}).get('http', None)
    headless_mode = CONF.get('playwright_headless', True)
    system_chrome_path = CONF.get('chrome_path', None)

    # Cookie 文件
    cookie_file = '.jable_cookies.json'

    for attempt in range(1, retry + 1):
        try:
            with sync_playwright() as p:
                # 最简单的启动配置
                launch_options = {
                    'headless': headless_mode,
                }

                # 如果配置了系统浏览器，使用系统浏览器
                if system_chrome_path and os.path.exists(system_chrome_path):
                    launch_options['executable_path'] = system_chrome_path
                    if attempt == 1:
                        print(f"  [Simple] 使用系统浏览器: {system_chrome_path}")

                # 启动浏览器
                if attempt == 1:
                    mode_text = "无头模式" if headless_mode else "有头模式"
                    print(f"  [Simple] 启动浏览器 ({mode_text})...")
                    print(f"  [Simple] 原始模式：不做任何伪装")

                browser = p.chromium.launch(**launch_options)

                if attempt == 1:
                    print(f"  [Simple] 浏览器版本: {browser.version}")

                try:
                    # 最简单的上下文配置 - 只配置代理
                    context_options = {}

                    if proxy:
                        context_options['proxy'] = {'server': proxy}
                        if attempt == 1:
                            print(f"  [Simple] 使用代理: {proxy}")

                    context = browser.new_context(**context_options)

                    # 加载之前保存的 Cookie（这是唯一的优化）
                    if os.path.exists(cookie_file):
                        try:
                            with open(cookie_file, 'r', encoding='utf-8') as f:
                                cookies = json.load(f)
                                if cookies:
                                    context.add_cookies(cookies)
                                    if attempt == 1:
                                        print(f"  [Simple] 加载了 {len(cookies)} 个 Cookie")
                        except Exception as e:
                            if attempt == 1:
                                print(f"  [Simple] Cookie 加载失败: {str(e)[:50]}")

                    # 创建页面
                    page = context.new_page()

                    # 直接访问 URL - 不做任何额外操作
                    if attempt == 1:
                        print(f"  [Simple] 正在访问: {url}")

                    page.goto(url, timeout=60000)

                    # 等待页面加载完成
                    if attempt == 1:
                        print(f"  [Simple] 页面加载完成")

                    # 简单等待一下确保内容加载
                    page.wait_for_timeout(3000)

                    # 获取页面内容
                    html = page.content()

                    # 保存 Cookie
                    try:
                        current_cookies = context.cookies()
                        if current_cookies:
                            with open(cookie_file, 'w', encoding='utf-8') as f:
                                json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                            if attempt == 1:
                                print(f"  [Simple] 保存了 {len(current_cookies)} 个 Cookie")
                    except Exception as e:
                        if attempt == 1:
                            print(f"  [Simple] Cookie 保存失败: {str(e)[:50]}")

                    # 检查是否遇到 Cloudflare
                    if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
                        if attempt == 1:
                            print(f"  [Simple] 检测到 Cloudflare 验证页面")

                        # 简单等待 - 不做任何模拟
                        if attempt == 1:
                            print(f"  [Simple] 等待 Cloudflare 自动验证...")

                        max_wait = 30
                        for i in range(max_wait):
                            page.wait_for_timeout(1000)
                            html = page.content()

                            if 'Just a moment' not in html and 'Verify you are human' not in html and '請稍候' not in html:
                                print(f"  [Simple] ✓ Cloudflare 验证通过 (等待 {i+1} 秒)")

                                # 保存验证后的 Cookie
                                try:
                                    current_cookies = context.cookies()
                                    with open(cookie_file, 'w', encoding='utf-8') as f:
                                        json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                                except:
                                    pass
                                break

                            if (i + 1) % 10 == 0:
                                print(f"  [Simple] 仍在等待... ({i+1}/{max_wait}秒)")

                        # 最后再取一次内容
                        html = page.content()

                    if attempt == 1:
                        print(f"  [Simple] 完成！HTML 长度: {len(html)}")

                    return html

                finally:
                    browser.close()

        except Exception as e:
            print(f"  [Simple] 错误 (尝试 {attempt}/{retry}): {str(e)[:200]}")
            if attempt == retry:
                raise Exception(f"Simple request failed after {retry} attempts: {str(e)}")
            time.sleep(3 * attempt)

    raise Exception(f"Simple request failed: {url}")


# 兼容性：提供和原来一样的函数名
get_response_from_playwright = get_response_from_playwright_simple


if __name__ == '__main__':
    # 测试
    print("测试最原始的 Playwright 方案")
    print()

    test_url = "https://jable.tv/models/851cf1602f37c2611917b675f2d432c7/"

    try:
        html = get_response_from_playwright_simple(test_url)

        print()
        print("="*60)
        print("测试结果")
        print("="*60)

        if 'Just a moment' in html or 'Verify you are human' in html:
            print("❌ 仍然遇到 Cloudflare 验证")
        else:
            print("✅ 成功获取页面内容！")
            print(f"HTML 长度: {len(html)}")

            # 检查是否有演员名称
            if 'h3-md mb-1' in html or 'video-img' in html:
                print("✓ 页面包含正常内容")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

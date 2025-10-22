"""
使用 playwright-stealth 的增强版本
更强大的反检测能力

安装：pip3 install playwright-stealth

使用：
from utils_stealth import get_response_from_playwright_stealth
html = get_response_from_playwright_stealth(url)
"""

import json
import os
from pathlib import Path
import re
import requests
import time
from urllib import parse

from config import CONF

def get_response_from_playwright_stealth(url, retry=3):
    """
    使用 playwright-stealth 获取网页内容
    提供更强大的反检测能力
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    from playwright_stealth import stealth_sync
    import random
    import platform

    proxy = CONF.get('proxies', {}).get('http', None)
    headless_mode = CONF.get('playwright_headless', True)
    cookie_file = '.jable_cookies.json'

    # 自动检测操作系统
    system = platform.system()
    if system == 'Linux':
        platform_name = 'Linux'
        nav_platform = 'Linux x86_64'
    elif system == 'Darwin':
        platform_name = 'macOS'
        nav_platform = 'MacIntel'
    elif system == 'Windows':
        platform_name = 'Windows'
        nav_platform = 'Win32'
    else:
        platform_name = 'Linux'
        nav_platform = 'Linux x86_64'

    for attempt in range(1, retry + 1):
        try:
            with sync_playwright() as p:
                # 启动浏览器
                launch_options = {
                    'headless': headless_mode,
                    'timeout': 60000,
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-setuid-sandbox',
                        '--no-zygote',
                    ]
                }

                if attempt == 1:
                    mode_text = "无头模式" if headless_mode else "有头模式（可见窗口）"
                    print(f"  [Stealth] 启动浏览器 ({mode_text})...")
                    print(f"  [Stealth] 使用 playwright-stealth 反检测库")
                    print(f"  [Stealth] 操作系统: {system} → {platform_name}")

                browser = p.chromium.launch(**launch_options)
                browser_version = browser.version

                if attempt == 1:
                    print(f"  [Stealth] 浏览器版本: {browser_version}")

                try:
                    # 随机视口
                    viewport_width = random.randint(1366, 1920)
                    viewport_height = random.randint(768, 1080)

                    # 构建 User-Agent
                    if system == 'Linux':
                        user_agent = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
                    elif system == 'Darwin':
                        user_agent = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
                    elif system == 'Windows':
                        user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
                    else:
                        user_agent = f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'

                    # 创建浏览器上下文
                    context_options = {
                        'user_agent': user_agent,
                        'viewport': {'width': viewport_width, 'height': viewport_height},
                        'ignore_https_errors': True,
                        'locale': 'zh-TW',
                        'timezone_id': 'Asia/Taipei',
                        'device_scale_factor': 1,
                        'java_script_enabled': True,
                    }

                    if proxy:
                        context_options['proxy'] = {'server': proxy}

                    context = browser.new_context(**context_options)

                    # 加载 Cookie
                    if os.path.exists(cookie_file):
                        try:
                            with open(cookie_file, 'r', encoding='utf-8') as f:
                                cookies = json.load(f)
                                if cookies:
                                    context.add_cookies(cookies)
                                    if attempt == 1:
                                        print(f"  [Stealth] 加载了 {len(cookies)} 个已保存的 Cookie")
                        except Exception as e:
                            if attempt == 1:
                                print(f"  [Stealth] Cookie 加载失败: {str(e)[:50]}")

                    # 设置额外头部
                    major_version = browser_version.split('.')[0]
                    extra_headers = {
                        'sec-ch-ua': f'"Chromium";v="{major_version}", "Not_A Brand";v="24"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': f'"{platform_name}"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'none',
                        'sec-fetch-user': '?1',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'upgrade-insecure-requests': '1',
                        'dnt': '1',
                    }
                    context.set_extra_http_headers(extra_headers)

                    # 创建页面
                    page = context.new_page()

                    # ⭐ 关键：应用 playwright-stealth
                    stealth_sync(page)

                    if attempt == 1:
                        print(f"  [Stealth] ✓ 已应用 stealth 插件（隐藏所有自动化特征）")

                    # 访问页面
                    if attempt == 1:
                        print(f"  [Stealth] 正在访问页面...")

                    page.goto(url, timeout=45000, wait_until='domcontentloaded')

                    # 模拟用户行为
                    try:
                        for _ in range(random.randint(2, 4)):
                            x = random.randint(100, viewport_width - 100)
                            y = random.randint(100, viewport_height - 100)
                            page.mouse.move(x, y)
                            page.wait_for_timeout(random.randint(100, 300))
                    except:
                        pass

                    # 等待关键元素
                    try:
                        page.wait_for_selector('#site-header', timeout=5000)
                    except PlaywrightTimeoutError:
                        pass

                    # 等待演员名称
                    if '/models/' in url:
                        try:
                            page.wait_for_selector('h2.h3-md.mb-1', timeout=5000)
                        except PlaywrightTimeoutError:
                            page.wait_for_timeout(2000)

                    # 获取内容
                    html = page.content()

                    # 保存 Cookie
                    try:
                        current_cookies = context.cookies()
                        if current_cookies:
                            with open(cookie_file, 'w', encoding='utf-8') as f:
                                json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                            if attempt == 1:
                                print(f"  [Stealth] 保存了 {len(current_cookies)} 个 Cookie")
                    except Exception as e:
                        if attempt == 1:
                            print(f"  [Stealth] Cookie 保存失败: {str(e)[:50]}")

                    # 检查 Cloudflare
                    if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
                        if attempt == 1:
                            print("  [Stealth] 检测到 Cloudflare 验证，等待通过...")

                        # 用户行为模拟
                        try:
                            for _ in range(random.randint(1, 3)):
                                page.mouse.wheel(0, random.randint(100, 300))
                                page.wait_for_timeout(random.randint(500, 1000))
                        except:
                            pass

                        # 等待验证
                        max_wait_time = 60
                        waited = 0
                        check_interval = 3

                        while waited < max_wait_time:
                            page.wait_for_timeout(check_interval * 1000)
                            waited += check_interval

                            html = page.content()

                            if 'Just a moment' not in html and 'Verify you are human' not in html and '請稍候' not in html:
                                print(f"  [Stealth] ✓ Cloudflare 验证通过 (等待 {waited}秒)")

                                # 保存验证后的 Cookie
                                try:
                                    current_cookies = context.cookies()
                                    if current_cookies:
                                        with open(cookie_file, 'w', encoding='utf-8') as f:
                                            json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                                        print(f"  [Stealth] ✓ 已保存验证后的 {len(current_cookies)} 个 Cookie")
                                except Exception as e:
                                    print(f"  [Stealth] Cookie 保存失败: {str(e)[:50]}")
                                break

                            if waited % 9 == 0:
                                print(f"  [Stealth] 仍在验证中... (已等待 {waited}秒)")

                        # 最终检查
                        html = page.content()
                        if 'Just a moment' in html or 'Verify you are human' in html:
                            print("  [Stealth] ⚠ Cloudflare 验证超时")
                            if attempt < retry:
                                print("  [Stealth] 将在下次尝试中重试...")
                                continue

                    if attempt == 1:
                        print("  [Stealth] 页面信息获取完成！")

                    return html

                finally:
                    browser.close()

        except Exception as e:
            print(f"  [Stealth] 请求失败 (尝试 {attempt}/{retry}): {str(e)[:200]}")
            if attempt == retry:
                raise Exception(f"Stealth request failed after {retry} attempts: {str(e)[:200]}")
            time.sleep(5 * attempt)

    raise Exception(f"Stealth request failed: {url}")

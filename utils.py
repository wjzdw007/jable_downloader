import json
import os
from pathlib import Path
import re
import requests
import time
from urllib import parse

from config import CONF

video_index_cache_filename = "./jable_index_cache.json"

HEADERS = CONF.get("headers")

logged = False


def get_video_ids_map_from_cache():
    cache = {}
    if os.path.exists(video_index_cache_filename):
        with open(video_index_cache_filename, 'r', encoding='utf-8') as f:
            cache = json.load(f)

    return cache


def _add_proxy(query_param, retry_index, ignore_proxy):
    if not ignore_proxy or retry_index > 1:
        proxies_config = CONF.get('proxies', None)
        if proxies_config and 'http' in proxies_config and 'https' in proxies_config:
            query_param['proxies'] = proxies_config


def requests_with_retry(url, headers=HEADERS, timeout=20, retry=5, ignore_proxy=False):
    query_param = {
        'headers': headers,
        'timeout': timeout
    }

    for i in range(1, retry+1):
        try:
            _add_proxy(query_param, i, ignore_proxy)
            response = requests.get(url, **query_param)
        except Exception as e:
            if i == 1 and ignore_proxy:
                continue
            if i < retry:
                wait_time = min(10 * i, 30)  # 最多等待30秒
                print(f"    ⚠ 请求失败 (尝试 {i}/{retry}): {str(e)[:80]}")
                print(f"    ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"    ✗ 请求最终失败: {str(e)[:80]}")
            continue

        if str(response.status_code).startswith('2'):
            return response
        else:
            if i < retry:
                wait_time = min(10 * i, 30)  # 最多等待30秒
                print(f"    ⚠ HTTP错误 (尝试 {i}/{retry}): 状态码 {response.status_code}")
                print(f"    ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            continue
    raise Exception("%s exceed max retry time %s." % (url, retry))


def scrapingant_requests_get(url, retry=5) -> str:
    global logged
    if not CONF.get('sa_token'):
        if not logged:
            logged = True
            print("You need to go to https://app.scrapingant.com/ website to\n apply for a token and fill it in the sa_token field")
            print("Use local Playwright as a replacement.\n")
        print("  [Playwright] 正在获取视频页面信息...")
        return get_response_from_playwright(url)
        exit(1)

    query_param = {
        "timeout": 180
    }

    sa_api = 'https://api.scrapingant.com/v2/general'
    qParams = {'url': url, 'x-api-key': CONF.get('sa_token'), 'browser': 'false'}
    if CONF.get('sa_mode', None) == 'browser':
        qParams['browser'] = 'true'
    reqUrl = f'{sa_api}?{parse.urlencode(qParams)}'

    proxies_config = CONF.get('proxies', None)

    if proxies_config and 'http' in proxies_config and 'https' in proxies_config:
        query_param['proxies'] = proxies_config

    for i in range(1, retry+1):
        try:
            response = requests.get(reqUrl, **query_param)
        except Exception as e:
            if i == retry:
                print("Unexpected Error: %s" % e)
            time.sleep(120 * i)
            continue

        if str(response.status_code).startswith('2'):
            return response.text
        else:
            time.sleep(120 * i)
            continue
    raise Exception("%s exceed max retry time %s" % (url, retry))


def update_video_ids_cache(data):
    with open(video_index_cache_filename, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def get_local_video_list(path="./"):
    re_extractor = re.compile(r"[a-zA-Z0-9]{2,}-\d{3,}")

    def extract_movie_id(full_name):
        foo = re_extractor.search(full_name)
        movie_id = None
        if foo:
            movie_id = foo.group(0).lower()
        return movie_id

    result = {extract_movie_id(foo.name) for foo in list(Path(path).rglob("*.mp4"))}
    if None in result:
        result.remove(None)

    return result


def get_response_from_playwright(url, retry=3):
    """
    使用 Playwright 获取网页内容，替代 chromedp
    包含完整的浏览器头部模拟和 Cookie 持久化

    Args:
        url: 目标URL
        retry: 重试次数

    Returns:
        str: 网页HTML内容
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    import random
    import platform

    proxy = CONF.get('proxies', {}).get('http', None)

    # 自动检测操作系统并适配平台名称
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

    # 读取配置：是否使用无头模式
    headless_mode = CONF.get('playwright_headless', True)

    # Cookie 持久化文件
    cookie_file = '.jable_cookies.json'

    for attempt in range(1, retry + 1):
        try:
            with sync_playwright() as p:
                # 配置浏览器启动参数
                # 添加参数来降低被 Cloudflare 检测的风险
                launch_options = {
                    'headless': headless_mode,  # 从配置读取
                    'timeout': 60000,
                    'args': [
                        '--disable-blink-features=AutomationControlled',  # 禁用自动化特征
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',  # 禁用同源策略限制
                        '--disable-features=IsolateOrigins,site-per-process',
                    ]
                }

                # 启动浏览器
                if attempt == 1:
                    mode_text = "无头模式" if headless_mode else "有头模式（可见窗口）"
                    print(f"  [Playwright] 启动浏览器 ({mode_text})...")
                    print(f"  [Playwright] 检测到操作系统: {system} → 使用 {platform_name} 平台特征")
                browser = p.chromium.launch(**launch_options)
                if attempt == 1:
                    print("  [Playwright] 浏览器启动成功，正在加载页面...")

                try:
                    # 随机视口大小（模拟不同用户的屏幕）
                    viewport_width = random.randint(1366, 1920)
                    viewport_height = random.randint(768, 1080)

                    # 创建浏览器上下文
                    # 注意：不设置 user_agent，让浏览器使用默认的（版本号会自动匹配）
                    context_options = {
                        'viewport': {'width': viewport_width, 'height': viewport_height},
                        'ignore_https_errors': True,
                        # 添加额外的浏览器特征来模拟真实用户
                        'locale': 'zh-TW',  # 台湾中文
                        'timezone_id': 'Asia/Taipei',
                        # 设置设备缩放因子
                        'device_scale_factor': 1,
                        # 启用 JavaScript
                        'java_script_enabled': True,
                    }

                    # 配置代理
                    if proxy:
                        context_options['proxy'] = {'server': proxy}

                    context = browser.new_context(**context_options)

                    # 加载之前保存的 Cookie（如果存在）
                    if os.path.exists(cookie_file):
                        try:
                            with open(cookie_file, 'r', encoding='utf-8') as f:
                                cookies = json.load(f)
                                if cookies:
                                    context.add_cookies(cookies)
                                    if attempt == 1:
                                        print(f"  [Playwright] 加载了 {len(cookies)} 个已保存的 Cookie")
                        except Exception as e:
                            if attempt == 1:
                                print(f"  [Playwright] Cookie 加载失败: {str(e)[:50]}")

                    # 设置额外的 HTTP 头部
                    # 注意：不设置 sec-ch-ua（包含版本号），让浏览器使用真实的版本
                    # 只设置与版本无关的通用头部
                    extra_headers = {
                        # Sec-Ch-Ua 系列（只设置平台，不设置版本号）
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': f'"{platform_name}"',  # 自动适配：Linux/macOS/Windows
                        # Sec-Fetch 系列（Fetch Metadata）
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'none',
                        'sec-fetch-user': '?1',
                        # 其他标准头部
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'upgrade-insecure-requests': '1',
                        'dnt': '1',  # Do Not Track
                    }
                    context.set_extra_http_headers(extra_headers)

                    # 添加初始化脚本，隐藏 webdriver 特征和其他自动化痕迹
                    context.add_init_script(f"""
                        // 隐藏 webdriver
                        Object.defineProperty(navigator, 'webdriver', {{
                            get: () => undefined
                        }});

                        // 设置正确的 platform（与 HTTP 头部一致）
                        Object.defineProperty(navigator, 'platform', {{
                            get: () => '{nav_platform}'
                        }});

                        // 设置硬件信息（更真实）
                        Object.defineProperty(navigator, 'hardwareConcurrency', {{
                            get: () => 8  // 模拟 8 核 CPU
                        }});

                        Object.defineProperty(navigator, 'deviceMemory', {{
                            get: () => 8  // 模拟 8GB 内存
                        }});

                        // 伪造 plugins
                        Object.defineProperty(navigator, 'plugins', {{
                            get: () => [1, 2, 3, 4, 5]
                        }});

                        // 设置语言
                        Object.defineProperty(navigator, 'languages', {{
                            get: () => ['zh-TW', 'zh', 'en-US', 'en']
                        }});

                        // 伪造 Chrome 对象
                        window.chrome = {{
                            runtime: {{}},
                            loadTimes: function() {{}},
                            csi: function() {{}},
                            app: {{}}
                        }};

                        // 隐藏自动化相关属性
                        Object.defineProperty(navigator, 'permissions', {{
                            get: () => ({{
                                query: () => Promise.resolve({{ state: 'granted' }})
                            }})
                        }});

                        // 伪造 battery API
                        Object.defineProperty(navigator, 'getBattery', {{
                            get: () => () => Promise.resolve({{
                                charging: true,
                                chargingTime: 0,
                                dischargingTime: Infinity,
                                level: 1
                            }})
                        }});

                        // 覆盖 toString 方法避免检测
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (parameters) => (
                            parameters.name === 'notifications' ?
                                Promise.resolve({{ state: Notification.permission }}) :
                                originalQuery(parameters)
                        );

                        // 伪造 connection
                        Object.defineProperty(navigator, 'connection', {{
                            get: () => ({{
                                effectiveType: '4g',
                                rtt: 50,
                                downlink: 10,
                                saveData: false
                            }})
                        }});

                        // 隐藏 Playwright 特征
                        delete navigator.__proto__.webdriver;
                    """)

                    # 创建新页面
                    page = context.new_page()

                    # 访问目标URL - 使用 domcontentloaded，不等待所有网络请求
                    # Cloudflare 页面会持续发送请求，networkidle 会超时
                    page.goto(url, timeout=45000, wait_until='domcontentloaded')
                    if attempt == 1:
                        print("  [Playwright] 页面加载完成，正在解析...")

                    # 模拟真实用户行为 - 随机移动鼠标
                    try:
                        # 随机移动鼠标到几个位置
                        for _ in range(random.randint(2, 4)):
                            x = random.randint(100, viewport_width - 100)
                            y = random.randint(100, viewport_height - 100)
                            page.mouse.move(x, y)
                            page.wait_for_timeout(random.randint(100, 300))
                    except:
                        pass

                    # 等待关键元素加载
                    try:
                        # 优先等待 #site-header
                        page.wait_for_selector('#site-header', timeout=5000)
                    except PlaywrightTimeoutError:
                        pass

                    # 额外等待确保动态内容加载
                    # 对于演员页面，等待演员名称元素
                    if '/models/' in url:
                        try:
                            # 等待演员名称加载
                            page.wait_for_selector('h2.h3-md.mb-1', timeout=5000)
                        except PlaywrightTimeoutError:
                            # 如果还是没有，再等待一下
                            page.wait_for_timeout(2000)

                    # 对于视频页面，等待视频信息加载
                    elif '/videos/' in url:
                        try:
                            page.wait_for_selector('.video-detail', timeout=5000)
                        except PlaywrightTimeoutError:
                            page.wait_for_timeout(1000)

                    # 其他页面，短暂等待确保动态内容渲染
                    else:
                        page.wait_for_timeout(1000)

                    # 获取页面内容
                    html = page.content()

                    # 保存 Cookie 供下次使用
                    try:
                        current_cookies = context.cookies()
                        if current_cookies:
                            with open(cookie_file, 'w', encoding='utf-8') as f:
                                json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                            if attempt == 1:
                                print(f"  [Playwright] 保存了 {len(current_cookies)} 个 Cookie 供下次使用")
                    except Exception as e:
                        if attempt == 1:
                            print(f"  [Playwright] Cookie 保存失败: {str(e)[:50]}")

                    # 检查是否遇到 Cloudflare 验证页面
                    if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html or '請完成以下操作' in html:
                        if attempt == 1:
                            print("  [Playwright] 检测到 Cloudflare 验证，等待通过...")

                        # 模拟人类等待 - 随机滚动和鼠标移动
                        try:
                            # 随机滚动页面
                            for _ in range(random.randint(1, 3)):
                                page.mouse.wheel(0, random.randint(100, 300))
                                page.wait_for_timeout(random.randint(500, 1000))

                            # 随机移动鼠标
                            for _ in range(random.randint(2, 4)):
                                x = random.randint(200, viewport_width - 200)
                                y = random.randint(200, viewport_height - 200)
                                page.mouse.move(x, y)
                                page.wait_for_timeout(random.randint(200, 500))
                        except:
                            pass

                        # 等待 Cloudflare 自动验证通过
                        max_wait_time = 60  # 最多等待 60 秒（增加以应对更复杂的验证）
                        waited = 0
                        check_interval = 3  # 每 3 秒检查一次

                        while waited < max_wait_time:
                            page.wait_for_timeout(check_interval * 1000)
                            waited += check_interval

                            html = page.content()

                            # 检查是否通过验证
                            if 'Just a moment' not in html and 'Verify you are human' not in html and '請稍候' not in html:
                                print("  [Playwright] ✓ Cloudflare 验证通过 (等待 {}秒)".format(waited))
                                # 验证通过后，立即保存新的 Cookie
                                try:
                                    current_cookies = context.cookies()
                                    if current_cookies:
                                        with open(cookie_file, 'w', encoding='utf-8') as f:
                                            json.dump(current_cookies, f, ensure_ascii=False, indent=2)
                                        print(f"  [Playwright] ✓ 已保存 Cloudflare 验证后的 {len(current_cookies)} 个 Cookie")
                                except Exception as e:
                                    print(f"  [Playwright] Cookie 保存失败: {str(e)[:50]}")
                                break

                            if waited % 9 == 0:  # 每 9 秒提示一次
                                print("  [Playwright] 仍在验证中... (已等待 {}秒)".format(waited))

                        # 最终检查
                        html = page.content()
                        if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
                            print("  [Playwright] ⚠ Cloudflare 验证超时，可能需要手动交互")
                            # 尝试重试
                            if attempt < retry:
                                print("  [Playwright] 将在下次尝试中重试...")
                                continue

                    if attempt == 1:
                        print("  [Playwright] 页面信息获取完成！")

                    return html

                finally:
                    # 确保浏览器被关闭
                    browser.close()

        except Exception as e:
            print(f"Playwright request failed (attempt {attempt}/{retry}): {str(e)[:200]}")
            if attempt == retry:
                raise Exception(f"Playwright request failed after {retry} attempts: {str(e)[:200]}")
            time.sleep(5 * attempt)  # 递增等待时间

    raise Exception(f"Playwright request failed: {url}")
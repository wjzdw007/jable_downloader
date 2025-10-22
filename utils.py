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

    Args:
        url: 目标URL
        retry: 重试次数

    Returns:
        str: 网页HTML内容
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    proxy = CONF.get('proxies', {}).get('http', None)
    user_agent = HEADERS.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    for attempt in range(1, retry + 1):
        try:
            with sync_playwright() as p:
                # 配置浏览器启动参数
                # 添加参数来降低被 Cloudflare 检测的风险
                launch_options = {
                    'headless': True,
                    'timeout': 60000,
                    'args': [
                        '--disable-blink-features=AutomationControlled',  # 禁用自动化特征
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                }

                # 启动浏览器
                if attempt == 1:
                    print("  [Playwright] 启动浏览器...")
                browser = p.chromium.launch(**launch_options)
                if attempt == 1:
                    print("  [Playwright] 浏览器启动成功，正在加载页面...")

                try:
                    # 创建浏览器上下文，配置代理和User-Agent
                    context_options = {
                        'user_agent': user_agent,
                        'viewport': {'width': 1920, 'height': 1080},
                        'ignore_https_errors': True,
                        # 添加额外的浏览器特征来模拟真实用户
                        'locale': 'zh-TW',  # 台湾中文
                        'timezone_id': 'Asia/Taipei',
                    }

                    # 配置代理
                    if proxy:
                        context_options['proxy'] = {'server': proxy}

                    context = browser.new_context(**context_options)

                    # 添加初始化脚本，隐藏 webdriver 特征
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-TW', 'zh', 'en-US', 'en']
                        });
                    """)

                    # 创建新页面
                    page = context.new_page()

                    # 访问目标URL - 使用 domcontentloaded，不等待所有网络请求
                    # Cloudflare 页面会持续发送请求，networkidle 会超时
                    page.goto(url, timeout=45000, wait_until='domcontentloaded')
                    if attempt == 1:
                        print("  [Playwright] 页面加载完成，正在解析...")

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

                    # 检查是否遇到 Cloudflare 验证页面
                    if 'Just a moment' in html or 'Verify you are human' in html or 'cloudflare' in html.lower():
                        if attempt == 1:
                            print("  [Playwright] 检测到 Cloudflare 验证，等待通过...")

                        # 等待更长时间让 Cloudflare 自动验证通过
                        page.wait_for_timeout(10000)  # 等待 10 秒

                        # 重新获取页面内容
                        html = page.content()

                        # 如果还是验证页面，再等一次
                        if 'Just a moment' in html or 'Verify you are human' in html:
                            print("  [Playwright] 仍在验证中，继续等待...")
                            page.wait_for_timeout(10000)  # 再等 10 秒
                            html = page.content()

                        # 检查是否通过验证
                        if 'Just a moment' not in html and 'Verify you are human' not in html:
                            print("  [Playwright] ✓ Cloudflare 验证通过")
                        else:
                            print("  [Playwright] ⚠ Cloudflare 验证可能失败，返回当前内容")

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
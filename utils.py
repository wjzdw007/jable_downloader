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
                launch_options = {
                    'headless': True,
                    'timeout': 60000,  # 增加浏览器启动超时时间
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
                    }

                    # 配置代理
                    if proxy:
                        context_options['proxy'] = {'server': proxy}

                    context = browser.new_context(**context_options)

                    # 创建新页面
                    page = context.new_page()

                    # 访问目标URL
                    page.goto(url, timeout=30000, wait_until='domcontentloaded')
                    if attempt == 1:
                        print("  [Playwright] 页面加载完成，正在解析...")

                    # 等待关键元素加载（与chromedp保持一致）
                    try:
                        page.wait_for_selector('#site-header', timeout=10000)
                    except PlaywrightTimeoutError:
                        # 某些页面可能没有这个元素，继续执行
                        pass

                    # 获取页面内容
                    html = page.content()
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
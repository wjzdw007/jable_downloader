"""
最原始、最简单的 Playwright 使用方案
不做任何伪装、不设置头部、不注入 JavaScript
不保存/加载 Cookie，完全独立的浏览器会话
完全模拟真实用户使用浏览器的行为

这是完整的 utils.py 替代版本，包含所有必要的函数
"""

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
                wait_time = min(10 * i, 30)
                print(f"    ⚠ 请求失败 (尝试 {i}/{retry}): {str(e)[:80]}")
                print(f"    ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"    ✗ 请求最终失败: {str(e)[:80]}")
            continue

        if str(response.status_code).startswith('2'):
            return response
        else:
            # 对于永久性错误（404, 410），不重试
            if response.status_code in [404, 410]:
                if response.status_code == 410:
                    print(f"    ✗ HTTP 410 Gone: 资源已过期或永久消失")
                    print(f"    💡 提示: 链接可能包含时间戳已过期，或服务器时间不准确")
                else:
                    print(f"    ✗ HTTP 404: 资源不存在")
                raise Exception(f"HTTP {response.status_code}: {url}")

            # 对于其他错误，重试
            if i < retry:
                wait_time = min(10 * i, 30)
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
    # 修正正则：匹配完整的视频 ID，包括所有后缀
    # 格式: 字母数字-数字-字母(可选)，例如 ssni-301-c, abc-123, xyz-456-d
    re_extractor = re.compile(r"[a-zA-Z0-9]{2,}-\d{3,}(?:-[a-zA-Z0-9]+)?")

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


def get_response_from_playwright_simple(url, retry=3):
    """
    最原始的 Playwright 使用方案

    原则：
    - 不设置任何额外的 HTTP 头部（除了 Referer 用于分页导航）
    - 不注入任何 JavaScript 代码
    - 不做任何浏览器指纹伪装
    - 不强制设置 User-Agent
    - 不保存/加载 Cookie，每次都是全新会话
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

                    # 设置基础的 Referer（如果 URL 有参数）
                    # 这样访问 ?from=1 时会带上 Referer，模拟真实的页面导航
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(url)
                    if parsed.query:  # 如果有查询参数
                        # 基础 URL（不带参数）作为 Referer
                        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        context.set_extra_http_headers({
                            'Referer': base_url
                        })
                        if attempt == 1:
                            print(f"  [Simple] 设置 Referer: {base_url}")

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

                    # 检查是否遇到 Cloudflare
                    if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
                        if attempt == 1:
                            print(f"  [Simple] 检测到 Cloudflare 验证页面")

                        # 简单等待 - 不做任何模拟
                        if attempt == 1:
                            print(f"  [Simple] 等待 Cloudflare 自动验证...")

                        max_wait = 60  # 增加到 60 秒
                        for i in range(max_wait):
                            page.wait_for_timeout(1000)
                            html = page.content()

                            if 'Just a moment' not in html and 'Verify you are human' not in html and '請稍候' not in html:
                                print(f"  [Simple] ✓ Cloudflare 验证通过 (等待 {i+1} 秒)")
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

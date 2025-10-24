#!/usr/bin/env python3
"""
测试：通过 Cloudflare 验证后，直接用 requests 访问
"""

import requests
from playwright.sync_api import sync_playwright
import time

def get_cloudflare_cookies(url):
    """
    使用 Playwright 通过 Cloudflare 验证，获取 cookies
    """
    print("1. 使用浏览器通过 Cloudflare 验证...")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 访问页面
        print(f"正在访问: {url}")
        page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # 等待 Cloudflare 验证
        html = page.content()
        if 'Just a moment' in html or '請稍候' in html:
            print("检测到 Cloudflare 验证，等待...")
            time.sleep(5)

        # 获取 cookies
        cookies = context.cookies()
        print(f"\n✓ 获取到 {len(cookies)} 个 cookies:")
        for cookie in cookies:
            print(f"  - {cookie['name']}: {cookie['value'][:50]}...")

        browser.close()

    return cookies


def test_requests_with_cookies(url, cookies):
    """
    使用 requests + cookies 直接访问
    """
    print("\n2. 使用 requests + cookies 直接访问")
    print("=" * 80)

    # 将 cookies 转换为 requests 格式
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(
            cookie['name'],
            cookie['value'],
            domain=cookie.get('domain', '.jable.tv')
        )

    # 设置 headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://jable.tv/',
    }

    print(f"正在访问: {url}")
    start_time = time.time()

    try:
        response = session.get(url, headers=headers, timeout=10)
        elapsed = time.time() - start_time

        print(f"\n状态码: {response.status_code}")
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"响应长度: {len(response.text):,} 字符")

        if response.status_code == 200:
            content = response.text

            # 检查是否成功
            if 'video-img-box' in content:
                count = content.count('video-img-box')
                print(f"\n✅ 成功！找到 {count} 个视频容器")
                print("可以直接用 requests 访问！")
                return True, elapsed
            elif 'cloudflare' in content.lower() or 'just a moment' in content.lower():
                print("\n❌ 仍然遇到 Cloudflare 验证")
                return False, elapsed
            else:
                print("\n⚠️  内容异常")
                print("前500字符:", content[:500])
                return False, elapsed
        else:
            print(f"\n❌ HTTP 错误: {response.status_code}")
            return False, elapsed

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False, 0


def test_multiple_pages(cookies):
    """
    测试多个页面
    """
    print("\n3. 测试多个页面访问")
    print("=" * 80)

    test_urls = [
        "https://jable.tv/hot/",
        "https://jable.tv/hot/2/",
        "https://jable.tv/hot/3/",
    ]

    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(
            cookie['name'],
            cookie['value'],
            domain=cookie.get('domain', '.jable.tv')
        )

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    total_time = 0
    success_count = 0

    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] {url}")
        start_time = time.time()

        try:
            response = session.get(url, headers=headers, timeout=10)
            elapsed = time.time() - start_time
            total_time += elapsed

            if response.status_code == 200 and 'video-img-box' in response.text:
                count = response.text.count('video-img-box')
                print(f"  ✓ 成功！耗时: {elapsed:.2f}秒, 找到 {count} 个视频")
                success_count += 1
            else:
                print(f"  ✗ 失败：状态码 {response.status_code}")

        except Exception as e:
            print(f"  ✗ 失败：{str(e)[:50]}")

        # 延迟
        if i < len(test_urls):
            time.sleep(1)

    print("\n" + "=" * 80)
    print(f"成功: {success_count}/{len(test_urls)}")
    print(f"平均耗时: {total_time/len(test_urls):.2f} 秒")
    print("=" * 80)


if __name__ == '__main__':
    url = "https://jable.tv/hot/"

    # 步骤1：获取 cookies
    cookies = get_cloudflare_cookies(url)

    if not cookies:
        print("❌ 无法获取 cookies")
        exit(1)

    # 步骤2：测试单个页面
    success, elapsed = test_requests_with_cookies(url, cookies)

    if success:
        print(f"\n🎉 可以使用 requests！预计加速 {(8-elapsed)/8*100:.0f}%")

        # 步骤3：测试多个页面
        test_multiple_pages(cookies)

        print("\n" + "=" * 80)
        print("结论：")
        print("  ✓ 可以先用浏览器获取 cookies")
        print("  ✓ 然后用 requests 快速访问")
        print("  ✓ cookies 可能有时效性（需定期刷新）")
        print("=" * 80)
    else:
        print("\n❌ 无法使用 requests")
        print("   仍需要使用浏览器")

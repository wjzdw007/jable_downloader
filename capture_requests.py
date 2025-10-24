#!/usr/bin/env python3
"""
抓包分析 jable.tv/hot/ 的网络请求
找出可以直接调用的 API 接口
"""

from playwright.sync_api import sync_playwright
import json

def capture_requests(url):
    """
    捕获页面加载时的所有网络请求
    """
    print(f"正在分析页面: {url}")
    print("=" * 80)

    captured_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 监听网络请求
        def handle_request(request):
            captured_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'headers': request.headers
            })

        # 监听网络响应
        def handle_response(response):
            url = response.url
            status = response.status
            content_type = response.headers.get('content-type', '')

            print(f"[{status}] {response.request.method} {url[:100]}")
            print(f"      Type: {response.request.resource_type}, Content-Type: {content_type}")

            # 如果是 JSON 或 HTML，尝试获取内容
            if 'json' in content_type or 'html' in content_type:
                try:
                    if response.status == 200:
                        text = response.text()
                        print(f"      Length: {len(text)} bytes")

                        # 如果是 JSON，打印前500字符
                        if 'json' in content_type:
                            print(f"      Preview: {text[:500]}")
                        # 如果是 HTML，检查是否包含视频数据
                        elif 'html' in content_type and 'video-img-box' in text:
                            count = text.count('video-img-box')
                            print(f"      ✓ 包含 {count} 个视频容器")
                except:
                    pass

            print()

        page.on('request', handle_request)
        page.on('response', handle_response)

        # 访问页面
        print("开始加载页面...\n")
        page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # 等待一下确保所有请求完成
        page.wait_for_timeout(3000)

        browser.close()

    print("\n" + "=" * 80)
    print("请求分析总结")
    print("=" * 80)

    # 按资源类型分组
    by_type = {}
    for req in captured_requests:
        rtype = req['resource_type']
        if rtype not in by_type:
            by_type[rtype] = []
        by_type[rtype].append(req)

    print(f"\n总请求数: {len(captured_requests)}\n")

    for rtype, reqs in sorted(by_type.items()):
        print(f"{rtype:<15} {len(reqs):>3} 个")

        # 显示重要的请求
        if rtype in ['document', 'xhr', 'fetch']:
            for req in reqs:
                print(f"  - {req['method']} {req['url'][:100]}")

    # 保存到文件
    with open('captured_requests.json', 'w', encoding='utf-8') as f:
        json.dump(captured_requests, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 请求详情已保存到: captured_requests.json")

    return captured_requests


if __name__ == '__main__':
    # 分析热门页面
    url = "https://jable.tv/hot/"
    capture_requests(url)

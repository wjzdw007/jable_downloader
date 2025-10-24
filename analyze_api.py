#!/usr/bin/env python3
"""
详细分析 jable.tv 的 API 接口
重点查找：XHR、fetch 请求，特别是返回视频列表的 API
"""

from playwright.sync_api import sync_playwright
import json
import time

def analyze_api_requests(url, wait_time=10):
    """
    捕获并分析 API 请求
    """
    print(f"正在分析页面: {url}")
    print("=" * 80)

    api_requests = []
    api_responses = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 监听 API 请求和响应
        def handle_request(request):
            # 只关注 XHR 和 fetch 类型
            if request.resource_type in ['xhr', 'fetch']:
                api_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data
                })
                print(f"\n🔍 发现 API 请求:")
                print(f"   类型: {request.resource_type}")
                print(f"   方法: {request.method}")
                print(f"   URL: {request.url}")
                if request.post_data:
                    print(f"   POST 数据: {request.post_data[:200]}")

        def handle_response(response):
            # 只关注 API 响应
            if response.request.resource_type in ['xhr', 'fetch']:
                try:
                    content_type = response.headers.get('content-type', '')

                    print(f"\n📥 API 响应:")
                    print(f"   状态: {response.status}")
                    print(f"   URL: {response.url}")
                    print(f"   Content-Type: {content_type}")

                    if response.status == 200:
                        try:
                            # 尝试获取响应内容
                            body = response.body()
                            text = body.decode('utf-8', errors='ignore')

                            api_responses[response.url] = {
                                'status': response.status,
                                'content_type': content_type,
                                'body': text,
                                'size': len(text)
                            }

                            print(f"   大小: {len(text)} bytes")

                            # 如果是 JSON，尝试解析
                            if 'json' in content_type:
                                try:
                                    data = json.loads(text)
                                    print(f"   ✓ JSON 数据预览:")
                                    print(f"     {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                                except:
                                    print(f"   内容预览: {text[:500]}")
                            else:
                                print(f"   内容预览: {text[:500]}")

                        except Exception as e:
                            print(f"   ⚠️  无法获取响应体: {e}")

                except Exception as e:
                    print(f"   ⚠️  处理响应失败: {e}")

        page.on('request', handle_request)
        page.on('response', handle_response)

        # 访问页面
        print("\n开始加载页面...\n")
        page.goto(url, wait_until='networkidle', timeout=60000)

        # 等待更长时间，确保所有 AJAX 请求完成
        print(f"\n等待 {wait_time} 秒，观察是否有延迟加载的 API 请求...")
        page.wait_for_timeout(wait_time * 1000)

        # 尝试滚动页面，触发懒加载
        print("\n尝试滚动页面，触发懒加载...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        # 尝试点击分页
        print("\n尝试查找并点击分页链接...")
        try:
            # 查找第2页链接
            next_page = page.query_selector('a[href="/hot/2/"]')
            if next_page:
                print("找到第2页链接，点击...")
                next_page.click()
                page.wait_for_timeout(5000)
        except:
            print("未找到分页链接或点击失败")

        browser.close()

    print("\n" + "=" * 80)
    print("API 请求分析总结")
    print("=" * 80)

    if not api_requests:
        print("\n❌ 未发现任何 XHR/fetch API 请求！")
        print("   说明：视频列表数据直接在 HTML 中渲染（服务端渲染）")
        print("   结论：无法通过 API 获取数据，必须解析 HTML")
    else:
        print(f"\n✓ 发现 {len(api_requests)} 个 API 请求\n")

        for i, req in enumerate(api_requests, 1):
            print(f"{i}. {req['method']} {req['url']}")
            if req['post_data']:
                print(f"   POST: {req['post_data'][:100]}")

            # 显示响应
            if req['url'] in api_responses:
                resp = api_responses[req['url']]
                print(f"   响应: {resp['status']}, {resp['size']} bytes")

        # 保存详细信息
        with open('api_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'requests': api_requests,
                'responses': {url: {**data, 'body': data['body'][:5000]} for url, data in api_responses.items()}
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✓ 详细信息已保存到: api_analysis.json")

    return api_requests, api_responses


def test_pagination_api(base_url="https://jable.tv/hot/"):
    """
    专门测试分页是否使用 API
    """
    print("\n" + "=" * 80)
    print("测试分页机制")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        api_calls = []

        def handle_request(request):
            if request.resource_type in ['xhr', 'fetch', 'document']:
                api_calls.append({
                    'type': request.resource_type,
                    'method': request.method,
                    'url': request.url
                })
                if request.resource_type in ['xhr', 'fetch']:
                    print(f"  📡 {request.method} {request.url}")

        page.on('request', handle_request)

        # 访问第1页
        print("\n1. 访问第1页...")
        page.goto(base_url, wait_until='networkidle')
        page.wait_for_timeout(3000)

        first_page_calls = len([c for c in api_calls if c['type'] in ['xhr', 'fetch']])
        print(f"   XHR/Fetch 请求数: {first_page_calls}")

        # 点击第2页
        print("\n2. 点击第2页...")
        try:
            api_calls.clear()

            # 查找第2页链接
            link = page.query_selector('a[href="/hot/2/"]')
            if link:
                link.click()
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)

                second_page_calls = len([c for c in api_calls if c['type'] in ['xhr', 'fetch']])
                print(f"   XHR/Fetch 请求数: {second_page_calls}")

                if second_page_calls > 0:
                    print("\n   ✓ 分页使用了 AJAX！")
                    for call in api_calls:
                        if call['type'] in ['xhr', 'fetch']:
                            print(f"     - {call['method']} {call['url']}")
                else:
                    print("\n   ❌ 分页是完整页面刷新，没有使用 AJAX")
            else:
                print("   未找到分页链接")

        except Exception as e:
            print(f"   测试失败: {e}")

        browser.close()


if __name__ == '__main__':
    # 分析主页的 API 请求
    print("【测试1】分析主页 API 请求")
    analyze_api_requests("https://jable.tv/hot/", wait_time=10)

    # 测试分页机制
    print("\n\n【测试2】测试分页机制")
    test_pagination_api()

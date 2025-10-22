#!/usr/bin/env python3
# coding: utf-8

"""
调试视频URL - 检查m3u8链接提取
"""

import re
from utils import get_response_from_playwright

def debug_video_url(video_url):
    """调试视频URL提取"""
    print("=" * 60)
    print("视频URL调试工具")
    print("=" * 60)
    print()

    video_id = video_url.split('/')[-2]
    print(f"视频ID: {video_id}")
    print(f"视频URL: {video_url}")
    print()

    print("正在获取视频页面...")
    try:
        page_str = get_response_from_playwright(video_url)
        print(f"✓ 页面获取成功，长度: {len(page_str)} 字符")
        print()

        # 尝试提取m3u8 URL
        print("正在提取 m3u8 URL...")
        result = re.search(r"https://.+?m3u8", page_str)

        if result:
            m3u8url = result[0]
            print(f"✓ 找到 m3u8 URL:")
            print(f"  {m3u8url}")
            print()

            # 分析URL
            print("URL分析:")
            parts = m3u8url.split('/')
            for i, part in enumerate(parts):
                print(f"  [{i}] {part}")
            print()

            # 检查URL是否包含完整路径
            if m3u8url.endswith('.m3u8'):
                print("✓ URL看起来是完整的")
            else:
                print("⚠ URL可能不完整，末尾不是 .m3u8")

            # 尝试访问这个URL
            print()
            print("尝试访问 m3u8 URL...")
            import requests
            try:
                response = requests.get(m3u8url, timeout=10)
                print(f"状态码: {response.status_code}")

                if response.status_code == 200:
                    print(f"✓ m3u8 文件可访问")
                    print(f"内容长度: {len(response.content)} 字节")
                    print()
                    print("m3u8 内容预览（前500字符）:")
                    print("-" * 60)
                    print(response.text[:500])
                    print("-" * 60)
                elif response.status_code == 404:
                    print("✗ 404 Not Found - 文件不存在")
                    print()
                    print("可能的原因:")
                    print("1. URL提取不正确")
                    print("2. 视频已被删除")
                    print("3. URL有时效性限制")
                    print("4. 需要特定的请求头")
                elif response.status_code == 403:
                    print("✗ 403 Forbidden - 访问被拒绝")
                    print()
                    print("可能的原因:")
                    print("1. 需要配置代理")
                    print("2. 需要特定的 Referer 头")
                    print("3. IP被限制")
                else:
                    print(f"✗ 未知错误: {response.status_code}")

            except Exception as e:
                print(f"✗ 访问失败: {str(e)}")
                print()
                print("提示: 可能需要配置代理或检查网络连接")

        else:
            print("✗ 未找到 m3u8 URL")
            print()
            print("尝试搜索其他可能的视频URL模式...")

            # 尝试其他模式
            patterns = [
                r'https://[^"\']+\.m3u8[^"\']*',
                r'https://[^"\']*video[^"\']*\.m3u8',
                r'hlsUrl["\']:\s*["\']([^"\']+)',
                r'videoUrl["\']:\s*["\']([^"\']+)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, page_str)
                if matches:
                    print(f"✓ 找到匹配: {pattern}")
                    for match in matches[:3]:  # 只显示前3个
                        print(f"  {match}")
                    print()

    except Exception as e:
        print(f"✗ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 测试URL
    test_url = "https://jable.tv/videos/fsdss-610/"
    debug_video_url(test_url)

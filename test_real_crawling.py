#!/usr/bin/env python3
# coding: utf-8

"""
真实爬取测试 - 测试视频列表页面的爬取功能
"""

import sys
from utils import get_response_from_playwright
from bs4 import BeautifulSoup

def test_video_list_page():
    """测试视频列表页面爬取"""
    print("=" * 60)
    print("真实爬取测试 - 视频列表页面")
    print("=" * 60)
    print()

    # 使用最新视频页面
    test_url = "https://jable.tv/latest-updates/"

    print(f"[测试 1] 访问最新视频列表页")
    print(f"URL: {test_url}")
    print()

    try:
        print("正在获取页面...")
        html = get_response_from_playwright(test_url)

        print(f"✓ 页面获取成功，长度: {len(html)} 字符")
        print()

        # 解析页面
        print("[测试 2] 解析视频信息")
        soup = BeautifulSoup(html, 'html.parser')

        # 查找视频链接
        video_links = soup.select('div.img-box > a')
        print(f"✓ 找到 {len(video_links)} 个视频")
        print()

        if len(video_links) > 0:
            print("前5个视频信息:")
            print("-" * 60)
            for i, link in enumerate(video_links[:5]):
                video_url = link.get('href', '')
                video_id = video_url.split('/')[-2] if video_url else 'unknown'

                # 获取视频标题
                title_elem = link.find('div', class_='title')
                title = title_elem.text.strip() if title_elem else 'No Title'

                print(f"{i+1}. ID: {video_id}")
                print(f"   标题: {title}")
                print(f"   URL: {video_url}")
                print()

            print("-" * 60)

        return len(video_links) > 0

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_page():
    """测试女优页面爬取"""
    print("\n" + "=" * 60)
    print("真实爬取测试 - 女优页面")
    print("=" * 60)
    print()

    # 测试一个女优页面（使用你配置中的订阅）
    test_url = "https://jable.tv/models/yua-mikami/"

    print(f"[测试 3] 访问女优页面")
    print(f"URL: {test_url}")
    print()

    try:
        print("正在获取页面...")
        html = get_response_from_playwright(test_url)

        print(f"✓ 页面获取成功，长度: {len(html)} 字符")
        print()

        # 解析页面
        print("[测试 4] 解析女优信息")
        soup = BeautifulSoup(html, 'html.parser')

        # 获取女优名称
        name_elem = soup.find('h2', class_='h3-md mb-1')
        if name_elem:
            name = name_elem.text.strip()
            print(f"✓ 女优名称: {name}")

        # 获取视频数量
        count_elem = soup.select_one('span.inactive-color')
        if count_elem:
            count_text = count_elem.text.strip()
            print(f"✓ 视频数量: {count_text}")

        print()

        # 查找视频
        video_links = soup.select('div.img-box > a')
        print(f"✓ 当前页面找到 {len(video_links)} 个视频")

        if len(video_links) > 0:
            print()
            print("前3个视频:")
            for i, link in enumerate(video_links[:3]):
                video_url = link.get('href', '')
                video_id = video_url.split('/')[-2] if video_url else 'unknown'
                print(f"  {i+1}. {video_id} - {video_url}")

        # 检查分页
        pagination = soup.select('.pagination > .page-item > .page-link')
        if pagination:
            last_page_elem = pagination[-1].get('data-parameters', '')
            if last_page_elem and ':' in last_page_elem:
                last_page = last_page_elem.split(':')[-1]
                print(f"\n✓ 总页数: {last_page}")

        return len(video_links) > 0

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success1 = test_video_list_page()
    success2 = test_model_page()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("✓ 所有真实爬取测试通过")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        print("=" * 60)
        sys.exit(1)

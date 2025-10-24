#!/usr/bin/env python3
"""
热门影片数据爬虫模块
负责从 https://jable.tv/hot/ 爬取视频数据和演员信息
"""

import re
import time
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup

# 使用优化版的 utils（复用浏览器，禁用资源，移除固定等待）
try:
    import utils_fast
    USE_FAST_MODE = True
    print("ℹ️  使用优化版爬虫（utils_fast）")

    def fetch_page(url: str, retry: int = 3) -> str:
        """统一的页面获取接口（优化版）"""
        return utils_fast.fast_requests_get(url, retry)

    def cleanup_browser():
        """清理浏览器实例"""
        utils_fast.close_browser_instance()

except ImportError:
    import utils
    USE_FAST_MODE = False
    print("⚠️  优化版不可用，使用原版 utils")

    def fetch_page(url: str, retry: int = 3) -> str:
        """统一的页面获取接口（原版）"""
        return utils.scrapingant_requests_get(url, retry)

    def cleanup_browser():
        """清理浏览器实例（原版无需清理）"""
        pass


def extract_videos_from_page(html: str) -> List[Dict]:
    """
    从页面 HTML 中提取视频信息

    Args:
        html: 页面 HTML 内容

    Returns:
        视频列表，每项包含 {video_id, title, views, likes, url}
    """
    soup = BeautifulSoup(html, 'html.parser')
    video_containers = soup.select('div.video-img-box')

    videos = []

    for container in video_containers:
        try:
            # 提取视频链接和 ID
            link_tag = container.select_one('a[href*="/videos/"]')
            if not link_tag:
                continue

            video_url = link_tag.get('href', '')
            if not video_url:
                continue

            # 从 URL 中提取视频 ID
            video_id = video_url.split('/')[-2] if '/' in video_url else ''
            if not video_id:
                continue

            # 提取标题
            title_tag = container.select_one('h6.title a')
            title = title_tag.get_text(strip=True) if title_tag else ''

            # 提取统计数据（观看数和点赞数）
            sub_title = container.select_one('p.sub-title')

            views = 0
            likes = 0

            if sub_title:
                text = sub_title.get_text()

                # 按行分割，提取每行的数字
                lines = text.strip().split('\n')
                numbers = []

                for line in lines:
                    line = line.strip()
                    if line:
                        # 去除所有空格和制表符
                        num_str = re.sub(r'\s+', '', line)
                        if num_str.isdigit():
                            numbers.append(int(num_str))

                # 第一个数字是观看数，第二个是点赞数
                if len(numbers) >= 2:
                    views = numbers[0]
                    likes = numbers[1]

            videos.append({
                'video_id': video_id,
                'title': title,
                'views': views,
                'likes': likes,
                'url': video_url
            })

        except Exception as e:
            print(f"⚠️  解析视频失败: {e}")
            continue

    return videos


def get_total_pages(html: str) -> int:
    """
    从页面 HTML 中获取总页数

    Args:
        html: 页面 HTML 内容

    Returns:
        总页数
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有分页链接
    pagination_links = soup.select('ul.pagination li a[href*="/hot/"]')
    max_page = 1

    for link in pagination_links:
        # 检查是否是"最後"链接
        text = link.get_text(strip=True)
        href = link.get('href', '')

        # 如果是"最後"链接，优先使用
        if '最後' in text or '»' in text:
            match = re.search(r'/hot/(\d+)/', href)
            if match:
                return int(match.group(1))

        # 否则，记录最大页码
        match = re.search(r'/hot/(\d+)/', href)
        if match:
            page_num = int(match.group(1))
            max_page = max(max_page, page_num)

    return max_page


def crawl_hot_page(page_num: int = 1, retry: int = 3) -> Tuple[List[Dict], int]:
    """
    爬取指定页的热门视频数据

    Args:
        page_num: 页码（从 1 开始）
        retry: 重试次数

    Returns:
        (视频列表, 总页数)
    """
    if page_num == 1:
        url = 'https://jable.tv/hot/'
    else:
        url = f'https://jable.tv/hot/{page_num}/'

    print(f"正在爬取第 {page_num} 页: {url}")

    try:
        html = fetch_page(url, retry=retry)
        videos = extract_videos_from_page(html)

        # 只在第一页时获取总页数
        total_pages = get_total_pages(html) if page_num == 1 else 0

        print(f"  ✓ 第 {page_num} 页爬取成功，找到 {len(videos)} 个视频")

        return videos, total_pages

    except Exception as e:
        print(f"  ✗ 第 {page_num} 页爬取失败: {str(e)[:100]}")
        return [], 0


def crawl_all_hot_pages(start_page: int = 1, end_page: Optional[int] = None,
                       page_delay: float = 1.0) -> List[Dict]:
    """
    爬取所有（或指定范围）热门页面的视频数据

    Args:
        start_page: 起始页码（默认 1）
        end_page: 结束页码（None 表示爬到最后一页）
        page_delay: 每页之间的延迟（秒）

    Returns:
        所有视频的列表
    """
    all_videos = []

    # 先爬第一页获取总页数
    print("=" * 80)
    print("开始爬取热门视频数据")
    print("=" * 80)

    first_page_videos, total_pages = crawl_hot_page(1, retry=5)

    if total_pages == 0:
        print("❌ 无法获取总页数，爬取失败")
        return []

    print(f"\n✓ 总页数: {total_pages:,}")

    if end_page is None:
        end_page = total_pages
    else:
        end_page = min(end_page, total_pages)

    # 如果起始页是 1，使用已经爬取的数据
    if start_page == 1:
        all_videos.extend(first_page_videos)
        start_page = 2

    print(f"✓ 爬取范围: 第 {start_page} 页 到 第 {end_page} 页")
    print(f"✓ 预计视频数量: {(end_page - start_page + 1) * 24:,} 个")
    print(f"✓ 预计耗时: {(end_page - start_page + 1) * (3 + page_delay) / 60:.1f} 分钟\n")

    # 爬取剩余页面
    for page_num in range(start_page, end_page + 1):
        videos, _ = crawl_hot_page(page_num, retry=3)
        all_videos.extend(videos)

        # 显示进度
        progress = (page_num - start_page + 1) / (end_page - start_page + 1) * 100
        print(f"  进度: {progress:.1f}% ({page_num}/{end_page}) | 已爬取: {len(all_videos):,} 个视频")

        # 延迟（避免请求过快）
        if page_num < end_page:
            time.sleep(page_delay)

    print("\n" + "=" * 80)
    print(f"✓ 爬取完成！共获取 {len(all_videos):,} 个视频")
    print("=" * 80)

    # 清理浏览器实例（如果使用优化版）
    if USE_FAST_MODE:
        print("\n正在清理浏览器实例...")
        cleanup_browser()

    return all_videos


def extract_actors_from_video_page(html: str) -> List[Dict]:
    """
    从视频详情页提取演员信息

    Args:
        html: 视频详情页 HTML 内容

    Returns:
        演员列表，每项包含 {actor_id, actor_name}
    """
    soup = BeautifulSoup(html, 'html.parser')

    actors = []

    # 查找演员容器
    models_container = soup.select('div.models a.model')

    for model_link in models_container:
        try:
            # 提取演员链接
            href = model_link.get('href', '')
            if not href or '/models/' not in href:
                continue

            # 从链接中提取演员 ID
            actor_id = href.split('/')[-2] if '/' in href else ''
            if not actor_id:
                continue

            # 提取演员名字（从 span 的 data-original-title 属性）
            span_tag = model_link.select_one('span[data-original-title]')
            actor_name = span_tag.get('data-original-title', '') if span_tag else ''

            # 如果没有 data-original-title，尝试从 title 属性获取
            if not actor_name:
                actor_name = span_tag.get('title', '') if span_tag else ''

            # 如果还是没有，使用显示的文本
            if not actor_name:
                actor_name = model_link.get_text(strip=True)

            if actor_id and actor_name:
                actors.append({
                    'actor_id': actor_id,
                    'actor_name': actor_name
                })

        except Exception as e:
            print(f"  ⚠️  解析演员失败: {e}")
            continue

    return actors


def crawl_video_actors(video_id: str, video_url: Optional[str] = None, retry: int = 2) -> List[Dict]:
    """
    爬取视频的演员信息

    Args:
        video_id: 视频 ID
        video_url: 视频 URL（可选，如果不提供则自动构建）
        retry: 重试次数

    Returns:
        演员列表，每项包含 {actor_id, actor_name}
    """
    if not video_url:
        video_url = f'https://jable.tv/videos/{video_id}/'

    print(f"  正在获取视频 {video_id} 的演员信息...")

    try:
        html = fetch_page(video_url, retry=retry)
        actors = extract_actors_from_video_page(html)

        if actors:
            actor_names = ', '.join([a['actor_name'] for a in actors])
            print(f"    ✓ 找到 {len(actors)} 个演员: {actor_names}")
        else:
            print(f"    ⚠️  未找到演员信息")

        return actors

    except Exception as e:
        print(f"    ✗ 获取演员信息失败: {str(e)[:100]}")
        return []


def crawl_multiple_video_actors(video_list: List[Dict], delay: float = 2.0) -> Dict[str, List[Dict]]:
    """
    批量爬取多个视频的演员信息

    Args:
        video_list: 视频列表，每项包含 {video_id, url}
        delay: 每个视频之间的延迟（秒）

    Returns:
        字典：{video_id: [演员列表]}
    """
    result = {}
    total = len(video_list)

    print("=" * 80)
    print(f"开始爬取 {total} 个视频的演员信息")
    print("=" * 80)

    for i, video in enumerate(video_list, 1):
        video_id = video['video_id']
        video_url = video.get('url')

        print(f"\n[{i}/{total}] 视频: {video_id}")

        actors = crawl_video_actors(video_id, video_url, retry=2)
        result[video_id] = actors

        # 延迟
        if i < total:
            time.sleep(delay)

    print("\n" + "=" * 80)
    print(f"✓ 完成！共获取 {len(result)} 个视频的演员信息")

    # 统计
    with_actors = sum(1 for actors in result.values() if actors)
    print(f"  有演员信息: {with_actors} 个")
    print(f"  无演员信息: {total - with_actors} 个")
    print("=" * 80)

    return result


if __name__ == '__main__':
    # 测试：爬取前 2 页
    print("测试爬虫模块")
    print("=" * 80)

    # 测试1：爬取单页
    print("\n【测试1】爬取第 1 页")
    videos, total_pages = crawl_hot_page(1)
    print(f"✓ 获取 {len(videos)} 个视频")
    print(f"✓ 总页数: {total_pages}")

    if videos:
        print(f"\n前 3 个视频:")
        for i, v in enumerate(videos[:3], 1):
            print(f"  {i}. {v['video_id']:<15} 👁️  {v['views']:>8,}  👍 {v['likes']:>6,}")

    # 测试2：爬取演员信息
    if videos:
        print(f"\n【测试2】爬取第一个视频的演员信息")
        first_video = videos[0]
        actors = crawl_video_actors(first_video['video_id'], first_video['url'])
        print(f"✓ 演员数量: {len(actors)}")
        for actor in actors:
            print(f"  - {actor['actor_name']} ({actor['actor_id']})")

    print("\n✓ 爬虫模块测试完成")

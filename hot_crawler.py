#!/usr/bin/env python3
"""
热门视频爬虫
从 https://jable.tv/hot/ 获取点赞数最高的视频并下载
"""

import os
import re
from bs4 import BeautifulSoup

import utils
import video_crawler
from config import CONF


def get_hot_videos(min_likes=2000):
    """
    获取热门页面的所有视频及其点赞数

    Args:
        min_likes: 最小点赞数阈值

    Returns:
        list: 包含视频信息的列表，按点赞数降序排列
              [{'id': 'xxx', 'url': 'xxx', 'title': 'xxx', 'likes': 123, 'views': 456}, ...]
    """
    url = "https://jable.tv/hot/"

    print(f"正在获取热门页面: {url}")

    try:
        html = utils.scrapingant_requests_get(url, retry=5)
        print(f"✓ 页面获取成功")
    except Exception as e:
        print(f"✗ 页面获取失败: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有视频容器
    video_containers = soup.select('div.video-img-box')

    if not video_containers:
        print("⚠️  未找到视频容器")
        return []

    print(f"找到 {len(video_containers)} 个视频")

    videos = []

    for container in video_containers:
        try:
            # 提取视频链接
            link_tag = container.select_one('a[href*="/videos/"]')
            if not link_tag:
                continue

            video_url = link_tag.get('href', '')
            if not video_url:
                continue

            # 提取视频 ID
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

            # 过滤低于阈值的视频
            if likes < min_likes:
                continue

            videos.append({
                'id': video_id,
                'url': video_url,
                'title': title,
                'likes': likes,
                'views': views
            })

        except Exception as e:
            print(f"⚠️  解析视频失败: {e}")
            continue

    # 按点赞数降序排列
    videos.sort(key=lambda x: x['likes'], reverse=True)

    return videos


def check_video_downloaded(video_id):
    """
    检查视频是否已下载（通过文件系统）

    Args:
        video_id: 视频 ID

    Returns:
        bool: True 表示已下载，False 表示未下载
    """
    output_dir = CONF.get('outputDir', './')

    # 检查是否存在对应的 mp4 文件
    # 可能的文件名格式：
    # 1. {video_id}.mp4
    # 2. {video_id}/{title}.mp4
    # 3. {title}.mp4 (包含 video_id)

    try:
        # 遍历输出目录
        if not os.path.exists(output_dir):
            return False

        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.mp4'):
                    # 检查文件名或路径中是否包含 video_id
                    full_path = os.path.join(root, file)
                    if video_id.lower() in full_path.lower():
                        return True

        return False

    except Exception as e:
        print(f"⚠️  检查文件时出错: {e}")
        return False


def download_hot_videos(top_n=4, min_likes=2000):
    """
    下载热门视频中点赞数最高的前 N 个

    Args:
        top_n: 下载数量（默认 4）
        min_likes: 最小点赞数阈值（默认 2000）
    """
    print("\n" + "=" * 80)
    print(f"开始下载热门视频（Top {top_n}，最小点赞数 {min_likes:,}）")
    print("=" * 80)

    # 获取热门视频列表
    videos = get_hot_videos(min_likes=min_likes)

    if not videos:
        print("\n❌ 未找到符合条件的视频")
        return

    print(f"\n找到 {len(videos)} 个符合条件的视频（点赞数 ≥ {min_likes:,}）")

    # 取前 N 个
    top_videos = videos[:top_n]

    print(f"\n准备下载前 {len(top_videos)} 个视频:")
    print("-" * 80)
    for i, video in enumerate(top_videos, 1):
        title_short = video['title'][:60] + '...' if len(video['title']) > 60 else video['title']
        print(f"{i}. {video['id']:<15} 👍 {video['likes']:>6,}   {title_short}")
    print("-" * 80)

    # 开始下载
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    download_interval = CONF.get('downloadInterval', 0)

    for i, video in enumerate(top_videos, 1):
        video_id = video['id']
        video_url = video['url']

        print(f"\n[{i}/{len(top_videos)}] 处理视频: {video_id}")
        print(f"  标题: {video['title'][:80]}")
        print(f"  点赞: {video['likes']:,} | 观看: {video['views']:,}")

        # 检查是否已下载
        if check_video_downloaded(video_id):
            print(f"  ✓ 已下载，跳过")
            skipped_count += 1
            continue

        # 下载视频
        print(f"  开始下载...")
        try:
            video_crawler.download_by_video_url(video_url)
            downloaded_count += 1
            print(f"  ✓ 下载完成")

            # 下载间隔
            if i < len(top_videos) and download_interval > 0:
                import time
                print(f"  等待 {download_interval} 秒...")
                time.sleep(download_interval)

        except Exception as e:
            print(f"  ✗ 下载失败: {str(e)[:100]}")
            failed_count += 1
            # 继续下一个视频
            continue

    # 统计
    print("\n" + "=" * 80)
    print("下载完成")
    print("=" * 80)
    print(f"总数: {len(top_videos)}")
    print(f"✓ 已下载: {downloaded_count}")
    print(f"⊙ 跳过（已存在）: {skipped_count}")
    print(f"✗ 失败: {failed_count}")
    print("=" * 80)


if __name__ == '__main__':
    # 测试
    download_hot_videos(top_n=4, min_likes=2000)

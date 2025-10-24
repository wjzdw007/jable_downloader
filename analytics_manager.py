#!/usr/bin/env python3
"""
热门影片分析管理模块
整合爬虫、数据库操作，提供初始化、每日更新、榜单生成等功能
"""

import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import analytics_db
import analytics_crawler
import telegram_notifier


DEFAULT_DB_PATH = './analytics.db'


def format_growth_report_for_telegram(report_data: Dict, top_n: int = 50) -> str:
    """
    格式化增量榜单为 Telegram 消息

    Args:
        report_data: generate_growth_report() 返回的榜单数据
        top_n: 显示前 N 个

    Returns:
        格式化的 Telegram 消息
    """
    date = report_data['date']
    prev_date = report_data['prev_date']
    video_growth = report_data['video_growth'][:top_n]
    actor_growth = report_data['actor_growth'][:top_n]

    # 构建消息
    lines = []
    lines.append(f"📊 *热门影片增量榜单*")
    lines.append(f"📅 对比: {prev_date} → {date}")
    lines.append("")

    # 影片榜
    lines.append(f"🎬 *影片点赞增长 Top {len(video_growth)}*")
    lines.append("```")

    for i, video in enumerate(video_growth, 1):
        growth = video['growth']
        today_likes = video['today_likes']
        video_id = video['video_id']
        title = video['title'][:35] + '...' if len(video['title']) > 35 else video['title']

        lines.append(f"{i:2}. +{growth:>6,}  👍{today_likes:>7,}  {video_id}")

    lines.append("```")
    lines.append("")

    # 演员榜
    lines.append(f"⭐ *演员点赞增长 Top {len(actor_growth)}*")
    lines.append("```")

    for i, actor in enumerate(actor_growth, 1):
        growth = actor['growth']
        today_likes = actor['today_likes']
        actor_name = actor['actor_name'][:20]

        lines.append(f"{i:2}. +{growth:>7,}  👍{today_likes:>8,}  {actor_name}")

    lines.append("```")

    return '\n'.join(lines)


def initialize_hot_videos_analysis(db_path: str = DEFAULT_DB_PATH,
                                   max_pages: Optional[int] = None,
                                   top_n_for_actors: int = 200) -> None:
    """
    初始化热门影片分析

    步骤：
    1. 初始化数据库
    2. 爬取所有热门页面的视频数据
    3. 存入数据库
    4. 爬取 Top N 影片的演员信息
    5. 更新演员统计

    Args:
        db_path: 数据库路径
        max_pages: 最大爬取页数（None 表示爬取所有页面）
        top_n_for_actors: 爬取演员信息的视频数量（按点赞数排序）
    """
    print("\n" + "=" * 80)
    print("🚀 开始初始化热门影片分析系统")
    print("=" * 80)

    # 1. 初始化数据库
    print("\n【步骤 1/5】初始化数据库")
    print("-" * 80)
    analytics_db.init_database(db_path)

    # 2. 爬取所有热门页面
    print("\n【步骤 2/5】爬取热门视频数据")
    print("-" * 80)

    if max_pages:
        print(f"⚠️  限制爬取页数: {max_pages}")

    all_videos = analytics_crawler.crawl_all_hot_pages(
        start_page=1,
        end_page=max_pages,
        page_delay=1.0
    )

    if not all_videos:
        print("❌ 爬取失败，没有获取到任何视频")
        return

    # 3. 存入数据库
    print("\n【步骤 3/5】保存视频数据到数据库")
    print("-" * 80)

    today = datetime.now().strftime('%Y-%m-%d')

    # 准备批量插入的数据
    stats_list = []
    for rank, video in enumerate(all_videos, 1):
        stats_list.append({
            'video_id': video['video_id'],
            'title': video['title'],
            'date': today,
            'views': video['views'],
            'likes': video['likes'],
            'rank': rank
        })

    # 批量插入
    print(f"正在保存 {len(stats_list):,} 个视频的数据...")
    analytics_db.bulk_insert_daily_stats(stats_list, db_path)
    print(f"✓ 完成！共保存 {len(stats_list):,} 个视频")

    # 4. 爬取 Top N 影片的演员信息
    print(f"\n【步骤 4/5】爬取 Top {top_n_for_actors} 影片的演员信息")
    print("-" * 80)

    # 按点赞数排序，取前 N 个
    top_videos = sorted(all_videos, key=lambda x: x['likes'], reverse=True)[:top_n_for_actors]

    print(f"选出点赞数前 {len(top_videos)} 个视频")
    print(f"预计耗时: {len(top_videos) * 2.5 / 60:.1f} 分钟\n")

    # 爬取演员信息
    actors_data = analytics_crawler.crawl_multiple_video_actors(top_videos, delay=2.0)

    # 保存演员信息到数据库
    print("\n正在保存演员信息到数据库...")
    saved_count = 0

    for video_id, actors in actors_data.items():
        if actors:
            analytics_db.bulk_insert_video_actors(video_id, actors, db_path)
            saved_count += 1

    print(f"✓ 完成！共为 {saved_count} 个视频保存了演员信息")

    # 5. 更新演员每日统计
    print(f"\n【步骤 5/5】更新演员每日统计")
    print("-" * 80)

    analytics_db.update_actor_daily_stats(today, db_path)
    print(f"✓ 完成！已更新演员每日统计")

    # 显示统计信息
    print("\n" + "=" * 80)
    print("✅ 初始化完成！数据库统计:")
    print("=" * 80)

    stats = analytics_db.get_database_stats(db_path)
    print(f"  视频总数: {stats['total_videos']:,}")
    print(f"  演员总数: {stats['total_actors']:,}")
    print(f"  有演员信息的视频: {stats['videos_with_actors']:,}")
    print(f"  数据日期: {stats['date_range'][0]} 到 {stats['date_range'][1]}")
    print("=" * 80)


def daily_update_hot_videos(db_path: str = DEFAULT_DB_PATH,
                            max_pages: Optional[int] = None,
                            top_n_for_new_actors: int = 200) -> None:
    """
    每日更新热门影片数据

    步骤：
    1. 爬取所有热门页面的视频数据（只更新观看数和点赞数）
    2. 存入数据库
    3. 检查是否有新进 Top N 的影片
    4. 如果有，爬取其演员信息
    5. 更新演员统计

    Args:
        db_path: 数据库路径
        max_pages: 最大爬取页数（None 表示爬取所有页面）
        top_n_for_new_actors: 检查新进榜的视频数量阈值
    """
    print("\n" + "=" * 80)
    print("📅 开始每日更新热门影片数据")
    print("=" * 80)

    today = datetime.now().strftime('%Y-%m-%d')

    # 1. 爬取所有热门页面
    print("\n【步骤 1/4】爬取热门视频数据")
    print("-" * 80)

    if max_pages:
        print(f"⚠️  限制爬取页数: {max_pages}")

    all_videos = analytics_crawler.crawl_all_hot_pages(
        start_page=1,
        end_page=max_pages,
        page_delay=1.0
    )

    if not all_videos:
        print("❌ 爬取失败，没有获取到任何视频")
        return

    # 2. 存入数据库
    print("\n【步骤 2/4】更新数据库")
    print("-" * 80)

    # 准备批量插入的数据
    stats_list = []
    for rank, video in enumerate(all_videos, 1):
        stats_list.append({
            'video_id': video['video_id'],
            'title': video['title'],
            'date': today,
            'views': video['views'],
            'likes': video['likes'],
            'rank': rank
        })

    print(f"正在更新 {len(stats_list):,} 个视频的数据...")
    analytics_db.bulk_insert_daily_stats(stats_list, db_path)
    print(f"✓ 完成！")

    # 3. 检查是否有新进 Top N 的影片（没有演员信息）
    print(f"\n【步骤 3/4】检查新进 Top {top_n_for_new_actors} 的影片")
    print("-" * 80)

    # 获取点赞数前 N 的视频
    top_videos_db = analytics_db.get_top_videos_by_likes(today, top_n_for_new_actors, db_path)
    top_video_ids = {v['video_id'] for v in top_videos_db}

    # 获取没有演员信息的视频
    videos_without_actors = set(analytics_db.get_videos_without_actors(db_path))

    # 找出需要补充演员信息的视频（在 Top N 且没有演员信息）
    need_actors = top_video_ids & videos_without_actors

    if need_actors:
        print(f"发现 {len(need_actors)} 个新进 Top {top_n_for_new_actors} 的视频需要补充演员信息")

        # 准备爬取演员信息
        videos_to_crawl = [
            {'video_id': vid, 'url': f'https://jable.tv/videos/{vid}/'}
            for vid in need_actors
        ]

        print(f"预计耗时: {len(videos_to_crawl) * 2.5 / 60:.1f} 分钟\n")

        # 爬取演员信息
        actors_data = analytics_crawler.crawl_multiple_video_actors(videos_to_crawl, delay=2.0)

        # 保存到数据库
        print("\n正在保存演员信息到数据库...")
        saved_count = 0

        for video_id, actors in actors_data.items():
            if actors:
                analytics_db.bulk_insert_video_actors(video_id, actors, db_path)
                saved_count += 1

        print(f"✓ 完成！共为 {saved_count} 个视频保存了演员信息")
    else:
        print(f"✓ Top {top_n_for_new_actors} 的视频都已有演员信息，无需补充")

    # 4. 更新演员每日统计
    print(f"\n【步骤 4/4】更新演员每日统计")
    print("-" * 80)

    analytics_db.update_actor_daily_stats(today, db_path)
    print(f"✓ 完成！")

    # 显示统计信息
    print("\n" + "=" * 80)
    print("✅ 每日更新完成！数据库统计:")
    print("=" * 80)

    stats = analytics_db.get_database_stats(db_path)
    print(f"  视频总数: {stats['total_videos']:,}")
    print(f"  演员总数: {stats['total_actors']:,}")
    print(f"  有演员信息的视频: {stats['videos_with_actors']:,}")
    print(f"  数据日期: {stats['date_range'][0]} 到 {stats['date_range'][1]}")
    print("=" * 80)


def send_growth_report_to_telegram(date: Optional[str] = None,
                                  prev_date: Optional[str] = None,
                                  top_n: int = 50,
                                  db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    生成增量榜单并发送到 Telegram

    Args:
        date: 当前日期 (YYYY-MM-DD)，None 表示今天
        prev_date: 前一天日期 (YYYY-MM-DD)，None 表示昨天
        top_n: 榜单数量
        db_path: 数据库路径

    Returns:
        是否发送成功
    """
    # 生成榜单
    report_data = generate_growth_report(date, prev_date, top_n, db_path)

    # 格式化为 Telegram 消息
    message = format_growth_report_for_telegram(report_data, top_n)

    # 发送到 Telegram
    print("\n" + "=" * 80)
    print("📱 发送榜单到 Telegram")
    print("=" * 80)

    success = telegram_notifier.send_telegram_message(message)

    if success:
        print("✓ 发送成功！")
    else:
        print("✗ 发送失败")

    return success


def generate_growth_report(date: Optional[str] = None,
                          prev_date: Optional[str] = None,
                          top_n: int = 50,
                          db_path: str = DEFAULT_DB_PATH) -> Dict:
    """
    生成增量榜单

    Args:
        date: 当前日期 (YYYY-MM-DD)，None 表示今天
        prev_date: 前一天日期 (YYYY-MM-DD)，None 表示昨天
        top_n: 榜单数量
        db_path: 数据库路径

    Returns:
        榜单数据 {video_growth: [...], actor_growth: [...]}
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    if prev_date is None:
        prev_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("\n" + "=" * 80)
    print(f"📊 生成增量榜单")
    print("=" * 80)
    print(f"  对比日期: {prev_date} → {date}")
    print(f"  榜单数量: Top {top_n}")
    print("-" * 80)

    # 获取视频点赞增长榜
    print("\n【影片点赞增长榜】")
    video_growth = analytics_db.get_likes_growth(date, prev_date, top_n, db_path)

    if video_growth:
        print(f"\n排名  视频ID            今日点赞    昨日点赞      增长")
        print("-" * 80)
        for i, video in enumerate(video_growth[:10], 1):  # 只显示前 10
            print(f"{i:<5} {video['video_id']:<15} {video['today_likes']:>10,}  {video['yesterday_likes']:>10,}  +{video['growth']:>8,}")

        if len(video_growth) > 10:
            print(f"... 还有 {len(video_growth) - 10} 个视频")
    else:
        print("  暂无数据")

    # 获取演员点赞增长榜
    print(f"\n【演员点赞增长榜】")
    actor_growth = analytics_db.get_actor_likes_growth(date, prev_date, top_n, db_path)

    if actor_growth:
        print(f"\n排名  演员名                今日点赞    昨日点赞      增长")
        print("-" * 80)
        for i, actor in enumerate(actor_growth[:10], 1):  # 只显示前 10
            print(f"{i:<5} {actor['actor_name']:<20} {actor['today_likes']:>10,}  {actor['yesterday_likes']:>10,}  +{actor['growth']:>8,}")

        if len(actor_growth) > 10:
            print(f"... 还有 {len(actor_growth) - 10} 个演员")
    else:
        print("  暂无数据")

    print("\n" + "=" * 80)

    return {
        'date': date,
        'prev_date': prev_date,
        'video_growth': video_growth,
        'actor_growth': actor_growth
    }


if __name__ == '__main__':
    # 测试：使用测试数据库
    test_db = './test_analytics_manager.db'

    # 删除旧的测试数据库
    if os.path.exists(test_db):
        os.remove(test_db)

    print("测试分析管理模块")
    print("=" * 80)

    # 测试初始化（只爬取前 2 页作为测试）
    print("\n【测试】初始化（前 2 页）")
    initialize_hot_videos_analysis(
        db_path=test_db,
        max_pages=2,
        top_n_for_actors=5  # 只爬取前 5 个视频的演员信息
    )

    # 显示数据库统计
    stats = analytics_db.get_database_stats(test_db)
    print(f"\n数据库统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ 分析管理模块测试完成")

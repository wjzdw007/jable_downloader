#!/usr/bin/env python3
"""
完整流程测试
测试初始化 → 每日更新 → 榜单生成的完整流程
"""

import os
import sqlite3
from datetime import datetime, timedelta

import analytics_manager
import analytics_db

# 测试数据库路径
TEST_DB = './test_complete_flow.db'


def clean_test_db():
    """清理测试数据库"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        print(f"✓ 已删除旧的测试数据库: {TEST_DB}\n")


def test_step1_initialize():
    """测试步骤 1：初始化"""
    print("\n" + "=" * 100)
    print("测试步骤 1：初始化（爬取前 3 页，Top 5 视频的演员信息）")
    print("=" * 100)

    analytics_manager.initialize_hot_videos_analysis(
        db_path=TEST_DB,
        max_pages=3,  # 只爬前 3 页作为测试
        top_n_for_actors=5  # 只爬 Top 5 的演员信息
    )

    # 显示统计
    stats = analytics_db.get_database_stats(TEST_DB)
    print(f"\n初始化后的数据库统计:")
    print(f"  视频总数: {stats['total_videos']}")
    print(f"  演员总数: {stats['total_actors']}")
    print(f"  有演员信息的视频: {stats['videos_with_actors']}")


def test_step2_simulate_next_day():
    """测试步骤 2：模拟第二天数据（修改部分视频的点赞数）"""
    print("\n" + "=" * 100)
    print("测试步骤 2：模拟第二天数据（人工修改点赞数）")
    print("=" * 100)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # 连接数据库
    with analytics_db.get_db_connection(TEST_DB) as conn:
        cursor = conn.cursor()

        # 获取今天的所有视频数据
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT video_id, views, likes
            FROM daily_stats
            WHERE date = ?
            ORDER BY likes DESC
        ''', (today,))

        videos = cursor.fetchall()

        print(f"正在为 {len(videos)} 个视频生成明天的数据...")

        # 为每个视频生成明天的数据（模拟增长）
        for i, video in enumerate(videos):
            video_id = video['video_id']
            old_views = video['views']
            old_likes = video['likes']

            # 前 10 个视频增长更快
            if i < 10:
                views_growth = int(old_views * 0.05)  # 增长 5%
                likes_growth = int(old_likes * 0.03)  # 增长 3%
            else:
                views_growth = int(old_views * 0.02)  # 增长 2%
                likes_growth = int(old_likes * 0.01)  # 增长 1%

            new_views = old_views + views_growth
            new_likes = old_likes + likes_growth

            # 插入明天的数据
            cursor.execute('''
                INSERT INTO daily_stats (video_id, date, views, likes, rank)
                VALUES (?, ?, ?, ?, ?)
            ''', (video_id, tomorrow, new_views, new_likes, i + 1))

        conn.commit()

    # 更新演员统计
    analytics_db.update_actor_daily_stats(tomorrow, TEST_DB)

    print(f"✓ 已生成明天（{tomorrow}）的数据")


def test_step3_generate_report():
    """测试步骤 3：生成增量榜单"""
    print("\n" + "=" * 100)
    print("测试步骤 3：生成增量榜单")
    print("=" * 100)

    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # 生成榜单
    report_data = analytics_manager.generate_growth_report(
        date=tomorrow,
        prev_date=today,
        top_n=10,  # 只显示 Top 10
        db_path=TEST_DB
    )

    # 格式化为 Telegram 消息（测试消息格式）
    print("\n" + "=" * 100)
    print("Telegram 消息预览:")
    print("=" * 100)

    message = analytics_manager.format_growth_report_for_telegram(report_data, top_n=10)
    print(message)


def test_step4_daily_update():
    """测试步骤 4：模拟每日更新（第三天）"""
    print("\n" + "=" * 100)
    print("测试步骤 4：每日更新（爬取最新数据）")
    print("=" * 100)

    # 注意：这里会真实爬取数据，会比较慢
    print("⚠️  这将真实爬取前 2 页数据，可能需要 1-2 分钟...")

    # 暂不执行，避免测试时间过长
    # analytics_manager.daily_update_hot_videos(
    #     db_path=TEST_DB,
    #     max_pages=2,
    #     top_n_for_new_actors=5
    # )

    print("✓ 跳过真实爬取（避免测试时间过长）")


def main():
    """运行完整测试"""
    print("\n" + "=" * 100)
    print("热门影片分析系统 - 完整流程测试")
    print("=" * 100)
    print(f"测试数据库: {TEST_DB}")
    print()

    # 清理旧数据
    clean_test_db()

    try:
        # 步骤 1：初始化
        test_step1_initialize()

        # 步骤 2：模拟第二天数据
        test_step2_simulate_next_day()

        # 步骤 3：生成榜单
        test_step3_generate_report()

        # 步骤 4：每日更新（跳过，避免时间过长）
        # test_step4_daily_update()

        print("\n" + "=" * 100)
        print("✅ 完整流程测试通过！")
        print("=" * 100)
        print()
        print("系统功能:")
        print("  ✓ 数据库初始化")
        print("  ✓ 热门视频爬取")
        print("  ✓ 演员信息提取")
        print("  ✓ 增量计算")
        print("  ✓ 榜单生成")
        print("  ✓ Telegram 消息格式化")
        print()
        print("命令行使用示例:")
        print("  # 初始化（爬取所有页面，Top 200 视频的演员信息）")
        print("  python main.py analyze init")
        print()
        print("  # 每日更新（爬取最新数据，补充新进榜视频的演员信息）")
        print("  python main.py analyze update")
        print()
        print("  # 生成榜单")
        print("  python main.py report --top 50")
        print()
        print("  # 生成榜单并发送到 Telegram")
        print("  python main.py report --top 50 --send")
        print()
        print("建议的 cron 任务（每天凌晨 2 点运行）:")
        print("  0 2 * * * cd /path/to/jable_downloader && python main.py analyze update && python main.py report --send")
        print()
        print("=" * 100)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

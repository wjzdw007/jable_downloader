#!/usr/bin/env python3
"""
热门影片和演员分析数据库模块
管理 SQLite 数据库的创建、读写操作
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

# 默认数据库路径
DEFAULT_DB_PATH = './analytics.db'


@contextmanager
def get_db_connection(db_path: str = DEFAULT_DB_PATH):
    """
    数据库连接上下文管理器

    Args:
        db_path: 数据库文件路径

    Yields:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    初始化数据库，创建所有必要的表

    Args:
        db_path: 数据库文件路径
    """
    print(f"正在初始化数据库: {db_path}")

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. 视频表（基本信息）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                first_seen_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 每日统计表（视频的观看数和点赞数快照）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                date TEXT NOT NULL,
                views INTEGER NOT NULL DEFAULT 0,
                likes INTEGER NOT NULL DEFAULT 0,
                rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(video_id),
                UNIQUE(video_id, date)
            )
        ''')

        # 3. 演员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actors (
                actor_id TEXT PRIMARY KEY,
                actor_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 4. 视频-演员关联表（多对多）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_actors (
                video_id TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (video_id, actor_id),
                FOREIGN KEY (video_id) REFERENCES videos(video_id),
                FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
            )
        ''')

        # 5. 演员每日统计表（聚合数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actor_daily_stats (
                actor_id TEXT NOT NULL,
                date TEXT NOT NULL,
                total_views INTEGER NOT NULL DEFAULT 0,
                total_likes INTEGER NOT NULL DEFAULT 0,
                video_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (actor_id, date),
                FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
            )
        ''')

        # 创建索引以提升查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats_video_date ON daily_stats(video_id, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats_likes ON daily_stats(likes DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_actor_daily_stats_date ON actor_daily_stats(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_actors_video ON video_actors(video_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_actors_actor ON video_actors(actor_id)')

        conn.commit()

    print("✓ 数据库初始化完成")


# ==================== 视频相关操作 ====================

def insert_video(video_id: str, title: str, first_seen_date: str,
                 db_path: str = DEFAULT_DB_PATH) -> None:
    """
    插入新视频（如果不存在）

    Args:
        video_id: 视频 ID
        title: 视频标题
        first_seen_date: 首次发现日期 (YYYY-MM-DD)
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO videos (video_id, title, first_seen_date)
            VALUES (?, ?, ?)
        ''', (video_id, title, first_seen_date))


def insert_daily_stats(video_id: str, date: str, views: int, likes: int,
                       rank: Optional[int] = None, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    插入或更新每日统计数据

    Args:
        video_id: 视频 ID
        date: 日期 (YYYY-MM-DD)
        views: 观看数
        likes: 点赞数
        rank: 排名（可选）
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_stats (video_id, date, views, likes, rank)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(video_id, date) DO UPDATE SET
                views = excluded.views,
                likes = excluded.likes,
                rank = excluded.rank
        ''', (video_id, date, views, likes, rank))


def bulk_insert_daily_stats(stats_list: List[Dict], db_path: str = DEFAULT_DB_PATH) -> None:
    """
    批量插入每日统计数据（更高效）

    Args:
        stats_list: 统计数据列表，每项包含 {video_id, title, date, views, likes, rank}
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 先插入视频基本信息
        video_data = [(s['video_id'], s['title'], s['date']) for s in stats_list]
        cursor.executemany('''
            INSERT OR IGNORE INTO videos (video_id, title, first_seen_date)
            VALUES (?, ?, ?)
        ''', video_data)

        # 再插入统计数据
        stats_data = [(s['video_id'], s['date'], s['views'], s['likes'], s.get('rank'))
                     for s in stats_list]
        cursor.executemany('''
            INSERT INTO daily_stats (video_id, date, views, likes, rank)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(video_id, date) DO UPDATE SET
                views = excluded.views,
                likes = excluded.likes,
                rank = excluded.rank
        ''', stats_data)


# ==================== 演员相关操作 ====================

def insert_actor(actor_id: str, actor_name: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    插入演员信息（如果不存在）

    Args:
        actor_id: 演员 ID
        actor_name: 演员名字
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO actors (actor_id, actor_name)
            VALUES (?, ?)
        ''', (actor_id, actor_name))


def link_video_actor(video_id: str, actor_id: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    关联视频和演员

    Args:
        video_id: 视频 ID
        actor_id: 演员 ID
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO video_actors (video_id, actor_id)
            VALUES (?, ?)
        ''', (video_id, actor_id))


def bulk_insert_video_actors(video_id: str, actors_list: List[Dict],
                             db_path: str = DEFAULT_DB_PATH) -> None:
    """
    批量插入视频的演员信息

    Args:
        video_id: 视频 ID
        actors_list: 演员列表，每项包含 {actor_id, actor_name}
        db_path: 数据库路径
    """
    if not actors_list:
        return

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 先插入演员信息
        actor_data = [(a['actor_id'], a['actor_name']) for a in actors_list]
        cursor.executemany('''
            INSERT OR IGNORE INTO actors (actor_id, actor_name)
            VALUES (?, ?)
        ''', actor_data)

        # 再关联视频和演员
        link_data = [(video_id, a['actor_id']) for a in actors_list]
        cursor.executemany('''
            INSERT OR IGNORE INTO video_actors (video_id, actor_id)
            VALUES (?, ?)
        ''', link_data)


def update_actor_daily_stats(date: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    更新演员每日统计（从视频统计聚合）

    Args:
        date: 日期 (YYYY-MM-DD)
        db_path: 数据库路径
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 聚合计算每个演员在指定日期的总点赞数、总观看数和视频数量
        cursor.execute('''
            INSERT INTO actor_daily_stats (actor_id, date, total_views, total_likes, video_count)
            SELECT
                va.actor_id,
                ? as date,
                SUM(ds.views) as total_views,
                SUM(ds.likes) as total_likes,
                COUNT(DISTINCT ds.video_id) as video_count
            FROM video_actors va
            JOIN daily_stats ds ON va.video_id = ds.video_id
            WHERE ds.date = ?
            GROUP BY va.actor_id
            ON CONFLICT(actor_id, date) DO UPDATE SET
                total_views = excluded.total_views,
                total_likes = excluded.total_likes,
                video_count = excluded.video_count
        ''', (date, date))


# ==================== 查询操作 ====================

def get_top_videos_by_likes(date: str, limit: int = 200,
                           db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """
    获取指定日期点赞数最高的视频

    Args:
        date: 日期 (YYYY-MM-DD)
        limit: 返回数量
        db_path: 数据库路径

    Returns:
        视频列表，每项包含 {video_id, title, views, likes}
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.video_id, v.title, ds.views, ds.likes
            FROM daily_stats ds
            JOIN videos v ON ds.video_id = v.video_id
            WHERE ds.date = ?
            ORDER BY ds.likes DESC
            LIMIT ?
        ''', (date, limit))

        return [dict(row) for row in cursor.fetchall()]


def get_videos_without_actors(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """
    获取还没有演员信息的视频 ID 列表

    Args:
        db_path: 数据库路径

    Returns:
        视频 ID 列表
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.video_id
            FROM videos v
            LEFT JOIN video_actors va ON v.video_id = va.video_id
            WHERE va.video_id IS NULL
        ''')

        return [row['video_id'] for row in cursor.fetchall()]


def get_likes_growth(date: str, prev_date: str, limit: int = 50,
                    db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """
    获取点赞数增长最快的视频

    Args:
        date: 当前日期 (YYYY-MM-DD)
        prev_date: 前一天日期 (YYYY-MM-DD)
        limit: 返回数量
        db_path: 数据库路径

    Returns:
        视频列表，每项包含 {video_id, title, today_likes, yesterday_likes, growth}
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                v.video_id,
                v.title,
                today.likes as today_likes,
                COALESCE(yesterday.likes, 0) as yesterday_likes,
                (today.likes - COALESCE(yesterday.likes, 0)) as growth
            FROM daily_stats today
            JOIN videos v ON today.video_id = v.video_id
            LEFT JOIN daily_stats yesterday
                ON today.video_id = yesterday.video_id
                AND yesterday.date = ?
            WHERE today.date = ?
            ORDER BY growth DESC
            LIMIT ?
        ''', (prev_date, date, limit))

        return [dict(row) for row in cursor.fetchall()]


def get_actor_likes_growth(date: str, prev_date: str, limit: int = 50,
                          db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """
    获取演员点赞数增长最快的排名

    Args:
        date: 当前日期 (YYYY-MM-DD)
        prev_date: 前一天日期 (YYYY-MM-DD)
        limit: 返回数量
        db_path: 数据库路径

    Returns:
        演员列表，每项包含 {actor_id, actor_name, today_likes, yesterday_likes, growth}
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                a.actor_id,
                a.actor_name,
                today.total_likes as today_likes,
                COALESCE(yesterday.total_likes, 0) as yesterday_likes,
                (today.total_likes - COALESCE(yesterday.total_likes, 0)) as growth
            FROM actor_daily_stats today
            JOIN actors a ON today.actor_id = a.actor_id
            LEFT JOIN actor_daily_stats yesterday
                ON today.actor_id = yesterday.actor_id
                AND yesterday.date = ?
            WHERE today.date = ?
            ORDER BY growth DESC
            LIMIT ?
        ''', (prev_date, date, limit))

        return [dict(row) for row in cursor.fetchall()]


def get_database_stats(db_path: str = DEFAULT_DB_PATH) -> Dict:
    """
    获取数据库统计信息

    Args:
        db_path: 数据库路径

    Returns:
        统计信息字典
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        stats = {}

        # 视频总数
        cursor.execute('SELECT COUNT(*) as count FROM videos')
        stats['total_videos'] = cursor.fetchone()['count']

        # 演员总数
        cursor.execute('SELECT COUNT(*) as count FROM actors')
        stats['total_actors'] = cursor.fetchone()['count']

        # 有演员信息的视频数
        cursor.execute('SELECT COUNT(DISTINCT video_id) as count FROM video_actors')
        stats['videos_with_actors'] = cursor.fetchone()['count']

        # 数据日期范围
        cursor.execute('SELECT MIN(date) as min_date, MAX(date) as max_date FROM daily_stats')
        row = cursor.fetchone()
        stats['date_range'] = (row['min_date'], row['max_date'])

        return stats


if __name__ == '__main__':
    # 测试：初始化数据库
    print("测试数据库模块")
    print("=" * 60)

    # 使用测试数据库
    test_db = './test_analytics.db'

    # 删除旧的测试数据库
    if os.path.exists(test_db):
        os.remove(test_db)

    # 初始化
    init_database(test_db)

    # 插入测试数据
    print("\n插入测试数据...")
    today = datetime.now().strftime('%Y-%m-%d')

    test_videos = [
        {'video_id': 'test-001', 'title': '测试视频1', 'date': today, 'views': 10000, 'likes': 500},
        {'video_id': 'test-002', 'title': '测试视频2', 'date': today, 'views': 20000, 'likes': 800},
    ]

    bulk_insert_daily_stats(test_videos, test_db)

    # 插入演员数据
    print("插入演员数据...")
    bulk_insert_video_actors('test-001', [
        {'actor_id': 'actor-001', 'actor_name': '测试演员A'},
        {'actor_id': 'actor-002', 'actor_name': '测试演员B'}
    ], test_db)

    # 更新演员统计
    print("更新演员统计...")
    update_actor_daily_stats(today, test_db)

    # 查询统计
    print("\n数据库统计:")
    stats = get_database_stats(test_db)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ 数据库模块测试完成")

#!/usr/bin/python
# coding: utf-8

import argparse
from executor import process_subscription, process_videos, process_hot
import analytics_manager

parser = argparse.ArgumentParser(description="jable downloader and analytics")

sub_parser = parser.add_subparsers()

video_parser = sub_parser.add_parser("videos", help="download video by urls")
video_parser.add_argument("urls", metavar='N', type=str, nargs='+',
                          help="jable video urls to download")

video_parser.set_defaults(func=process_videos)

models_parser = sub_parser.add_parser("subscription",
                                      help="subscribe some topic(models or tags)/sync videos from subscriptions")

models_parser.add_argument("--add", type=str,  metavar='N', nargs='+', default=[],
                           help="add subscriptions by urls(support models/tags). "
                                "One sub containing multi urls means the intersection of urls.")
models_parser.add_argument("--get", action='store_true',
                           help="get current subscription")
models_parser.add_argument("--sync-videos", action='store_true',
                           help="download all subscription related videos")
models_parser.add_argument("--ids", type=int, metavar='N', nargs='+', default=[],
                           help="specify subscription ids to use to sync videos")

models_parser.set_defaults(func=process_subscription)

hot_parser = sub_parser.add_parser("hot",
                                    help="download top liked videos from https://jable.tv/hot/")

hot_parser.add_argument("--top", type=int, default=4,
                        help="number of top videos to download (default: 4)")
hot_parser.add_argument("--min-likes", type=int, default=2000,
                        help="minimum likes threshold (default: 2000)")

hot_parser.set_defaults(func=process_hot)

# ==================== 热门影片分析命令 ====================

def process_analyze_init(args):
    """处理初始化命令"""
    analytics_manager.initialize_hot_videos_analysis(
        db_path=args.db,
        max_pages=args.max_pages,
        top_n_for_actors=args.top_actors
    )


def process_analyze_update(args):
    """处理每日更新命令"""
    analytics_manager.daily_update_hot_videos(
        db_path=args.db,
        max_pages=args.max_pages,
        top_n_for_new_actors=args.top_actors
    )


def process_report(args):
    """处理榜单生成命令"""
    if args.send:
        # 生成并发送到 Telegram
        analytics_manager.send_growth_report_to_telegram(
            date=args.date,
            prev_date=args.prev_date,
            top_n=args.top,
            db_path=args.db
        )
    else:
        # 只生成榜单
        analytics_manager.generate_growth_report(
            date=args.date,
            prev_date=args.prev_date,
            top_n=args.top,
            db_path=args.db
        )


# analyze 命令：初始化和每日更新
analyze_parser = sub_parser.add_parser("analyze",
                                       help="analyze hot videos: initialize or daily update")

analyze_subparsers = analyze_parser.add_subparsers(dest='analyze_cmd')

# analyze init：初始化
init_parser = analyze_subparsers.add_parser("init",
                                           help="initialize: crawl all pages and fetch top N actors info")
init_parser.add_argument("--db", type=str, default="./analytics.db",
                        help="database path (default: ./analytics.db)")
init_parser.add_argument("--max-pages", type=int, default=None,
                        help="max pages to crawl (default: all pages)")
init_parser.add_argument("--top-actors", type=int, default=200,
                        help="fetch actors info for top N videos (default: 200)")
init_parser.set_defaults(func=process_analyze_init)

# analyze update：每日更新
update_parser = analyze_subparsers.add_parser("update",
                                              help="daily update: crawl all pages and update stats")
update_parser.add_argument("--db", type=str, default="./analytics.db",
                          help="database path (default: ./analytics.db)")
update_parser.add_argument("--max-pages", type=int, default=None,
                          help="max pages to crawl (default: all pages)")
update_parser.add_argument("--top-actors", type=int, default=200,
                          help="fetch actors info for new top N videos (default: 200)")
update_parser.set_defaults(func=process_analyze_update)

# report 命令：生成榜单
report_parser = sub_parser.add_parser("report",
                                     help="generate growth report and optionally send to Telegram")
report_parser.add_argument("--db", type=str, default="./analytics.db",
                          help="database path (default: ./analytics.db)")
report_parser.add_argument("--date", type=str, default=None,
                          help="target date (YYYY-MM-DD), default: today")
report_parser.add_argument("--prev-date", type=str, default=None,
                          help="previous date (YYYY-MM-DD), default: yesterday")
report_parser.add_argument("--top", type=int, default=50,
                          help="number of items in report (default: 50)")
report_parser.add_argument("--send", action='store_true',
                          help="send report to Telegram")
report_parser.set_defaults(func=process_report)


if __name__ == '__main__':
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        exit()

    args.func(args)

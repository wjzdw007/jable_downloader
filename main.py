#!/usr/bin/python
# coding: utf-8

import argparse
from executor import process_subscription, process_videos, process_hot

parser = argparse.ArgumentParser(description="jable downloader")

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


if __name__ == '__main__':
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        exit()

    args.func(args)

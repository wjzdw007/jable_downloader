import re
import time
import random

import config
import model_crawler
import utils
import video_crawler
import hot_crawler

CONF = config.CONF


def _add_subscription(input_urls):
    cur_subscription = []
    for input_url in input_urls:
        model_crawler.input_url_validator(input_url)
        name, _ = model_crawler.get_model_names_and_last_page_num(input_url)
        cur_subscription.append({'url': input_url, 'name': name})

    all_subs = CONF.get('subscriptions', [])

    for subs in all_subs:
        url_group = set()
        for sub_info in subs:
            url_group.add(sub_info['url'])
        if set(input_urls) == url_group:
            print("cur_subscription %s already exists." % subs)
            return

    all_subs.append(cur_subscription)
    CONF['subscriptions'] = all_subs
    config.update_config(CONF)
    print("add cur_subscription success.")
    print(cur_subscription)


def get_need_sync_video_ids(sub):
    # first update cache
    cache_info = utils.get_video_ids_map_from_cache()
    try:
        for item in sub:
            url = item['url']
            cached_video_ids = set(cache_info.get(url, set())) if cache_info else set()
            remote_video_id_set = model_crawler.get_all_video_ids(url, cached_video_ids)
            cache_info[url] = list(remote_video_id_set)
    except Exception:
        raise
    finally:
        utils.update_video_ids_cache(cache_info)

    need_sync_video_ids = set(cache_info[sub[0]['url']])
    for item in sub[1:]:
        url = item['url']
        need_sync_video_ids &= set(cache_info.get(url))
    return need_sync_video_ids


def print_all_subs(all_subs, print_url=False):
    if not all_subs:
        print("当前无任何订阅内容")
        return

    print("当前共%s个订阅，内容如下:" % len(all_subs))
    for index, subs in enumerate(all_subs):
        names = '-'.join([foo['name'] for foo in subs])
        if not print_url:
            print("%s\t: 订阅名: %s " % (index+1, names))
        else:
            urls = [foo['url'] for foo in subs]
            print("%s\t: 订阅名: %s\t\t订阅链接: %s" % (index+1, names, urls))


def process_subscription(args):
    if args.add:
        input_urls = args.add
        _add_subscription(input_urls)

    elif args.get:
        all_subs = CONF.get('subscriptions', [])
        print_all_subs(all_subs, print_url=True)
    elif args.sync_videos:
        all_subs = CONF.get('subscriptions', [])
        output_path = CONF.get("outputDir", './')
        if args.ids:
            all_subs = [all_subs[i-1] for i in args.ids if (1 <= i <= len(all_subs))]
        local_video_id_set = utils.get_local_video_list(path=output_path)
        block_video_ids = {str.lower(video_id) for video_id in config.CONF.get("videoIdBlockList", [])}
        ignore_video_ids = local_video_id_set | block_video_ids
        base_url = "https://jable.tv/videos/"

        download_inerval = CONF.get("downloadInterval", 1)
        print_all_subs(all_subs)

        for subs in all_subs:
            subs_name = '-'.join([foo['name'] for foo in subs])
            print("\n===================================")
            print("  同步订阅:\t%s" % subs_name)
            print("===================================\n")
            remote_video_id_set = get_need_sync_video_ids(subs)
            need_sync_video_ids = remote_video_id_set - ignore_video_ids
            need_sync_number = len(need_sync_video_ids)
            print("该订阅远端 %s 个 / 本地已存在 %s 个 " %
                  (len(remote_video_id_set), len(remote_video_id_set & ignore_video_ids)))

            # 将 set 转换为 list 并随机打乱顺序
            need_sync_video_list = list(need_sync_video_ids)
            random.shuffle(need_sync_video_list)
            print("🔀 已随机打乱下载顺序")

            print("开始同步 %s 的远端视频到本地..." % '-'.join([foo['name'] for foo in subs]))

            for index, video_id in enumerate(need_sync_video_list):
                print("\n该订阅需同步视频 %s 个 / 剩余 %s 个 " % (need_sync_number, need_sync_number - index))
                download_url = base_url + video_id + '/'
                # print(download_url)
                video_crawler.download_by_video_url(download_url)

                ignore_video_ids.add(video_id)
                if index < len(need_sync_video_list) - 1:
                    time.sleep(download_inerval)

            print("订阅 %s 同步完成" % subs_name)
        print("\n==所有订阅同步完成==\n")


def process_videos(args):
    video_urls = []
    for url in args.urls:
        if "videos" not in url:
            raise Exception("only support video url")
        if not url.endswith('/'):
            video_urls.append(url+'/')
        else:
            video_urls.append(url)

    output_path = CONF.get("outputDir", './')
    local_video_id_set = utils.get_local_video_list(path=output_path)
    block_video_ids = {str.lower(video_id) for video_id in config.CONF.get("videoIdBlockList", [])}
    ignore_video_ids = local_video_id_set | block_video_ids

    # 修正正则：匹配完整的视频 ID，包括所有后缀（如 -c, -cn 等）
    re_extractor = re.compile(r"[a-zA-Z0-9]{2,}-\d{3,}(?:-[a-zA-Z0-9]+)?")

    for video_url in video_urls:
        re_res = re_extractor.search(video_url)
        if re_res:
            video_id = re_res.group(0)
            if video_id and video_id in ignore_video_ids:
                print("视频 %s 已经下载，跳过该视频" % video_url)
                continue
            ignore_video_ids.add(video_id)
        video_crawler.download_by_video_url(video_url)


def process_hot(args):
    """
    处理热门视频下载命令

    Args:
        args: 命令行参数
            - top: 下载数量（默认 4）
            - min_likes: 最小点赞数（默认 2000）
    """
    top_n = args.top if hasattr(args, 'top') and args.top else 4
    min_likes = args.min_likes if hasattr(args, 'min_likes') and args.min_likes else 2000

    hot_crawler.download_hot_videos(top_n=top_n, min_likes=min_likes)

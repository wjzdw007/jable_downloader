import json
import os


CONF = {
    "downloadVideoCover": False,
    "downloadInterval": 0,
    "outputDir": "./",
    "outputFileFormat": 'title.mp4',
    "proxies": {},
    "save_vpn_traffic": False,
    "subscriptions": [],
    "videoIdBlockList": [],
    "headers": {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Referer": "https://jable.tv"
    },
    "sa_token": "",
    "sa_mode": "browser"
}


def get_config(conf_path='./config.json'):
    if not os.path.exists(conf_path):
        print(f"⚠️  配置文件不存在: {conf_path}")
        print(f"   将使用默认配置")
        print(f"   提示：可以从 config.example.json 复制创建配置文件")
        return

    with open(conf_path, 'r', encoding='utf8') as f:
        user_conf = json.load(f)

        # 深度合并 headers，保留默认的 User-Agent
        if 'headers' in user_conf:
            default_headers = CONF.get('headers', {}).copy()
            default_headers.update(user_conf['headers'])
            user_conf['headers'] = default_headers

        return CONF.update(user_conf)


def update_config(conf, conf_path='./config.json'):
    with open(conf_path, 'w', encoding='utf8') as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)


get_config()

headers = CONF.get("headers")

# jable_downloader
download jable tv tool

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
![Scrutinizer code quality (GitHub/Bitbucket)](https://img.shields.io/scrutinizer/quality/g/2niuhe/jable_downloader/main)
![Github_workflow](https://github.com/2niuhe/jable_downloader/actions/workflows/python-package.yml/badge.svg)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/2niuhe/jable_downloader)

![GitHub top language](https://img.shields.io/github/languages/top/2niuhe/jable_downloader)
![GitHub](https://img.shields.io/github/license/2niuhe/jable_downloader)
![Scrutinizer build (GitHub/Bitbucket)](https://img.shields.io/scrutinizer/build/g/2niuhe/jable_downloader/main)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/2niuhe/jable_downloader)
![GitHub Repo stars](https://img.shields.io/github/stars/2niuhe/jable_downloader?style=social)
![Github All Releases](https://img.shields.io/github/downloads/2niuhe/jable_downloader/total.svg)

---

## 🎯 重要更新 (2025-10-23)

**当前已切换到 Playwright 精简模式！** 🚀

- ✅ 使用系统 Chrome/Chromium 浏览器（不再使用 ChromeDP）
- ✅ 最小化干预，"零伪装"策略
- ✅ 远程服务器测试验证通过，成功率 90%+
- ✅ 不需要 ScrapingAnt Token

**详细说明**: 请查看 [CURRENT_MODE.md](CURRENT_MODE.md)

**快速开始**:
1. 安装 Playwright: `pip install playwright && playwright install chromium`
2. 配置系统浏览器路径到 `config.json` 中的 `chrome_path`
3. 运行: `xvfb-run -a python3 main.py subscription --sync-videos`

---

### Introduction
下载jable tv视频助手:heart_eyes:

支持功能：
- **指定视频url下载到指定目录**
- **添加订阅某女星或者类别的视频，将该影星或类别的视频同步下载到本地**
- **支持断点续传，支持防止重复下载**
- **支持配置代理**
- **支持下载视频完毕后下载封面**

### Usage

**使用方法**

> 为了绕过网站新的反爬机制，有以下两种使用方式：
> 1. 使用了第三方服务`https://app.scrapingant.com/`，你需要先到网站申请一个token，填到配置文件`config.json`到`sa_token`段中
> [申请token方法](https://github.com/2niuhe/jable_downloader/issues/10)
> 2. 如果`config.json`文件中不配置`sa_token`段，认为使用本地的chromedp下载，这中模式下需要从release中下载对应系统和cpu架构的chromedp_jable
> 文件，放到main.py同级目录，这种模式下需要电脑安装有chrome浏览器

TODO:

- [ ] 处理登录和VIP视频


```shell
# 安装依赖
pip install -r requirements.txt

# 配置网络代理见Config小节(可选)

# 查看帮助
python main.py --help

# 指定视频url下载，指定多个url会按队列逐个下载(下面url替换为自己的url)
python main.py videos  https://jable.tv/videos/111111/  https://jable.tv/videos/222222/


# 添加对某类别的订阅，如添加`桜空もも`的订阅，添加订阅不会发起下载
python main.py subscription --add https://jable.tv/models/sakura-momo/

# 添加对多类别交集的订阅，如下添加`桜空もも的中文字幕`的订阅，添加订阅不会发起下载
python main.py subscription --add https://jable.tv/models/sakura-momo/ https://jable.tv/categories/chinese-subtitle/
# 查看当前订阅
python main.py subscription --get
# 当前共18个订阅，内容如下:
# 1       : 订阅名: ***           订阅链接: ***
# ......
# 18       : 订阅名: ***           订阅链接: ***

# 下载/同步所有订阅内容到本地(会跳过目标目录里的已下载内容)
python main.py subscription --sync-videos
# 按顺序下载/同步指定订阅号(3和2)的内容到本地(会跳过目标目录里的已下载内容)
# 订阅号上查看订阅时显示的数字编号，不指定--ids默认同步下载所有订阅
python main.py subscription --sync-videos --ids 3 2 


# h265编码压缩视频(可选)(体积可以减少为原1/3，实测1.8G的视频可以压缩到500M，耗时30分钟)
ffmpeg -i input.mp4 -c:v libx265 -vtag hvc1 -c:a copy output.mkv
```

**使用帮助**

1. **下载完视频无法播放或者卡帧**
    - 解决方案1： 更换视频播放器，推荐[mpv播放器](https://mpv.io/installation/)
    - 解决方案2： 使用ffmpeg编码`ffmpeg -i input.mp4 -c:v libx264 -vtag hvc1 -c:a copy output.mp4`

### Config(Optional)

配置项(json文件)说明

> 配置文件提供程序自定义选项，并记录一些订阅信息，配置文件可选
> 读取配置文件的路径是执行命令的工作路径，文件名为config.json

- downloadVideoCover： 是否下载封面,默认不下载
- downloadInterval： 每个视频之间的下载间隔，默认0s
- outputDir：下载的输出目录，默认当前工作目录
- outputFileFormat: 下载文件的格式，默认是"title.mp4"，即视频标题作为文件名，可选配置如下:
    - "title.mp4": 默认值，即视频标题作为文件名 (**推荐**)
    - "id.mp4": 番号作为文件名
    - "id/title.mp4": 番号目录/视频标题.mp4 (创建子目录，番号作为子目录名，标题作为文件名) 
    - "id/id.mp4": 番号目录/番号.mp4 （创建子目录，番号作为子目录名，番号作为文件名)
- proxies: 网络代理配置(需要同时配置http和https)
- save_vpn_traffic: 节省vpn代理流量(默认不开启)，开启后，从CDN下载视频的请求优先不使用代理，请求失败重试时再使用代理，由于存在失败重试切换代理，可能降低下载速度
- subscriptions： 记录订阅的视频类别，支持models/tags等，建议通过命令行` python main.py subscription --add `添加
    - 添加订阅信息 `--add` 每次添加一个订阅，一个订阅`--add` 后添加多个url(url之间用空格分隔)表示是多个类型的交集
    - **订阅支持如下类型的url的任意组合**:
      - 女优:  https://jable.tv/models/sakura-momo/
      - 标签:  https://jable.tv/tags/flight-attendant/
      - 类型:  https://jable.tv/categories/chinese-subtitle/
      - 搜索:  https://jable.tv/search/天然美少女/
- videoIdBlockList: 需要跳过的番号列表，例如`["abc-123", "def-456"]`，默认为空
- headers: 自定义请求头，一般不需要改动
- sa_token: **可选值，scrapingant服务的token，必须要填一个有效的token**
- sa_mode: scrapingant服务的模式，推荐设为`browser`，可选值如下
    - `default`： 默认模式，每次请求消耗1个credit，免费用户每月10000个credit
    - `browser`： 浏览器模式，每次请求消耗10个credit，**能力更强**

*如下是订阅了桜空もも的中文字幕视频*

```json
{
    "downloadVideoCover": false,     
    "downloadInterval": 0,
    "outputDir": "./",
    "outputFileFormat": "",  
    "proxies": {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
    "save_vpn_traffic": false,
    "videoIdBlockList": [],
    "subscriptions": [
        [
            {
                "url": "https://jable.tv/models/sakura-momo/",
                "name": "桜空もも"
            },
            {
                "url": "https://jable.tv/categories/chinese-subtitle/",
                "name": "中文字幕"
            }
        ]
    ],
    "headers": {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
        "Referer": "https://jable.tv"
    },
    "sa_token": "paste your own token here",
    "sa_mode": "browser"
}
```

### Reference
[JableTVDownload](https://github.com/hcjohn463/JableTVDownload)

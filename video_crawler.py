import concurrent.futures
import io
import os
import pathlib
import re
import shutil
import time
from functools import partial

import m3u8
from Crypto.Cipher import AES
from bs4 import BeautifulSoup

import utils
from config import CONF

# 导入 Telegram 通知模块（如果存在）
try:
    from telegram_notifier import send_download_success_notification, send_download_error_notification
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

avoid_chars = ['/', '\\', '\t', '\n', '\r']

BUFFER_SIZE = 1024 * 1024 * 20  # 20MB
MAX_WORKER = 8

def get_video_full_name(video_id, html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    video_full_name = video_id

    for meta in soup.find_all("meta"):
        meta_content = meta.get("content")
        if not meta_content:
            continue
        # 精确匹配：video_id 必须在 meta_content 中作为完整单词出现
        # 支持分隔符：空格、横线、下划线等
        meta_lower = meta_content.lower()
        video_id_lower = video_id.lower()

        # 检查是否包含完整的 video_id（不是作为子串）
        # 例如：mide-938nggn 不应该匹配 mide-938
        if video_id_lower in meta_lower:
            # 确保匹配的是完整的 ID，检查前后字符
            idx = meta_lower.find(video_id_lower)
            before_char = meta_lower[idx-1] if idx > 0 else ' '
            after_idx = idx + len(video_id_lower)
            after_char = meta_lower[after_idx] if after_idx < len(meta_lower) else ' '

            # 视频 ID 的合法字符：字母、数字、横线
            # 前后字符不应该是这些字符（避免部分匹配）
            is_valid_id_char = lambda c: c.isalnum() or c == '-'
            if not (is_valid_id_char(before_char) or is_valid_id_char(after_char)):
                video_full_name = meta_content
                break

    if len(video_full_name.encode()) > 248:
        video_full_name = video_full_name[:50]

    # remove avoid char
    for char in avoid_chars:
        video_full_name = video_full_name.replace(char, '')

    return video_full_name


def get_cover(html_str, folder_path):
    soup = BeautifulSoup(html_str, "html.parser")
    cover_name = f"{os.path.basename(folder_path)}.jpg"
    cover_path = os.path.join(folder_path, cover_name)
    for meta in soup.find_all("meta"):
        meta_content = meta.get("content")
        if not meta_content:
            continue
        if "preview.jpg" not in meta_content:
            continue
        try:
            r = utils.requests_with_retry(meta_content)
            with open(cover_path, "wb") as cover_fh:
                r.raw.decode_content = True
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        cover_fh.write(chunk)
        except Exception as e:
            print(f"unable to download cover: {e}")

    print(f"cover downloaded as {cover_name}")


def prepare_output_dir():
    output_dir = CONF.get("outputDir")
    if not output_dir or output_dir == "./":
        output_dir = os.getcwd()
    else:
        os.makedirs(output_dir, exist_ok=True)
    return output_dir


def mv_video_and_download_cover(output_dir, video_id, video_full_name, html_str):
    src_file_name = os.path.join(output_dir, video_full_name + '.mp4')
    dest_dir_name = output_dir
    output_format = CONF.get('outputFileFormat', '')
    if output_format == 'id/id.mp4':
        dest_dir_name = os.path.join(output_dir, video_id)
        os.makedirs(dest_dir_name, exist_ok=True)
        dst_filename = os.path.join(dest_dir_name, video_id + '.mp4')
        shutil.move(src_file_name, dst_filename)
    elif output_format == 'id/title.mp4':
        dest_dir_name = os.path.join(output_dir, video_id)
        os.makedirs(dest_dir_name, exist_ok=True)
        dst_filename = os.path.join(dest_dir_name, video_full_name + '.mp4')
        shutil.move(src_file_name, dst_filename)
    elif output_format == 'id.mp4':
        dst_filename = os.path.join(output_dir, video_id + '.mp4')
        shutil.move(src_file_name, dst_filename)

    if CONF.get("downloadVideoCover", True):
        get_cover(html_str, folder_path=dest_dir_name)


def download_by_video_url(url):
    video_id = url.split('/')[-2]
    start_time = time.time()  # 记录开始时间

    output_dir = prepare_output_dir()

    print(f"[1/5] 正在访问视频页面: {video_id}")
    page_str = utils.scrapingant_requests_get(url, retry=5)

    print(f"[2/5] 正在解析视频信息...")
    video_full_name = get_video_full_name(video_id, page_str)

    all_filenames = [file.name for file in pathlib.Path(output_dir).rglob('*.mp4')]
    if video_full_name + '.mp4' in all_filenames or video_id + '.mp4' in all_filenames:
        print(video_full_name + " 已经存在，跳过下载")
        return

    print(f"[3/5] 开始下载: {video_full_name}")

    # 使用非贪婪匹配，避免匹配过多内容
    # 匹配 https://...任意字符.../.m3u8 (可能带查询参数)
    result = re.search(r'https://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?', page_str)
    if not result:
        print("✗ 获取下载链接失败，跳过")
        return
    m3u8url = result[0].strip('"\'')  # 去除可能的引号
    print(f"  ✓ 找到视频源")
    print(f"     URL: {m3u8url}")

    m3u8url_list = m3u8url.split('/')
    m3u8url_list.pop(-1)
    download_url = '/'.join(m3u8url_list)
    m3u8file = os.path.join(output_dir, video_id + '.m3u8')

    print(f"[4/5] 正在解析视频播放列表...")
    print(f"  - 正在下载 m3u8 文件: {m3u8url.split('/')[-1]}")
    try:
        # 使用视频页面URL作为Referer
        headers_with_referer = CONF.get("headers", {}).copy()
        headers_with_referer['Referer'] = url
        response = utils.requests_with_retry(m3u8url, headers=headers_with_referer, retry=5)
        print(f"  ✓ m3u8 文件下载成功")
    except Exception as e:
        error_msg = str(e)
        print(f"  ✗ m3u8 文件下载失败: {error_msg[:100]}")

        # 如果是 410 错误，提供详细的诊断信息
        if "410" in error_msg or "Gone" in error_msg:
            print(f"  ")
            print(f"  ❌ 链接已过期（HTTP 410 Gone）")
            print(f"  ")
            print(f"  可能的原因:")
            print(f"    1. 服务器时间不准确（最常见）")
            print(f"       运行: ./check_server_time.sh 检查时间")
            print(f"       运行: sudo ntpdate -u time.nist.gov 同步时间")
            print(f"    ")
            print(f"    2. 视频链接包含时间戳，有效期已过")
            print(f"       - CDN 链接通常只在获取后几分钟到几小时内有效")
            print(f"       - 确保从获取页面到下载之间没有长时间延迟")
            print(f"    ")
            print(f"    3. 页面可能被缓存")
            print(f"       - 清除浏览器缓存")
            print(f"       - 强制刷新页面")
        else:
            print(f"  完整URL: {m3u8url}")
            print(f"  提示: 视频链接可能已失效，或需要代理访问CDN")

        raise

    with open(m3u8file, 'wb') as f:
        f.write(response.content)

    print(f"  - 正在解析播放列表...")
    m3u8obj = m3u8.load(m3u8file)
    m3u8uri = ''
    m3u8iv = ''
    os.remove(m3u8file)

    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv

    ts_list = []
    for seg in m3u8obj.segments:
        ts_url = download_url + '/' + seg.uri
        ts_list.append(ts_url)

    print(f"  ✓ 找到 {len(ts_list)} 个视频片段")

    if m3u8uri:
        print(f"  ✓ 视频已加密，正在获取解密密钥...")
        m3u8key_url = download_url + '/' + m3u8uri

        # 使用相同的完整请求头
        response = utils.requests_with_retry(m3u8key_url, headers=headers_with_referer)
        content_key = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()

        ci = AES.new(content_key, AES.MODE_CBC, vt)
        print(f"  ✓ 解密密钥获取成功")
    else:
        ci = ''
        print(f"  ℹ 视频未加密")

    print(f"[5/5] 开始下载视频片段...")
    try:
        download_m3u8_video(ci, output_dir, ts_list, video_full_name, headers_with_referer)

        print(f"正在保存文件...")
        mv_video_and_download_cover(output_dir, video_id, video_full_name, page_str)

        # 计算文件大小和下载耗时
        output_format = CONF.get('outputFileFormat', '')
        if output_format == 'id/id.mp4':
            video_path = os.path.join(output_dir, video_id, video_id + '.mp4')
        elif output_format == 'id/title.mp4':
            video_path = os.path.join(output_dir, video_id, video_full_name + '.mp4')
        elif output_format == 'id.mp4':
            video_path = os.path.join(output_dir, video_id + '.mp4')
        else:
            video_path = os.path.join(output_dir, video_full_name + '.mp4')

        file_size = os.path.getsize(video_path) if os.path.exists(video_path) else None
        duration = time.time() - start_time

        print(f"✓ 下载完成: {video_full_name}")

        # 发送 Telegram 通知
        if TELEGRAM_AVAILABLE:
            send_download_success_notification(video_id, video_full_name, file_size, duration)

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)[:200]
        print(f"✗ 下载失败: {error_msg}")

        # 发送失败通知
        if TELEGRAM_AVAILABLE:
            send_download_error_notification(video_id, video_full_name, error_msg)

        raise


def scrape(ci, url, headers=None):
    try:
        ignore_proxy = CONF.get("save_vpn_traffic")
        # 使用传入的 headers，如果没有则使用默认的
        if headers is None:
            headers = CONF.get("headers", {})
        response = utils.requests_with_retry(url, headers=headers, retry=5, ignore_proxy=ignore_proxy)
    except Exception as e:
        print(e)
        return None

    content_ts = response.content
    if ci:
        try:
            # 检查数据长度，如果不是16的倍数，可能是网络问题导致的不完整数据
            if len(content_ts) % 16 != 0:
                print(f"数据长度异常: {url}, 长度: {len(content_ts)}, 不是16的倍数")
                # 尝试重新下载一次
                try:
                    response = utils.requests_with_retry(url, headers=headers, retry=3, ignore_proxy=ignore_proxy)
                    content_ts = response.content
                    if len(content_ts) % 16 != 0:
                        print(f"重试后数据仍然异常: {url}, 长度: {len(content_ts)}")
                        return None
                except Exception as retry_e:
                    print(f"重试下载失败: {url}, 错误: {str(retry_e)}")
                    return None
            
            content_ts = ci.decrypt(content_ts)
        except ValueError as e:
            print(f"解密失败: {url}, 错误: {str(e)}")
            return None
        except Exception as e:
            print(f"解密异常: {url}, 错误: {str(e)}")
            return None
    return content_ts

def download_m3u8_video(ci, output_dir, ts_list: list, video_full_name, headers=None):
    buffer = io.BytesIO()
    tmp_video_filename = os.path.join(output_dir, video_full_name + ".tmp")
    target_video_filename = os.path.join(output_dir, video_full_name + ".mp4")
    log_filename = os.path.join(output_dir, video_full_name + ".log")

    last_ts = ''
    if os.path.exists(log_filename):
        with open(log_filename) as log_f:
            last_ts = log_f.readline()

    tmp_video_open_mode = 'wb'
    if last_ts in ts_list and os.path.exists(tmp_video_filename):
        index_start = ts_list.index(last_ts) + 1
        print('已经下载 %s 个文件, 开始断点续传...' % index_start)
        ts_list = ts_list[index_start:]
        tmp_video_open_mode = 'ab'
    
    download_list = ts_list
    start_time = time.time()
    failed_count = 0
    print('开始下载 ' + str(len(download_list)) + ' 个文件..', end='')
    print('预计等待时间: {0:.2f} 分钟 视视频大小和网络速度而定)'.format(len(download_list) / 150))


    with open(tmp_video_filename, tmp_video_open_mode) as file, open(log_filename, 'w') as log_f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            results = executor.map(partial(scrape, ci, headers=headers), download_list)
            total_num = len(download_list)
            for i, result in enumerate(results):
                if result is not None:
                    print('\r当前下载: {0} , 剩余 {1} 个, 失败: {2} 个'.format(
                        i+1, total_num-i-1, failed_count), end='', flush=True)

                    buffer.write(result)
                    # Adjust the buffer size as needed
                    if buffer.tell() >= BUFFER_SIZE:  # Example: 1MB buffer
                        buffer.seek(0)
                        file.write(buffer.read())
                        buffer.seek(0)
                        buffer.truncate()
                        log_f.write(download_list[i])
                        log_f.seek(0)
                else:
                    failed_count += 1
                    print(f"\n片段 {i+1} 处理失败，跳过 (失败总数: {failed_count})")

        # Write any remaining data in the buffer to the file
        buffer.seek(0)
        file.write(buffer.read())

    # 检查失败率，如果失败太多则给出警告
    failure_rate = (failed_count / total_num) * 100
    if failure_rate > 10:  # 失败率超过10%
        print(f"\n警告: 下载失败率较高 ({failure_rate:.1f}%), 视频可能不完整")
        print(f"成功: {total_num - failed_count} 个片段, 失败: {failed_count} 个片段")
    
    shutil.move(tmp_video_filename, target_video_filename)
    os.remove(log_filename)
    end_time = time.time()
    print('\n消耗 {0:.2f} 分钟 同步1个视频完成 !'.format((end_time - start_time) / 60))

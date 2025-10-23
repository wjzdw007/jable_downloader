#!/usr/bin/env python3
"""
测试视频链接的新鲜度 - 检查从页面获取的 m3u8 链接是否立即可用
"""

import re
import requests
import time
from datetime import datetime

video_url = "https://jable.tv/videos/abf-274/"

print("=" * 80)
print("测试视频链接新鲜度")
print("=" * 80)
print()

# 步骤 1: 获取视频页面
print("步骤 1: 获取视频页面")
print("-" * 80)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

try:
    print(f"正在访问: {video_url}")
    start_time = time.time()
    response = requests.get(video_url, headers=headers, timeout=30)
    elapsed = time.time() - start_time

    print(f"✓ 状态码: {response.status_code}")
    print(f"✓ 耗时: {elapsed:.2f} 秒")
    print(f"✓ 内容长度: {len(response.text)} 字节")

    html = response.text

except Exception as e:
    print(f"✗ 失败: {str(e)}")
    exit(1)

print()

# 步骤 2: 提取 m3u8 链接
print("步骤 2: 提取 m3u8 链接")
print("-" * 80)

result = re.search(r'https://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?', html)
if not result:
    print("✗ 未找到 m3u8 链接")
    exit(1)

m3u8_url = result[0].strip('"\'')
print(f"✓ 找到链接: {m3u8_url}")
print()

# 步骤 3: 分析链接结构
print("步骤 3: 分析链接结构")
print("-" * 80)

parts = m3u8_url.split('/')
if len(parts) >= 6:
    print(f"域名: {parts[2]}")
    print(f"Token: {parts[4]}")
    print(f"时间戳: {parts[5]}")

    try:
        timestamp = int(parts[5])
        current_time = int(time.time())
        diff = timestamp - current_time

        print(f"当前时间戳: {current_time}")
        print(f"链接时间戳: {timestamp}")
        print(f"当前时间: {datetime.fromtimestamp(current_time)}")
        print(f"过期时间: {datetime.fromtimestamp(timestamp)}")
        print(f"剩余有效期: {diff} 秒 ({diff/3600:.2f} 小时)")

        if diff < 0:
            print("⚠️ 警告: 链接已过期！")
        elif diff < 300:  # 5分钟
            print("⚠️ 警告: 链接即将过期（< 5分钟）")
        elif diff < 3600:  # 1小时
            print("✓ 链接还有效（< 1小时）")
        else:
            print("✓ 链接有效期充足")
    except Exception as e:
        print(f"无法解析时间戳: {e}")

print()

# 步骤 4: 立即测试下载
print("步骤 4: 立即测试下载（模拟正常流程）")
print("-" * 80)

download_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Referer": video_url
}

try:
    print("正在下载 m3u8 文件...")
    start_time = time.time()
    response = requests.get(m3u8_url, headers=download_headers, timeout=30)
    elapsed = time.time() - start_time

    print(f"状态码: {response.status_code}")
    print(f"耗时: {elapsed:.2f} 秒")

    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)} 字节")
        print(f"前 200 字符:")
        print(response.text[:200])
    elif response.status_code == 410:
        print(f"❌ 410 Gone - 链接已过期")
    elif response.status_code == 403:
        print(f"❌ 403 Forbidden - 权限不足")
        print(f"可能需要的头部:")
        print(f"  - Referer: {video_url}")
        print(f"  - User-Agent: (现代浏览器)")
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

print()

# 步骤 5: 延迟后测试（模拟可能的延迟）
print("步骤 5: 5秒延迟后测试")
print("-" * 80)
print("等待 5 秒...")
time.sleep(5)

try:
    response = requests.get(m3u8_url, headers=download_headers, timeout=30)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        print(f"✅ 仍然有效")
    elif response.status_code == 410:
        print(f"❌ 已过期（5秒后）")
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
print()
print("结论:")
print("如果立即下载成功，但5秒后失败 => 链接有效期很短")
print("如果立即下载就失败 => 页面上的链接本身已过期")
print("如果都成功 => 链接有效，问题可能在其他地方")

#!/usr/bin/env python3
"""
测试 m3u8 文件下载，分析 403 错误的原因
"""

import requests
import time

# 测试 URL（从用户的错误信息中获取）
test_url = "https://adoda-smart-coin.mushroomtrack.com/hls/54Y8cBjAIYwGQNCz8iNY9A/1761241870/54000/54211/54211.m3u8"
video_page_url = "https://jable.tv/videos/abf-274/"

print("=" * 80)
print("测试 m3u8 文件下载 - 403 错误分析")
print("=" * 80)
print()

# 测试 1: 无任何头部
print("测试 1: 无任何头部")
print("-" * 80)
try:
    response = requests.get(test_url, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
    else:
        print(f"❌ 失败: {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 2: 只有基础 User-Agent
print("测试 2: 只有基础 User-Agent (Firefox 105)")
print("-" * 80)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}
try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
    else:
        print(f"❌ 失败: {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 3: User-Agent + Referer (jable.tv)
print("测试 3: User-Agent + Referer (https://jable.tv)")
print("-" * 80)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Referer": "https://jable.tv"
}
try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
    else:
        print(f"❌ 失败: {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 4: User-Agent + Referer (视频页面)
print("测试 4: User-Agent + Referer (视频页面)")
print("-" * 80)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Referer": video_page_url
}
try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
        print(f"前 200 字符: {response.text[:200]}")
    else:
        print(f"❌ 失败: {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 5: 现代 Chrome User-Agent + Referer (视频页面)
print("测试 5: 现代 Chrome User-Agent + Referer (视频页面)")
print("-" * 80)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": video_page_url
}
try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
        print(f"前 200 字符: {response.text[:200]}")
    else:
        print(f"❌ 失败: {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 6: 完整的浏览器头部 + Referer (视频页面)
print("测试 6: 完整的浏览器头部")
print("-" * 80)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": video_page_url,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://jable.tv",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site"
}
try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功！内容长度: {len(response.content)}")
        print(f"前 200 字符: {response.text[:200]}")
    else:
        print(f"❌ 失败: {response.status_code}")
        print(f"响应头部: {dict(response.headers)}")
except Exception as e:
    print(f"❌ 异常: {str(e)[:100]}")
print()

# 测试 7: 检查链接是否已过期（时间戳）
print("测试 7: 分析 URL 结构")
print("-" * 80)
print(f"URL: {test_url}")
print()
parts = test_url.split('/')
if len(parts) >= 6:
    print(f"域名: {parts[2]}")
    print(f"Token: {parts[4]}")
    print(f"时间戳: {parts[5]}")

    # 检查时间戳
    try:
        timestamp = int(parts[5])
        current_time = int(time.time())
        diff = timestamp - current_time

        print(f"当前时间戳: {current_time}")
        print(f"链接时间戳: {timestamp}")
        print(f"时间差: {diff} 秒 ({diff/3600:.2f} 小时)")

        if diff < 0:
            print("⚠️ 警告: 链接可能已过期（时间戳在过去）")
        elif diff > 86400:  # 24小时
            print("✓ 链接有效期充足")
        else:
            print(f"✓ 链接还有 {diff/3600:.2f} 小时有效期")
    except:
        print("无法解析时间戳")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)

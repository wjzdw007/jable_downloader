#!/usr/bin/env python3
"""
使用 Playwright 测试链接时效性
模拟实际使用场景
"""

import re
import requests
import time
from datetime import datetime

# 模拟从用户的实际场景中获取
# 这是一个刚刚过期的链接
test_url_old = "https://anono-cloneing.mushroomtrack.com/hls/ZUs_fJVfSsWuuNdOzpo3hw/1761173802/54000/54211/54211.m3u8"

print("=" * 80)
print("分析 m3u8 链接时效性")
print("=" * 80)
print()

# 分析旧链接的时间戳
print("分析示例链接（来自用户报错）:")
print("-" * 80)
print(f"URL: {test_url_old}")
print()

parts = test_url_old.split('/')
if len(parts) >= 6:
    token = parts[4]
    timestamp_str = parts[5]

    print(f"Token: {token}")
    print(f"时间戳: {timestamp_str}")

    try:
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        diff = timestamp - current_time

        print(f"链接过期时间: {datetime.fromtimestamp(timestamp)}")
        print(f"当前时间: {datetime.fromtimestamp(current_time)}")
        print(f"时间差: {diff} 秒 ({diff/3600:.2f} 小时)")

        if diff < 0:
            print(f"❌ 链接已过期 {abs(diff/3600):.2f} 小时")
        else:
            print(f"✅ 链接还有 {diff/3600:.2f} 小时有效期")
    except Exception as e:
        print(f"无法解析时间戳: {e}")

print()

# 测试当前状态
print("测试当前状态:")
print("-" * 80)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Referer": "https://jable.tv/videos/abf-274/"
}

try:
    response = requests.get(test_url_old, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        print("✅ 可以访问")
    elif response.status_code == 403:
        print("❌ 403 Forbidden")
    elif response.status_code == 410:
        print("❌ 410 Gone (链接已过期)")
    else:
        print(f"❌ {response.status_code}")
except Exception as e:
    print(f"❌ 请求失败: {str(e)[:100]}")

print()

# 分析可能的原因
print("=" * 80)
print("问题分析:")
print("=" * 80)
print()

print("1. 链接结构:")
print("   https://domain/hls/TOKEN/TIMESTAMP/path/to/file.m3u8")
print("   - TOKEN: 动态生成的访问令牌")
print("   - TIMESTAMP: Unix 时间戳，表示链接过期时间")
print()

print("2. 可能的原因:")
print()

print("   原因 A: 链接有效期很短")
print("   - 从页面获取链接到实际下载之间，链接可能已过期")
print("   - CDN 设置了很短的有效期（例如几分钟）")
print("   - 解决方案: 获取页面后立即下载，不要延迟")
print()

print("   原因 B: 服务器时间不同步")
print("   - 如果服务器时间比实际时间慢")
print("   - CDN 会认为请求来自'未来'，拒绝访问")
print("   - 解决方案: 同步服务器时间")
print()

print("   原因 C: 页面可能被缓存")
print("   - 如果页面来自缓存（CDN 或浏览器缓存）")
print("   - 链接在缓存时就已经过期")
print("   - 解决方案: 强制刷新页面，不使用缓存")
print()

print("   原因 D: 重试机制导致的延迟")
print("   - 代码中的重试机制会等待（10+20+30+30=90秒）")
print("   - 如果链接原本还有效，重试期间可能过期")
print("   - 解决方案: 如果是 410，不要重试")
print()

print("3. 建议的解决方案:")
print()
print("   1) 检查服务器时间是否准确")
print("      命令: date")
print("      如果不准确: sudo ntpdate -u time.nist.gov")
print()
print("   2) 修改代码，对 410 状态码不重试")
print("      410 = Gone (永久消失)，重试无意义")
print()
print("   3) 获取页面时强制不使用缓存")
print("      添加 headers: 'Cache-Control': 'no-cache'")
print()
print("   4) 从页面获取链接后立即下载")
print("      减少中间步骤的延迟")
print()

print("=" * 80)

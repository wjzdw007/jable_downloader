#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的浏览器模拟功能
包括：HTTP 头部、Cookie 管理、JavaScript 特征隐藏
"""

import json
import os
from utils import get_response_from_playwright

def test_browser_simulation():
    """测试浏览器模拟"""

    test_url = "https://jable.tv/models/851cf1602f37c2611917b675f2d432c7/"

    print("="*60)
    print("🧪 浏览器模拟功能测试")
    print("="*60)
    print()
    print("📍 测试 URL:", test_url)
    print()

    # 显示当前配置
    print("🔧 当前配置：")
    print("  ✓ 完整的 HTTP 头部（Sec-Ch-Ua, Sec-Fetch-* 等）")
    print("  ✓ Cookie 持久化管理")
    print("  ✓ JavaScript 自动化特征隐藏")
    print("  ✓ 真实用户行为模拟（鼠标、滚动）")
    print("  ✓ 随机视口大小")
    print("  ✓ zh-TW 语言和时区")
    print()

    # 检查是否存在旧的 Cookie
    cookie_file = '.jable_cookies.json'
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            print(f"📦 发现已保存的 {len(cookies)} 个 Cookie，将在请求中使用")
            print()
    else:
        print("📦 未发现已保存的 Cookie，将在首次请求后保存")
        print()

    print("-"*60)
    print("🚀 开始测试...")
    print("-"*60)
    print()

    try:
        # 调用 Playwright 获取页面
        html = get_response_from_playwright(test_url)

        print()
        print("-"*60)
        print("📊 测试结果分析")
        print("-"*60)
        print()

        # 检查是否成功
        if 'Just a moment' in html or 'Verify you are human' in html or '請稍候' in html:
            print("❌ 仍然遇到 Cloudflare 验证页面")
            print()
            print("💡 可能的解决方案：")
            print("  1. 配置住宅代理（推荐）")
            print("  2. 使用 ScrapingAnt 服务")
            print("  3. 等待更长时间让验证自动完成")
            return False
        else:
            print("✅ 成功绕过 Cloudflare 验证！")
            print()

            # 检查演员名称
            if 'h3-md mb-1' in html or 'h2.h3-md.mb-1' in html:
                # 尝试提取演员名称
                import re
                name_pattern = r'<h2[^>]*class="[^"]*h3-md[^"]*"[^>]*>(.*?)</h2>'
                match = re.search(name_pattern, html)
                if match:
                    name = match.group(1).strip()
                    print(f"👤 成功获取演员名称: {name}")
                else:
                    print("👤 页面包含演员名称元素，但需要进一步解析")

            print()
            print("📈 页面信息：")
            print(f"  - HTML 长度: {len(html)} 字符")
            print(f"  - 包含 '#site-header': {'是' if '#site-header' in html else '否'}")
            print(f"  - 包含 'video-img': {'是' if 'video-img' in html else '否'}")

            # 检查 Cookie
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    print(f"  - 已保存 Cookie: {len(cookies)} 个")

                    # 显示 Cloudflare Cookie
                    cf_cookies = [c for c in cookies if 'cf_' in c.get('name', '').lower()]
                    if cf_cookies:
                        print(f"  - Cloudflare Cookie: {len(cf_cookies)} 个")
                        for cookie in cf_cookies:
                            print(f"    • {cookie['name']}")

            return True

    except Exception as e:
        print()
        print(f"❌ 测试失败: {str(e)[:200]}")
        return False


def show_headers_info():
    """显示发送的 HTTP 头部信息"""
    import platform

    print()
    print("="*60)
    print("📋 实际使用的 HTTP 头部（自动适配）")
    print("="*60)
    print()

    # 自动检测操作系统（与 utils.py 一致）
    system = platform.system()
    if system == 'Linux':
        platform_name = 'Linux'
        print("🖥️  检测到 Linux 系统")
    elif system == 'Darwin':
        platform_name = 'macOS'
        print("🖥️  检测到 macOS 系统")
    elif system == 'Windows':
        platform_name = 'Windows'
        print("🖥️  检测到 Windows 系统")
    else:
        platform_name = 'Linux'
        print("🖥️  检测到未知系统，使用 Linux 配置")

    print()
    print("✅ 已自动适配头部：")
    print()

    headers = {
        'User-Agent': '（使用浏览器默认的，包含真实版本号）',
        'sec-ch-ua': '（使用浏览器默认的，包含真实版本号）',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': f'"{platform_name}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
    }

    for key, value in headers.items():
        print(f"  {key}: {value}")

    print()
    print("💡 注意：User-Agent 和 sec-ch-ua 使用浏览器真实版本，不硬编码")
    print()


if __name__ == '__main__':
    show_headers_info()
    success = test_browser_simulation()

    print()
    print("="*60)
    if success:
        print("✅ 测试完成！浏览器模拟工作正常")
    else:
        print("⚠️ 测试完成，但仍需要改进")
    print("="*60)
    print()

    # 显示 Cookie 文件位置
    cookie_file = '.jable_cookies.json'
    if os.path.exists(cookie_file):
        abs_path = os.path.abspath(cookie_file)
        print(f"💾 Cookie 已保存到: {abs_path}")
        print()

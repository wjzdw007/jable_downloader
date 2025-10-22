#!/usr/bin/env python3
# coding: utf-8

"""
测试和比较浏览器请求头
"""

from __future__ import print_function
import sys
import json

def compare_headers():
    """比较不同浏览器的请求头特征"""
    print("=" * 60)
    print("浏览器请求头分析")
    print("=" * 60)
    print()

    # 真实 Chrome 浏览器的请求头（手机）
    real_mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?1',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    # 真实桌面 Chrome 的请求头
    real_desktop_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    # Playwright 的默认请求头
    playwright_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    print("=== 真实移动浏览器（手机） ===")
    for key, value in real_mobile_headers.items():
        print("  {}: {}".format(key, value[:80]))
    print()

    print("=== 真实桌面浏览器 ===")
    for key, value in real_desktop_headers.items():
        print("  {}: {}".format(key, value[:80]))
    print()

    print("=== Playwright 默认 ===")
    for key, value in playwright_headers.items():
        print("  {}: {}".format(key, value[:80]))
    print()

    print("=" * 60)
    print("关键差异")
    print("=" * 60)
    print()

    print("1. Sec-Ch-Ua 头（Client Hints）")
    print("   真实: 包含浏览器品牌信息")
    print("   Playwright: 可能缺失或不正确")
    print()

    print("2. Sec-Fetch-* 头（Fetch Metadata）")
    print("   真实: Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site, Sec-Fetch-User")
    print("   Playwright: 可能缺失")
    print()

    print("3. Accept-Language")
    print("   真实: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")
    print("   Playwright: en-US,en;q=0.9")
    print()

    print("4. Accept")
    print("   真实: 包含 application/signed-exchange;v=b3;q=0.7")
    print("   Playwright: 可能缺失")
    print()

    print("=" * 60)
    print("建议的请求头配置")
    print("=" * 60)
    print()

    recommended_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    print("推荐配置（config.json）:")
    print()
    print(json.dumps({'headers': recommended_headers}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    compare_headers()

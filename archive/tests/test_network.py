#!/usr/bin/env python3
# coding: utf-8

"""
网络连接测试 - 诊断下载问题
"""

import requests
import time

def test_connection():
    """测试网络连接"""
    print("=" * 60)
    print("网络连接诊断")
    print("=" * 60)
    print()

    # 测试1: 测试 jable.tv 主页
    print("[测试 1] jable.tv 主页访问")
    try:
        response = requests.get("https://jable.tv/", timeout=10)
        if response.status_code == 200:
            print(f"  ✓ 成功 (状态码: {response.status_code})")
        else:
            print(f"  ✗ 失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"  ✗ 失败: {str(e)[:100]}")

    print()

    # 测试2: 测试 CDN 访问（使用一个示例 CDN URL）
    print("[测试 2] CDN 资源访问")
    cdn_url = "https://assets-cdn.jable.tv/assets/icon/favicon.png"
    try:
        start = time.time()
        response = requests.get(cdn_url, timeout=10)
        elapsed = time.time() - start
        if response.status_code == 200:
            print(f"  ✓ 成功 (状态码: {response.status_code}, 耗时: {elapsed:.2f}秒)")
            print(f"  ✓ 下载大小: {len(response.content)} 字节")
        else:
            print(f"  ✗ 失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"  ✗ 失败: {str(e)[:100]}")
        print(f"  提示: CDN访问失败可能需要配置代理")

    print()

    # 测试3: 使用代理测试
    print("[测试 3] 代理配置测试")
    proxy_configs = [
        {"http": "http://127.0.0.1:1081", "https": "http://127.0.0.1:1081"},
        {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"},
    ]

    for idx, proxies in enumerate(proxy_configs, 1):
        print(f"  测试代理 {idx}: {proxies['http']}")
        try:
            response = requests.get(cdn_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                print(f"    ✓ 代理可用")
                print(f"    建议: 在 config.json 中配置此代理")
                print(f'    "proxies": {{"http": "{proxies["http"]}", "https": "{proxies["https"]}"}}')
                break
            else:
                print(f"    ✗ 代理不可用 (状态码: {response.status_code})")
        except Exception as e:
            print(f"    ✗ 代理连接失败: {str(e)[:80]}")

    print()
    print("=" * 60)
    print("诊断完成")
    print("=" * 60)
    print()
    print("建议:")
    print("1. 如果CDN访问失败，请配置代理")
    print("2. 在 config.json 中设置 proxies 字段")
    print("3. 确保代理服务正在运行")
    print()

if __name__ == '__main__':
    test_connection()

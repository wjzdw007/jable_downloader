#!/usr/bin/env python3
# coding: utf-8

"""
检查代理配置和网络状态
"""

from __future__ import print_function
import os
import sys
import json
import requests

def check_proxy():
    """检查代理配置"""
    print("=" * 60)
    print("代理和网络配置检查")
    print("=" * 60)
    print()

    # 1. 检查环境变量
    print("=== 系统环境变量 ===")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                  'NO_PROXY', 'no_proxy']

    has_env_proxy = False
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print("  {} = {}".format(var, value))
            has_env_proxy = True

    if not has_env_proxy:
        print("  (未设置)")
    print()

    # 2. 检查 config.json
    print("=== config.json 配置 ===")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        proxies = config.get('proxies', {})
        if proxies:
            print("  已配置代理:")
            for key, value in proxies.items():
                print("    {} = {}".format(key, value))
        else:
            print("  未配置代理")
    except FileNotFoundError:
        print("  config.json 不存在")
    except Exception as e:
        print("  读取失败: {}".format(e))
    print()

    # 3. 检查实际出口 IP
    print("=== 网络出口 IP ===")

    # 不使用代理
    try:
        print("  不使用代理:")
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_data = response.json()
        print("    IP: {}".format(ip_data.get('ip', 'Unknown')))
    except Exception as e:
        print("    获取失败: {}".format(str(e)[:50]))

    # 使用 config.json 中的代理
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        proxies = config.get('proxies', {})

        if proxies:
            print()
            print("  使用 config.json 代理:")
            response = requests.get('https://api.ipify.org?format=json',
                                   proxies=proxies, timeout=10)
            ip_data = response.json()
            print("    IP: {}".format(ip_data.get('ip', 'Unknown')))
    except Exception as e:
        if proxies:
            print("    获取失败: {}".format(str(e)[:50]))
    print()

    # 4. 测试访问 jable.tv
    print("=== 测试访问 jable.tv ===")

    # 不使用代理
    try:
        print("  不使用代理:")
        response = requests.head('https://jable.tv', timeout=10,
                                allow_redirects=True)
        print("    状态码: {}".format(response.status_code))

        # 检查是否是 Cloudflare 验证页面
        if response.status_code == 200:
            test_response = requests.get('https://jable.tv', timeout=10)
            if 'Just a moment' in test_response.text or 'Verify you are human' in test_response.text:
                print("    结果: Cloudflare 验证页面")
            else:
                print("    结果: 正常访问")
    except Exception as e:
        print("    访问失败: {}".format(str(e)[:50]))

    # 使用代理
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        proxies = config.get('proxies', {})

        if proxies:
            print()
            print("  使用 config.json 代理:")
            response = requests.head('https://jable.tv', proxies=proxies,
                                    timeout=10, allow_redirects=True)
            print("    状态码: {}".format(response.status_code))

            if response.status_code == 200:
                test_response = requests.get('https://jable.tv',
                                            proxies=proxies, timeout=10)
                if 'Just a moment' in test_response.text or 'Verify you are human' in test_response.text:
                    print("    结果: Cloudflare 验证页面")
                else:
                    print("    结果: 正常访问")
    except Exception as e:
        if proxies:
            print("    访问失败: {}".format(str(e)[:50]))
    print()

    # 5. 建议
    print("=" * 60)
    print("建议")
    print("=" * 60)
    print()

    # 检查是否需要代理
    need_proxy = False
    try:
        response = requests.get('https://jable.tv', timeout=10)
        if 'Just a moment' in response.text or 'Verify you are human' in response.text:
            need_proxy = True
    except:
        pass

    if need_proxy:
        print("⚠ 当前网络访问 jable.tv 会触发 Cloudflare 验证")
        print()
        print("建议:")
        print("1. 配置代理 (住宅 IP 代理)")
        print("   编辑 config.json:")
        print('   {')
        print('       "proxies": {')
        print('           "http": "http://proxy-server:port",')
        print('           "https": "http://proxy-server:port"')
        print('       }')
        print('   }')
        print()
        print("2. 使用 ScrapingAnt 服务")
        print("   编辑 config.json:")
        print('   {')
        print('       "sa_token": "your_token_here"')
        print('   }')
        print()
        print("3. 在本地运行（如果本地可以正常访问）")
    else:
        print("✓ 当前网络可以正常访问 jable.tv")
        print()
        print("但 Playwright 仍可能触发验证，因为:")
        print("- Cloudflare 检测自动化工具")
        print("- 需要更高级的反检测技术")

if __name__ == '__main__':
    check_proxy()

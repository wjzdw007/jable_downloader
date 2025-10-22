#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示系统信息和自动适配的浏览器配置
"""

import platform
import json

def show_system_info():
    """显示系统信息"""

    print("="*70)
    print("🖥️  系统信息和浏览器配置自动适配")
    print("="*70)
    print()

    # 检测操作系统
    system = platform.system()
    system_release = platform.release()
    system_version = platform.version()
    machine = platform.machine()

    print("📊 操作系统信息：")
    print(f"  • 系统类型: {system}")
    print(f"  • 系统版本: {system_release}")
    print(f"  • 架构: {machine}")
    print(f"  • 详细版本: {system_version[:50]}...")
    print()

    # 确定浏览器配置
    if system == 'Linux':
        platform_name = 'Linux'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        nav_platform = 'Linux x86_64'
    elif system == 'Darwin':
        platform_name = 'macOS'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        nav_platform = 'MacIntel'
    elif system == 'Windows':
        platform_name = 'Windows'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        nav_platform = 'Win32'
    else:
        platform_name = 'Linux'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        nav_platform = 'Linux x86_64'

    print("-"*70)
    print("🌐 自动适配的浏览器配置：")
    print("-"*70)
    print()

    print("HTTP 头部：")
    print(f"  • User-Agent:")
    print(f"    {user_agent}")
    print(f"  • sec-ch-ua-platform: \"{platform_name}\"")
    print()

    print("JavaScript 特征：")
    print(f"  • navigator.platform: {nav_platform}")
    print(f"  • navigator.userAgent: {user_agent}")
    print()

    # 读取 config.json 配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        print("-"*70)
        print("⚙️  当前配置（config.json）：")
        print("-"*70)
        print()

        # 显示关键配置
        headless = config.get('playwright_headless', True)
        headless_text = "无头模式（后台运行）" if headless else "有头模式（显示窗口）"
        print(f"  • playwright_headless: {headless}")
        print(f"    → {headless_text}")
        print()

        # 代理配置
        proxies = config.get('proxies', {})
        if proxies:
            print(f"  • 代理配置:")
            for key, value in proxies.items():
                print(f"    - {key}: {value}")
        else:
            print(f"  • 代理配置: 未配置")
        print()

        # User-Agent 覆盖
        headers = config.get('headers', {})
        config_ua = headers.get('User-Agent', None)
        if config_ua:
            print(f"  • config.json 中的 User-Agent:")
            print(f"    {config_ua}")
            print()
            print(f"  ⚠️  注意: config.json 中定义的 User-Agent 会覆盖自动检测的")
            print(f"    建议删除 config.json 中的 User-Agent，让程序自动适配")
        else:
            print(f"  • User-Agent: 自动适配 ✅")

    except FileNotFoundError:
        print("-"*70)
        print("⚠️  未找到 config.json 文件")
        print("-"*70)
    except Exception as e:
        print(f"⚠️  读取 config.json 失败: {str(e)}")

    print()
    print("="*70)
    print("✅ 系统信息显示完成")
    print("="*70)
    print()

    # 显示建议
    print("💡 建议：")
    print()

    if system == 'Linux':
        print("  检测到 Linux 系统（Ubuntu/Debian 等）")
        print()
        print("  1. 使用有头模式（更难被检测）：")
        print("     • 编辑 config.json，设置 \"playwright_headless\": false")
        print("     • 安装 Xvfb: sudo apt-get install -y xvfb")
        print("     • 运行: xvfb-run -a python3 main.py subscription --sync-videos")
        print()
        print("  2. 使用无头模式（更简单）：")
        print("     • 编辑 config.json，设置 \"playwright_headless\": true")
        print("     • 直接运行: python3 main.py subscription --sync-videos")
    elif system == 'Darwin':
        print("  检测到 macOS 系统")
        print()
        print("  1. 推荐使用有头模式（可以看到浏览器操作）：")
        print("     • 编辑 config.json，设置 \"playwright_headless\": false")
        print("     • 直接运行: python3 main.py subscription --sync-videos")
        print()
        print("  2. 或使用无头模式（后台运行）：")
        print("     • 编辑 config.json，设置 \"playwright_headless\": true")
    elif system == 'Windows':
        print("  检测到 Windows 系统")
        print()
        print("  1. 推荐使用有头模式：")
        print("     • 编辑 config.json，设置 \"playwright_headless\": false")
        print("     • 直接运行: python main.py subscription --sync-videos")

    print()
    print("  3. 删除 config.json 中的 User-Agent 配置（推荐）：")
    print("     让程序自动根据操作系统适配正确的 User-Agent")
    print()


if __name__ == '__main__':
    show_system_info()

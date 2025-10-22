#!/usr/bin/env python3
# coding: utf-8

"""
完整功能测试脚本
测试项目的主要功能是否正常工作
"""

import sys
import os
import json
import traceback

def test_imports():
    """测试 1: 检查所有必要的模块是否可以导入"""
    print("=" * 60)
    print("测试 1: 模块导入测试")
    print("=" * 60)

    modules = [
        ('config', '配置模块'),
        ('utils', '工具模块'),
        ('video_crawler', '视频爬取模块'),
        ('model_crawler', '模型爬取模块'),
        ('executor', '执行器模块'),
        ('main', '主程序'),
    ]

    failed = []
    for module_name, desc in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {desc} ({module_name})")
        except Exception as e:
            print(f"  ✗ {desc} ({module_name}): {e}")
            failed.append(module_name)

    print()
    if failed:
        print(f"✗ 导入测试失败，{len(failed)} 个模块无法导入")
        return False
    else:
        print("✓ 所有模块导入成功")
        return True


def test_playwright_integration():
    """测试 2: Playwright 集成测试"""
    print("\n" + "=" * 60)
    print("测试 2: Playwright 集成测试")
    print("=" * 60)

    try:
        from utils import get_response_from_playwright

        # 使用一个简单的测试 URL
        test_url = "https://example.com"
        print(f"  - 测试 URL: {test_url}")

        html = get_response_from_playwright(test_url)

        if html and len(html) > 0:
            print(f"  ✓ 成功获取页面内容 ({len(html)} 字符)")

            # 检查是否包含预期内容
            if "Example Domain" in html:
                print(f"  ✓ 页面内容验证成功")
                return True
            else:
                print(f"  ✗ 页面内容验证失败")
                return False
        else:
            print(f"  ✗ 未获取到页面内容")
            return False

    except Exception as e:
        print(f"  ✗ Playwright 测试失败: {e}")
        traceback.print_exc()
        return False


def test_config():
    """测试 3: 配置文件测试"""
    print("\n" + "=" * 60)
    print("测试 3: 配置管理测试")
    print("=" * 60)

    try:
        import config

        # 检查配置项
        required_keys = [
            'downloadVideoCover',
            'downloadInterval',
            'outputDir',
            'headers',
        ]

        missing = []
        for key in required_keys:
            if key in config.CONF:
                print(f"  ✓ 配置项 '{key}' 存在")
            else:
                print(f"  ✗ 配置项 '{key}' 缺失")
                missing.append(key)

        if missing:
            print(f"\n✗ 配置测试失败，{len(missing)} 个必需项缺失")
            return False
        else:
            print(f"\n✓ 配置测试通过")
            return True

    except Exception as e:
        print(f"  ✗ 配置测试失败: {e}")
        traceback.print_exc()
        return False


def test_utils():
    """测试 4: 工具函数测试"""
    print("\n" + "=" * 60)
    print("测试 4: 工具函数测试")
    print("=" * 60)

    try:
        from utils import (
            get_video_ids_map_from_cache,
            get_local_video_list,
        )

        # 测试缓存读取
        print("  - 测试缓存读取...")
        cache = get_video_ids_map_from_cache()
        print(f"  ✓ 缓存读取成功 (包含 {len(cache)} 个条目)")

        # 测试本地视频列表
        print("  - 测试本地视频列表...")
        output_dir = os.getcwd()
        videos = get_local_video_list(output_dir)
        print(f"  ✓ 本地视频列表获取成功 (找到 {len(videos)} 个视频)")

        print(f"\n✓ 工具函数测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 工具函数测试失败: {e}")
        traceback.print_exc()
        return False


def test_video_crawler_functions():
    """测试 5: 视频爬取模块函数测试"""
    print("\n" + "=" * 60)
    print("测试 5: 视频爬取模块测试")
    print("=" * 60)

    try:
        from video_crawler import (
            get_video_full_name,
            prepare_output_dir,
        )

        # 测试输出目录准备
        print("  - 测试输出目录准备...")
        output_dir = prepare_output_dir()
        if os.path.exists(output_dir):
            print(f"  ✓ 输出目录准备成功: {output_dir}")
        else:
            print(f"  ✗ 输出目录不存在: {output_dir}")
            return False

        # 测试视频名称提取
        print("  - 测试视频名称提取...")
        test_html = '''
        <html>
            <meta content="ABC-123 Test Video Title">
        </html>
        '''
        video_name = get_video_full_name("abc-123", test_html)
        if video_name:
            print(f"  ✓ 视频名称提取成功: {video_name}")
        else:
            print(f"  ✗ 视频名称提取失败")
            return False

        print(f"\n✓ 视频爬取模块测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 视频爬取模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_model_crawler_functions():
    """测试 6: 模型爬取模块函数测试"""
    print("\n" + "=" * 60)
    print("测试 6: 模型爬取模块测试")
    print("=" * 60)

    try:
        from model_crawler import (
            input_url_validator,
            get_page_url,
        )

        # 测试 URL 验证
        print("  - 测试 URL 验证...")
        try:
            input_url_validator("https://jable.tv/models/test/")
            print(f"  ✓ 有效 URL 验证通过")
        except:
            print(f"  ✗ 有效 URL 验证失败")
            return False

        try:
            input_url_validator("https://jable.tv/models/test/?from=2")
            print(f"  ✗ 无效 URL 应该被拒绝")
            return False
        except:
            print(f"  ✓ 无效 URL 正确拒绝")

        # 测试分页 URL 生成
        print("  - 测试分页 URL 生成...")
        page_url = get_page_url("https://jable.tv/models/test/", 2)
        if "from=2" in page_url:
            print(f"  ✓ 分页 URL 生成成功: {page_url}")
        else:
            print(f"  ✗ 分页 URL 生成失败: {page_url}")
            return False

        print(f"\n✓ 模型爬取模块测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 模型爬取模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_main_program():
    """测试 7: 主程序测试"""
    print("\n" + "=" * 60)
    print("测试 7: 主程序测试")
    print("=" * 60)

    try:
        # 测试主程序是否可以正常导入
        import main
        print(f"  ✓ 主程序导入成功")

        # 测试 argparse 配置
        if hasattr(main, 'parser'):
            print(f"  ✓ 命令行解析器配置正确")
        else:
            print(f"  ✗ 命令行解析器未找到")
            return False

        print(f"\n✓ 主程序测试通过")
        return True

    except Exception as e:
        print(f"  ✗ 主程序测试失败: {e}")
        traceback.print_exc()
        return False


def test_dependencies():
    """测试 8: 依赖检查"""
    print("\n" + "=" * 60)
    print("测试 8: 依赖库检查")
    print("=" * 60)

    dependencies = [
        ('requests', 'HTTP 请求库'),
        ('bs4', 'BeautifulSoup HTML 解析'),
        ('m3u8', 'M3U8 解析'),
        ('Crypto', 'AES 加密解密'),
        ('playwright.sync_api', 'Playwright 浏览器自动化'),
    ]

    failed = []
    for module_name, desc in dependencies:
        try:
            __import__(module_name)
            print(f"  ✓ {desc} ({module_name})")
        except Exception as e:
            print(f"  ✗ {desc} ({module_name}): {e}")
            failed.append(module_name)

    print()
    if failed:
        print(f"✗ 依赖检查失败，{len(failed)} 个库缺失")
        return False
    else:
        print("✓ 所有依赖库已安装")
        return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  Jable Downloader 功能测试套件")
    print("=" * 60)
    print()

    tests = [
        ("依赖库检查", test_dependencies),
        ("模块导入", test_imports),
        ("配置管理", test_config),
        ("工具函数", test_utils),
        ("视频爬取模块", test_video_crawler_functions),
        ("模型爬取模块", test_model_crawler_functions),
        ("Playwright 集成", test_playwright_integration),
        ("主程序", test_main_program),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 执行失败: {e}")
            traceback.print_exc()
            results.append((test_name, False))

    # 打印测试总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {test_name}")

    print()
    print("=" * 60)
    if passed == total:
        print(f"  ✓ 所有测试通过！({passed}/{total})")
        print("=" * 60)
        return True
    else:
        print(f"  ✗ 部分测试失败 ({passed}/{total} 通过)")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# coding: utf-8

"""
订阅管理功能测试
"""

import sys
import os
import json
import tempfile
import shutil

def test_subscription_management():
    """测试订阅管理功能"""
    print("=" * 60)
    print("订阅管理功能测试")
    print("=" * 60)
    print()

    # 创建临时配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    test_config = {
        "downloadVideoCover": False,
        "downloadInterval": 0,
        "outputDir": "./test_output",
        "subscriptions": [],
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://jable.tv"
        },
        "sa_token": ""
    }

    json.dump(test_config, temp_config)
    temp_config.close()

    print(f"创建临时配置文件: {temp_config.name}")
    print()

    try:
        # 测试配置读取
        print("[测试 1] 配置文件读取")
        import config
        print(f"  ✓ 当前订阅数: {len(config.CONF.get('subscriptions', []))}")
        print()

        # 测试订阅验证
        print("[测试 2] URL 验证")
        from model_crawler import input_url_validator

        test_cases = [
            ("https://jable.tv/models/test/", True, "有效的模型URL"),
            ("https://jable.tv/tags/test/", True, "有效的标签URL"),
            ("https://jable.tv/categories/test/", True, "有效的类别URL"),
            ("https://jable.tv/search/test/", True, "有效的搜索URL"),
            ("https://jable.tv/models/test/?from=2", False, "包含分页的无效URL"),
            ("https://jable.tv/videos/abc-123/", False, "视频URL（应该拒绝）"),
        ]

        for url, should_pass, desc in test_cases:
            try:
                input_url_validator(url)
                if should_pass:
                    print(f"  ✓ {desc}: 验证通过")
                else:
                    print(f"  ✗ {desc}: 应该被拒绝但通过了")
            except Exception as e:
                if not should_pass:
                    print(f"  ✓ {desc}: 正确拒绝")
                else:
                    print(f"  ✗ {desc}: 不应该被拒绝 ({e})")

        print()

        # 测试分页URL生成
        print("[测试 3] 分页URL生成")
        from model_crawler import get_page_url

        test_urls = [
            ("https://jable.tv/models/test/", 1, "https://jable.tv/models/test/?from=1"),
            ("https://jable.tv/models/test/", 5, "https://jable.tv/models/test/?from=5"),
            ("https://jable.tv/search/keyword/", 2, "https://jable.tv/search/keyword/?from_videos=2"),
        ]

        for base_url, page_num, expected in test_urls:
            result = get_page_url(base_url, page_num)
            if result == expected:
                print(f"  ✓ 第{page_num}页: {result}")
            else:
                print(f"  ✗ 第{page_num}页: 期望 {expected}, 得到 {result}")

        print()

        # 测试执行器函数
        print("[测试 4] 执行器函数")
        from executor import print_all_subs

        test_subs = [
            [{"url": "https://jable.tv/models/test1/", "name": "测试1"}],
            [
                {"url": "https://jable.tv/models/test2/", "name": "测试2"},
                {"url": "https://jable.tv/categories/chinese/", "name": "中文字幕"}
            ]
        ]

        print("  - 打印订阅列表:")
        print_all_subs(test_subs, print_url=False)
        print()

        print("✓ 订阅管理功能测试完成")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理临时文件
        if os.path.exists(temp_config.name):
            os.unlink(temp_config.name)
            print(f"\n清理临时文件: {temp_config.name}")


if __name__ == '__main__':
    success = test_subscription_management()
    sys.exit(0 if success else 1)

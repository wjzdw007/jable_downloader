#!/usr/bin/env python3
# coding: utf-8

"""
调试演员页面解析 - 检查为什么找不到演员名称
"""

from __future__ import print_function
import sys
from bs4 import BeautifulSoup
import utils

def debug_model_page(url):
    """调试演员页面"""
    print("=" * 60)
    print("演员页面调试工具")
    print("=" * 60)
    print()

    print("目标URL: {}".format(url))
    print()

    print("正在获取页面内容...")
    try:
        content = utils.scrapingant_requests_get(url)
        print("✓ 页面获取成功，长度: {} 字符".format(len(content)))
        print()
    except Exception as e:
        print("✗ 页面获取失败: {}".format(e))
        return

    # 保存HTML到文件
    with open("debug_model_page.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ 完整HTML已保存到: debug_model_page.html")
    print()

    # 解析HTML
    soup = BeautifulSoup(content, 'html.parser')

    # 尝试多种方式查找演员名称
    print("=== 尝试查找演员名称 ===")
    print()

    # 方法1: 原代码的方式
    print("方法1: 查找 <h2 class='h3-md mb-1'>")
    model_name_item = soup.find('h2', class_='h3-md mb-1')
    if model_name_item:
        print("  ✓ 找到: {}".format(model_name_item.get_text().strip()))
    else:
        print("  ✗ 未找到")
    print()

    # 方法2: 查找所有 h2 标签
    print("方法2: 查找所有 <h2> 标签")
    h2_tags = soup.find_all('h2')
    if h2_tags:
        print("  找到 {} 个 <h2> 标签:".format(len(h2_tags)))
        for i, tag in enumerate(h2_tags[:5], 1):
            classes = tag.get('class', [])
            text = tag.get_text().strip()[:50]
            print("    [{}] class={} text='{}'".format(i, classes, text))
    else:
        print("  ✗ 未找到任何 <h2> 标签")
    print()

    # 方法3: 查找包含特定文本的标签
    print("方法3: 查找包含 'レモン' 或 '田中' 的标签")
    for tag_name in ['h1', 'h2', 'h3', 'h4', 'div', 'span']:
        tags = soup.find_all(tag_name)
        for tag in tags:
            text = tag.get_text().strip()
            if 'レモン' in text or '田中' in text:
                classes = tag.get('class', [])
                print("  ✓ 找到 <{}> class={} text='{}'".format(
                    tag_name, classes, text[:50]))
                break
    print()

    # 方法4: 查找 title 标签
    print("方法4: 查找 <title> 标签")
    title_tag = soup.find('title')
    if title_tag:
        print("  ✓ 标题: {}".format(title_tag.get_text().strip()))
    else:
        print("  ✗ 未找到")
    print()

    # 方法5: 查找 meta 标签
    print("方法5: 查找相关 <meta> 标签")
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = meta.get('name', '')
        property_val = meta.get('property', '')
        content = meta.get('content', '')

        if any(keyword in str(content).lower() for keyword in ['レモン', '田中', 'lemon', 'tanaka']):
            print("  ✓ name='{}' property='{}' content='{}'".format(
                name, property_val, content[:50]))
    print()

    # 方法6: 查找分页信息
    print("方法6: 查找分页信息")
    page_items = soup.select('.pagination>.page-item>.page-link')
    if page_items:
        print("  ✓ 找到 {} 个分页链接".format(len(page_items)))
        if page_items:
            last_item = page_items[-1].get('data-parameters')
            print("  最后一页参数: {}".format(last_item))
    else:
        print("  ✗ 未找到分页")
    print()

    # 方法7: 查找视频数量
    print("方法7: 查找视频数量")
    span_tags = soup.select('span.inactive-color')
    if span_tags:
        for span in span_tags:
            text = span.get_text().strip()
            print("  找到: '{}'".format(text))
    else:
        print("  ✗ 未找到")
    print()

    # 输出建议
    print("=" * 60)
    print("建议")
    print("=" * 60)
    print()
    print("1. 查看保存的 HTML 文件:")
    print("   cat debug_model_page.html | grep -i '田中\\|レモン'")
    print()
    print("2. 如果页面结构变化，需要更新 model_crawler.py 中的选择器")
    print()
    print("3. 可能需要等待页面动态加载完成")
    print()

if __name__ == '__main__':
    # 测试URL
    test_url = "https://jable.tv/models/851cf1602f37c2611917b675f2d432c7/"

    if len(sys.argv) > 1:
        test_url = sys.argv[1]

    debug_model_page(test_url)

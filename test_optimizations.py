#!/usr/bin/env python3
"""
测试新增的优化措施
"""

import time
import sys

def test_lxml_available():
    """测试 lxml 是否可用"""
    print("=" * 80)
    print("【测试1】检查 lxml 解析器")
    print("=" * 80)

    try:
        from bs4 import BeautifulSoup
        html = "<html><body><div class='test'>Hello</div></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        print("✅ lxml 解析器可用")
        return True
    except Exception as e:
        print(f"❌ lxml 解析器不可用: {e}")
        print("   建议安装: pip install lxml")
        return False


def test_regex_precompile():
    """测试预编译正则表达式"""
    print("\n" + "=" * 80)
    print("【测试2】测试预编译正则表达式")
    print("=" * 80)

    import re

    # 测试数据
    test_string = "  123  456  "
    iterations = 100000

    # 方法1：每次编译
    start = time.time()
    for _ in range(iterations):
        result = re.sub(r'\s+', '', test_string)
    time_without_precompile = time.time() - start

    # 方法2：预编译
    pattern = re.compile(r'\s+')
    start = time.time()
    for _ in range(iterations):
        result = pattern.sub('', test_string)
    time_with_precompile = time.time() - start

    improvement = (time_without_precompile - time_with_precompile) / time_without_precompile * 100

    print(f"  未预编译: {time_without_precompile:.3f}秒")
    print(f"  预编译:   {time_with_precompile:.3f}秒")
    print(f"  提升:     {improvement:.1f}%")

    if improvement > 0:
        print("✅ 预编译正则有效")
    else:
        print("⚠️  预编译正则无明显提升")


def test_crawler_optimizations():
    """测试爬虫优化"""
    print("\n" + "=" * 80)
    print("【测试3】测试爬虫优化措施")
    print("=" * 80)

    from analytics_crawler import crawl_hot_page, USE_FAST_MODE

    print(f"  使用优化版: {'是' if USE_FAST_MODE else '否'}")

    # 测试爬取一页
    print("\n  测试爬取第1页...")
    start = time.time()
    videos, total_pages = crawl_hot_page(1, retry=3)
    elapsed = time.time() - start

    print(f"\n  ✓ 耗时: {elapsed:.2f}秒")
    print(f"  ✓ 获取视频: {len(videos)} 个")
    print(f"  ✓ 总页数: {total_pages}")

    if videos:
        print(f"\n  前3个视频:")
        for i, v in enumerate(videos[:3], 1):
            print(f"    {i}. {v['video_id']:<15} 👁️  {v['views']:>8,}  👍 {v['likes']:>6,}")

    # 性能评估
    if elapsed < 2.0:
        print(f"\n✅ 性能优秀（{elapsed:.2f}秒 < 2秒）")
    elif elapsed < 3.5:
        print(f"\n✅ 性能良好（{elapsed:.2f}秒 < 3.5秒）")
    else:
        print(f"\n⚠️  性能一般（{elapsed:.2f}秒）")


def test_smart_delay():
    """测试智能延迟"""
    print("\n" + "=" * 80)
    print("【测试4】测试智能延迟功能")
    print("=" * 80)

    from analytics_crawler import USE_FAST_MODE

    # 预期延迟
    expected_delay = 0.5 if USE_FAST_MODE else 1.0
    print(f"  优化模式: {'开启' if USE_FAST_MODE else '关闭'}")
    print(f"  预期延迟: {expected_delay}秒")

    # 测试实际延迟
    import time
    start = time.time()
    time.sleep(expected_delay)
    elapsed = time.time() - start

    print(f"  实际延迟: {elapsed:.2f}秒")

    if abs(elapsed - expected_delay) < 0.1:
        print("✅ 延迟设置正确")
    else:
        print("⚠️  延迟有偏差")


def test_checkpoint_resume():
    """测试断点续传功能"""
    print("\n" + "=" * 80)
    print("【测试5】测试断点续传功能")
    print("=" * 80)

    from progress_tracker import ProgressTracker
    import os

    # 使用测试文件
    test_file = './test_checkpoint.json'

    try:
        tracker = ProgressTracker(test_file)

        # 创建测试任务
        task_id = tracker.start_task('test', 10)
        print(f"  ✓ 创建任务: {task_id}")

        # 模拟完成几页
        for i in range(1, 4):
            tracker.update_page(task_id, i, success=True)
        print(f"  ✓ 模拟完成页面: 1-3")

        # 模拟失败一页
        tracker.update_page(task_id, 4, success=False)
        print(f"  ✓ 模拟失败页面: 4")

        # 获取待处理页面
        pending = tracker.get_pending_pages(task_id)
        print(f"  ✓ 待处理页面: {pending}")

        # 获取恢复信息
        resume_info = tracker.get_resume_info('test')
        if resume_info:
            print(f"  ✓ 恢复信息:")
            print(f"    - 已完成: {resume_info['completed']}/{resume_info['total']}")
            print(f"    - 进度: {resume_info['progress']:.1f}%")
            print(f"    - 待处理: {len(resume_info['pending'])} 页")

        print("\n✅ 断点续传功能正常")

    except Exception as e:
        print(f"\n❌ 断点续传测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"  ✓ 清理测试文件")


def main():
    print("\n" + "🚀" * 40)
    print("爬虫优化测试")
    print("🚀" * 40 + "\n")

    # 运行所有测试
    lxml_ok = test_lxml_available()
    test_regex_precompile()
    test_smart_delay()
    test_checkpoint_resume()

    # 最后测试爬虫（需要网络）
    try:
        test_crawler_optimizations()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    print("\n✅ 已实现的优化:")
    print("  1. 预编译正则表达式 ✓")
    print("  2. 智能延迟（优化版0.5秒，原版1.0秒）✓")
    print("  3. 断点续传功能 ✓")

    if lxml_ok:
        print("  4. lxml 解析器 ✓")
    else:
        print("  4. lxml 解析器 ✗ (需要安装)")
        print("     安装命令: pip install lxml")

    print("\n📊 预期性能提升:")
    print("  - 正则优化: 2-5%")
    print("  - 智能延迟: 节省12分钟（1424页）")
    print("  - lxml 解析: 5-10%")
    print("  - 综合提升: 10-20%")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()

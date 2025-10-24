#!/usr/bin/env python3
"""
进度跟踪模块
支持断点续传，记录爬取进度
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List


class ProgressTracker:
    """
    进度跟踪器

    记录格式：
    {
        "task_id": "analyze_init_2025-10-25",
        "task_type": "init",  # init 或 update
        "start_time": "2025-10-25 10:00:00",
        "last_update": "2025-10-25 10:30:00",
        "total_pages": 1424,
        "completed_pages": [1, 2, 3, ...],
        "failed_pages": [10, 20],
        "current_page": 100,
        "status": "in_progress",  # in_progress, completed, failed
        "stats": {
            "videos_count": 2400,
            "actors_count": 50
        }
    }
    """

    def __init__(self, progress_file: str = './progress.json'):
        """
        初始化进度跟踪器

        Args:
            progress_file: 进度文件路径
        """
        self.progress_file = progress_file
        self.progress = self._load_progress()

    def _load_progress(self) -> Dict:
        """加载进度文件"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_progress(self):
        """保存进度文件"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def start_task(self, task_type: str, total_pages: int) -> str:
        """
        开始新任务

        Args:
            task_type: 任务类型（init 或 update）
            total_pages: 总页数

        Returns:
            task_id
        """
        today = datetime.now().strftime('%Y-%m-%d')
        task_id = f"analyze_{task_type}_{today}"

        self.progress[task_id] = {
            'task_id': task_id,
            'task_type': task_type,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': total_pages,
            'completed_pages': [],
            'failed_pages': [],
            'current_page': 0,
            'status': 'in_progress',
            'stats': {
                'videos_count': 0,
                'actors_count': 0
            }
        }

        self._save_progress()
        print(f"✓ 任务已启动: {task_id}")
        return task_id

    def get_task(self, task_type: str) -> Optional[Dict]:
        """
        获取今天的任务进度

        Args:
            task_type: 任务类型

        Returns:
            任务进度字典，如果不存在返回 None
        """
        today = datetime.now().strftime('%Y-%m-%d')
        task_id = f"analyze_{task_type}_{today}"
        return self.progress.get(task_id)

    def update_page(self, task_id: str, page_num: int, success: bool = True):
        """
        更新页面完成状态

        Args:
            task_id: 任务ID
            page_num: 页码
            success: 是否成功
        """
        if task_id not in self.progress:
            return

        task = self.progress[task_id]

        if success:
            if page_num not in task['completed_pages']:
                task['completed_pages'].append(page_num)
            # 从失败列表中移除（如果之前失败过）
            if page_num in task['failed_pages']:
                task['failed_pages'].remove(page_num)
        else:
            if page_num not in task['failed_pages']:
                task['failed_pages'].append(page_num)

        task['current_page'] = page_num
        task['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self._save_progress()

    def update_stats(self, task_id: str, videos_count: int, actors_count: int):
        """
        更新统计信息

        Args:
            task_id: 任务ID
            videos_count: 视频数量
            actors_count: 演员数量
        """
        if task_id not in self.progress:
            return

        self.progress[task_id]['stats'] = {
            'videos_count': videos_count,
            'actors_count': actors_count
        }
        self._save_progress()

    def complete_task(self, task_id: str):
        """
        标记任务完成

        Args:
            task_id: 任务ID
        """
        if task_id not in self.progress:
            return

        self.progress[task_id]['status'] = 'completed'
        self.progress[task_id]['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_progress()

        print(f"✓ 任务已完成: {task_id}")

    def fail_task(self, task_id: str, error: str):
        """
        标记任务失败

        Args:
            task_id: 任务ID
            error: 错误信息
        """
        if task_id not in self.progress:
            return

        self.progress[task_id]['status'] = 'failed'
        self.progress[task_id]['error'] = error
        self.progress[task_id]['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_progress()

    def get_pending_pages(self, task_id: str) -> List[int]:
        """
        获取待处理的页码列表

        Args:
            task_id: 任务ID

        Returns:
            待处理页码列表
        """
        if task_id not in self.progress:
            return []

        task = self.progress[task_id]
        total_pages = task['total_pages']
        completed = set(task['completed_pages'])

        # 返回未完成的页码
        return [i for i in range(1, total_pages + 1) if i not in completed]

    def get_resume_info(self, task_type: str) -> Optional[Dict]:
        """
        获取可恢复的任务信息

        Args:
            task_type: 任务类型

        Returns:
            {
                'task_id': 'xxx',
                'completed': 100,
                'total': 1424,
                'pending': [101, 102, ...],
                'failed': [10, 20],
                'progress': 7.0  # 百分比
            }
        """
        task = self.get_task(task_type)
        if not task or task['status'] == 'completed':
            return None

        completed = len(task['completed_pages'])
        total = task['total_pages']
        pending = self.get_pending_pages(task['task_id'])

        return {
            'task_id': task['task_id'],
            'completed': completed,
            'total': total,
            'pending': pending,
            'failed': task['failed_pages'],
            'progress': (completed / total * 100) if total > 0 else 0,
            'last_update': task['last_update']
        }

    def print_status(self, task_id: str):
        """
        打印任务状态

        Args:
            task_id: 任务ID
        """
        if task_id not in self.progress:
            print(f"⚠️  任务不存在: {task_id}")
            return

        task = self.progress[task_id]

        print("\n" + "="*80)
        print("任务进度")
        print("="*80)
        print(f"  任务ID: {task['task_id']}")
        print(f"  类型: {task['task_type']}")
        print(f"  状态: {task['status']}")
        print(f"  开始时间: {task['start_time']}")
        print(f"  最后更新: {task['last_update']}")
        print(f"  总页数: {task['total_pages']:,}")
        print(f"  已完成: {len(task['completed_pages']):,} 页")
        print(f"  失败: {len(task['failed_pages'])} 页")
        print(f"  当前页: {task['current_page']}")

        if task['total_pages'] > 0:
            progress = len(task['completed_pages']) / task['total_pages'] * 100
            print(f"  进度: {progress:.1f}%")

        if task.get('stats'):
            print(f"\n  统计:")
            print(f"    视频数: {task['stats'].get('videos_count', 0):,}")
            print(f"    演员数: {task['stats'].get('actors_count', 0):,}")

        if task['failed_pages']:
            print(f"\n  失败页码: {task['failed_pages'][:10]}{'...' if len(task['failed_pages']) > 10 else ''}")

        print("="*80)


if __name__ == '__main__':
    # 测试
    tracker = ProgressTracker('./test_progress.json')

    # 模拟任务
    task_id = tracker.start_task('init', 10)

    # 模拟完成几页
    for i in range(1, 6):
        tracker.update_page(task_id, i, success=True)
        tracker.print_status(task_id)

    # 模拟失败一页
    tracker.update_page(task_id, 6, success=False)

    # 查看恢复信息
    resume_info = tracker.get_resume_info('init')
    print(f"\n恢复信息: {resume_info}")

    # 清理测试文件
    import os
    if os.path.exists('./test_progress.json'):
        os.remove('./test_progress.json')

    print("\n✓ 进度跟踪模块测试完成")

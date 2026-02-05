"""
异步任务系统
提供后台任务处理、进度跟踪和失败重试
"""

import threading
import time
import uuid
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue, PriorityQueue
import json


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass
class Task:
    """异步任务"""
    task_id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    progress: float = 0.0
    message: str = ""

    @property
    def duration(self) -> Optional[float]:
        """获取任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "result": str(self.result)[:100] if self.result else None,
            "error": self.error,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "started_at": datetime.fromtimestamp(self.started_at).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at).isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "progress": round(self.progress, 2),
            "duration": round(self.duration, 2) if self.duration else None
        }


class TaskQueue:
    """任务队列"""

    def __init__(self, max_size: int = 1000):
        self.queue: PriorityQueue = PriorityQueue(maxsize=max_size)
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()

    def put(self, task: Task):
        """添加任务"""
        with self.lock:
            self.queue.put((task.priority.value, task.created_at, task))
            self.tasks[task.task_id] = task

    def get(self, timeout: Optional[float] = None) -> Optional[Task]:
        """获取任务"""
        try:
            priority, created_at, task = self.queue.get(timeout=timeout)
            return task
        except:
            return None

    def get_task(self, task_id: str) -> Optional[Task]:
        """根据 ID 获取任务"""
        with self.lock:
            return self.tasks.get(task_id)

    def update_task(self, task: Task):
        """更新任务"""
        with self.lock:
            if task.task_id in self.tasks:
                self.tasks[task.task_id] = task

    def remove(self, task_id: str):
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        with self.lock:
            return list(self.tasks.values())

    def size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()


class TaskWorker(threading.Thread):
    """任务工作线程"""

    def __init__(
        self,
        worker_id: int,
        task_queue: TaskQueue,
        progress_callback: Optional[Callable[[str, float, str], None]] = None
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.progress_callback = progress_callback
        self.running = True
        self.current_task: Optional[Task] = None

    def run(self):
        """运行工作线程"""
        while self.running:
            task = self.task_queue.get(timeout=1.0)

            if task is None:
                continue

            self.current_task = task
            self._execute_task(task)

    def _execute_task(self, task: Task):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        self.task_queue.update_task(task)

        try:
            # 执行任务函数
            result = task.func(*task.args, **task.kwargs)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 100.0
            task.message = "Completed"

        except Exception as e:
            error_msg = str(e)

            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.error = None

                # 重新加入队列
                self.task_queue.put(task)

                # 指数退避
                time.sleep(2 ** task.retry_count)
                return

            task.status = TaskStatus.FAILED
            task.error = error_msg
            task.message = f"Failed: {error_msg}"

        finally:
            task.completed_at = time.time()
            self.task_queue.update_task(task)
            self.current_task = None

    def stop(self):
        """停止工作线程"""
        self.running = False

        # 如果有正在执行的任务，标记为取消
        if self.current_task:
            self.current_task.status = TaskStatus.CANCELLED
            self.task_queue.update_task(self.current_task)


class AsyncTaskManager:
    """异步任务管理器"""

    def __init__(self, num_workers: int = 4):
        self.task_queue = TaskQueue()
        self.workers: List[TaskWorker] = []
        self.num_workers = num_workers
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        self._initialize_workers()

    def _initialize_workers(self):
        """初始化工作线程"""
        for i in range(self.num_workers):
            worker = TaskWorker(
                worker_id=i,
                task_queue=self.task_queue,
                progress_callback=self._on_progress
            )
            worker.start()
            self.workers.append(worker)

    def submit_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())[:8]

        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries
        )

        self.task_queue.put(task)

        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.task_queue.get_task(task_id)
        if task:
            return task.to_dict()
        return None

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.task_queue.get_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self.task_queue.update_task(task)
            return True
        return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务"""
        tasks = self.task_queue.get_all_tasks()
        return [task.to_dict() for task in tasks]

    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """获取正在运行的任务"""
        tasks = self.task_queue.get_all_tasks()
        return [
            task.to_dict()
            for task in tasks
            if task.status == TaskStatus.RUNNING
        ]

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """获取待处理任务"""
        tasks = self.task_queue.get_all_tasks()
        return [
            task.to_dict()
            for task in tasks
            if task.status == TaskStatus.PENDING
        ]

    def _on_progress(self, task_id: str, progress: float, message: str):
        """进度回调"""
        if task_id in self.progress_callbacks:
            for callback in self.progress_callbacks[task_id]:
                try:
                    callback(progress, message)
                except:
                    pass

    def add_progress_callback(self, task_id: str, callback: Callable[[float, str], None]):
        """添加进度回调"""
        if task_id not in self.progress_callbacks:
            self.progress_callbacks[task_id] = []
        self.progress_callbacks[task_id].append(callback)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        tasks = self.task_queue.get_all_tasks()

        stats = {
            "total_tasks": len(tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "queue_size": self.task_queue.size(),
            "workers": self.num_workers
        }

        for task in tasks:
            stats[task.status.value] += 1

        return stats

    def cleanup_old_tasks(self, max_age: float = 3600):
        """清理旧任务"""
        tasks = self.task_queue.get_all_tasks()
        current_time = time.time()

        for task in tasks:
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at and (current_time - task.completed_at) > max_age:
                    self.task_queue.remove(task.task_id)

    def shutdown(self):
        """关闭任务管理器"""
        for worker in self.workers:
            worker.stop()


# 全局任务管理器实例
_task_manager: Optional[AsyncTaskManager] = None


def get_task_manager() -> AsyncTaskManager:
    """获取任务管理器单例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager(num_workers=4)
    return _task_manager


def async_task(
    priority: TaskPriority = TaskPriority.NORMAL,
    max_retries: int = 3
):
    """异步任务装饰器"""
    manager = get_task_manager()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 提交到任务队列
            task_id = manager.submit_task(
                func,
                *args,
                priority=priority,
                max_retries=max_retries,
                **kwargs
            )
            return task_id

        return wrapper

    return decorator


# 预定义的任务
def export_story_task(story_id: str, format: str = "json") -> str:
    """导出故事任务"""
    time.sleep(2)  # 模拟耗时操作
    return f"Story {story_id} exported as {format}"


def generate_report_task(story_id: str) -> str:
    """生成报告任务"""
    time.sleep(3)  # 模拟耗时操作
    return f"Report generated for story {story_id}"


def send_notification_task(user_id: str, message: str) -> bool:
    """发送通知任务"""
    time.sleep(1)  # 模拟耗时操作
    print(f"Notification sent to {user_id}: {message}")
    return True


# 使用示例
if __name__ == "__main__":
    manager = get_task_manager()

    # 提交任务
    task_id = manager.submit_task(
        export_story_task,
        "story-123",
        "pdf",
        priority=TaskPriority.HIGH
    )

    print(f"Task submitted: {task_id}")

    # 查询任务状态
    time.sleep(0.5)
    status = manager.get_task_status(task_id)
    print(f"Task status: {json.dumps(status, indent=2)}")

    # 获取统计信息
    stats = manager.get_stats()
    print(f"Manager stats: {json.dumps(stats, indent=2)}")

    # 等待任务完成
    time.sleep(3)
    status = manager.get_task_status(task_id)
    print(f"Final status: {json.dumps(status, indent=2)}")

"""
缓存系统模块
提供多层缓存策略和失效机制
"""

import json
import hashlib
import threading
from typing import Optional, Any, Callable, List, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
import time


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    ttl: int  # 秒
    created_at: float = field(default_factory=time.time)
    hits: int = 0
    tags: List[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> float:
        """获取缓存年龄（秒）"""
        return time.time() - self.created_at


class MemoryCache:
    """内存缓存实现（后备方案）"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None

            entry = self.cache[key]

            # 检查是否过期
            if entry.is_expired:
                del self.cache[key]
                self.stats["misses"] += 1
                return None

            entry.hits += 1
            self.stats["hits"] += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: Optional[List[str]] = None):
        """设置缓存值"""
        with self.lock:
            # 如果缓存已满，清理最旧的条目
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()

            ttl = ttl or self.default_ttl
            self.cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl=ttl,
                tags=tags or []
            )
            self.stats["sets"] += 1

    def delete(self, key: str):
        """删除缓存值"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()

    def delete_by_tag(self, tag: str):
        """按标签删除缓存"""
        with self.lock:
            keys_to_delete = [
                key for key, entry in self.cache.items()
                if tag in entry.tags
            ]
            for key in keys_to_delete:
                del self.cache[key]

    def _evict_oldest(self):
        """淘汰最旧的条目（LRU）"""
        if not self.cache:
            return

        # 找到最少使用的条目
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].hits, self.cache[k].age)
        )
        del self.cache[oldest_key]
        self.stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            **self.stats,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": round(hit_rate * 100, 2),
            "memory_usage_mb": round(
                sum(
                    len(str(entry.value))
                    for entry in self.cache.values()
                ) / (1024 * 1024),
                2
            )
        }

    def cleanup_expired(self):
        """清理过期条目"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)


class CacheStrategy:
    """缓存策略管理器"""

    # 预定义的缓存策略
    STRATEGIES = {
        "story": {"ttl": 3600, "tags": ["story"]},  # 1小时
        "node_tree": {"ttl": 1800, "tags": ["node", "tree"]},  # 30分钟
        "user_session": {"ttl": 7200, "tags": ["session"]},  # 2小时
        "media": {"ttl": 86400, "tags": ["media"]},  # 24小时
        "api_response": {"ttl": 300, "tags": ["api"]},  # 5分钟
        "static": {"ttl": 604800, "tags": ["static"]},  # 7天
    }

    @classmethod
    def get_strategy(cls, strategy_name: str) -> Dict[str, Any]:
        """获取预定义策略"""
        return cls.STRATEGIES.get(strategy_name, {"ttl": 3600, "tags": []})


def cache_key(
    prefix: str,
    *args,
    **kwargs
) -> str:
    """生成缓存键"""
    # 将参数序列化为字符串
    parts = [prefix]

    if args:
        parts.extend(str(arg) for arg in args)

    if kwargs:
        # 对 kwargs 排序以确保一致性
        sorted_kwargs = sorted(kwargs.items())
        parts.append(str(sorted_kwargs))

    key_string = ":".join(parts)

    # 如果键太长，使用哈希
    if len(key_string) > 200:
        hash_obj = hashlib.md5(key_string.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    return key_string


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    tags: Optional[List[str]] = None,
    strategy: Optional[str] = None
):
    """缓存装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取缓存实例
            cache = get_cache()

            # 生成缓存键
            key = cache_key(prefix, *args, **kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 确定缓存策略
            if strategy:
                cache_strategy = CacheStrategy.get_strategy(strategy)
                cache_ttl = cache_strategy["ttl"]
                cache_tags = cache_strategy["tags"]
            else:
                cache_ttl = ttl
                cache_tags = tags or []

            # 存入缓存
            cache.set(key, result, ttl=cache_ttl, tags=cache_tags)

            return result

        return wrapper

    return decorator


class CacheLayer:
    """多层缓存管理器"""

    def __init__(self):
        self.l1 = MemoryCache(max_size=100, default_ttl=300)  # L1: 热数据缓存
        self.l2 = MemoryCache(max_size=1000, default_ttl=3600)  # L2: 温数据缓存

    def get(self, key: str) -> Optional[Any]:
        """从多层缓存获取"""
        # 先查 L1
        value = self.l1.get(key)
        if value is not None:
            return value

        # 再查 L2
        value = self.l2.get(key)
        if value is not None:
            # 提升到 L1
            self.l1.set(key, value, ttl=300)
            return value

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置到多层缓存"""
        # 同时设置到 L1 和 L2
        self.l1.set(key, value, ttl=ttl or 300)
        self.l2.set(key, value, ttl=ttl or 3600)

    def invalidate(self, key: str):
        """使缓存失效"""
        self.l1.delete(key)
        self.l2.delete(key)

    def invalidate_by_tag(self, tag: str):
        """按标签使缓存失效"""
        self.l1.delete_by_tag(tag)
        self.l2.delete_by_tag(tag)

    def clear(self):
        """清空所有缓存"""
        self.l1.clear()
        self.l2.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取所有层级统计"""
        return {
            "l1": self.l1.get_stats(),
            "l2": self.l2.get_stats()
        }


# 全局缓存实例
_cache_layer: Optional[CacheLayer] = None


def get_cache() -> CacheLayer:
    """获取缓存层单例"""
    global _cache_layer
    if _cache_layer is None:
        _cache_layer = CacheLayer()
    return _cache_layer


class DistributedLock:
    """分布式锁（基于内存的简化实现）"""

    def __init__(self):
        self.locks: Dict[str, threading.Lock] = {}
        self.lock = threading.Lock()

    def acquire(self, key: str, timeout: float = 10) -> bool:
        """获取锁"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self.lock:
                if key not in self.locks:
                    self.locks[key] = threading.Lock()
                    lock = self.locks[key]

                    if lock.acquire(blocking=False):
                        return True

            time.sleep(0.01)

        return False

    def release(self, key: str):
        """释放锁"""
        with self.lock:
            if key in self.locks:
                self.locks[key].release()
                del self.locks[key]


def with_lock(key: str, timeout: float = 10):
    """分布式锁装饰器"""
    lock_manager = DistributedLock()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if lock_manager.acquire(key, timeout):
                try:
                    return func(*args, **kwargs)
                finally:
                    lock_manager.release(key)
            else:
                raise TimeoutError(f"Could not acquire lock for key: {key}")

        return wrapper

    return decorator


# 缓存预热
def warm_up_cache():
    """缓存预热"""
    cache = get_cache()

    # 预热常用数据
    # 这里可以添加预热的逻辑
    # 例如：加载热门故事、常用配置等

    print("Cache warmed up")


# 定期清理过期缓存
def start_cache_cleanup(interval: int = 300):
    """启动定期清理任务"""
    cache = get_cache()

    def cleanup_task():
        while True:
            time.sleep(interval)
            l1_expired = cache.l1.cleanup_expired()
            l2_expired = cache.l2.cleanup_expired()
            print(f"Cleaned up {l1_expired + l2_expired} expired cache entries")

    thread = threading.Thread(target=cleanup_task, daemon=True)
    thread.start()
    return thread

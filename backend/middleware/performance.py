"""
API 性能优化模块
提供响应压缩、缓存、限流等功能
"""

import gzip
import json
import time
import threading
from typing import Callable, Optional, Dict, Any
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class ResponseCompressor:
    """响应压缩器"""

    def __init__(self, min_size: int = 1024):
        self.min_size = min_size  # 最小压缩大小（字节）

    def compress(self, data: bytes, encoding: str = "gzip") -> bytes:
        """压缩数据"""
        if len(data) < self.min_size:
            return data

        if encoding == "gzip":
            return gzip.compress(data)
        else:
            return data

    def compress_json(self, obj: Any, encoding: str = "gzip") -> bytes:
        """压缩 JSON 对象"""
        json_str = json.dumps(obj, ensure_ascii=False)
        data = json_str.encode('utf-8')
        return self.compress(data, encoding)


class RateLimiter:
    """速率限制器"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        # 存储请求记录
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(
        self,
        key: str,
        window: str = "minute"
    ) -> tuple[bool, Optional[str]]:
        """检查是否允许请求"""
        current_time = time.time()

        with self.lock:
            # 清理过期记录
            self._cleanup_expired_requests(key, current_time)

            # 获取该 key 的请求记录
            request_times = self.requests[key]

            # 检查限制
            if window == "minute":
                limit = self.requests_per_minute
                window_start = current_time - 60
            elif window == "hour":
                limit = self.requests_per_hour
                window_start = current_time - 3600
            else:
                limit = self.burst_size
                window_start = current_time - 1  # 突发限制：1秒

            # 统计时间窗口内的请求数
            recent_requests = [
                req_time for req_time in request_times
                if req_time > window_start
            ]

            if len(recent_requests) >= limit:
                retry_after = int(window_start + 60 - current_time) + 1
                return False, f"Rate limit exceeded. Retry after {retry_after} seconds"

            # 记录本次请求
            self.requests[key].append(current_time)
            return True, None

    def _cleanup_expired_requests(self, key: str, current_time: float):
        """清理过期的请求记录"""
        if key in self.requests:
            # 只保留最近1小时的记录
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < 3600
            ]


class APICache:
    """API 响应缓存"""

    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()

    def _generate_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """生成缓存键"""
        key_parts = [endpoint]

        if params:
            # 对参数排序并序列化
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)

        key_string = ":".join(key_parts)

        # 使用哈希避免键过长
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """获取缓存响应"""
        key = self._generate_key(endpoint, params)

        with self.lock:
            if key in self.cache:
                response, expiry_time = self.cache[key]

                # 检查是否过期
                if time.time() < expiry_time:
                    return response
                else:
                    # 删除过期缓存
                    del self.cache[key]

        return None

    def set(
        self,
        endpoint: str,
        response: Any,
        ttl: Optional[int] = None,
        params: Optional[Dict] = None
    ):
        """设置缓存响应"""
        key = self._generate_key(endpoint, params)
        expiry_time = time.time() + (ttl or self.default_ttl)

        with self.lock:
            self.cache[key] = (response, expiry_time)

    def invalidate(self, endpoint: str, params: Optional[Dict] = None):
        """使缓存失效"""
        key = self._generate_key(endpoint, params)

        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """清空所有缓存"""
        with self.lock:
            self.cache.clear()

    def cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()

        with self.lock:
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if expiry < current_time
            ]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            total_entries = len(self.cache)
            current_time = time.time()
            expired_count = sum(
                1 for _, expiry in self.cache.values()
                if expiry < current_time
            )

            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_count,
                "expired_entries": expired_count
            }


class PerformanceMiddleware:
    """性能监控中间件"""

    def __init__(self):
        self.request_log: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def record_request(
        self,
        endpoint: str,
        duration_ms: float,
        status_code: int,
        response_size: int = 0
    ):
        """记录请求"""
        with self.lock:
            self.request_log[endpoint].append({
                "duration_ms": duration_ms,
                "status_code": status_code,
                "response_size": response_size,
                "timestamp": time.time()
            })

            # 只保留最近 1000 条记录
            if len(self.request_log[endpoint]) > 1000:
                self.request_log[endpoint] = self.request_log[endpoint][-1000:]

    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """获取端点统计"""
        with self.lock:
            if endpoint not in self.request_log:
                return {}

            requests = self.request_log[endpoint]

            if not requests:
                return {}

            durations = [r["duration_ms"] for r in requests]
            status_codes = [r["status_code"] for r in requests]

            return {
                "total_requests": len(requests),
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "p50_duration_ms": sorted(durations)[len(durations) // 2],
                "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
                "p99_duration_ms": sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0],
                "status_codes": {
                    code: status_codes.count(code)
                    for code in set(status_codes)
                }
            }

    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有端点统计"""
        with self.lock:
            return {
                endpoint: self.get_endpoint_stats(endpoint)
                for endpoint in self.request_log.keys()
            }

    def get_slow_requests(
        self,
        threshold_ms: float = 1000,
        limit: int = 10
    ) -> list:
        """获取慢请求"""
        with self.lock:
            slow_requests = []

            for endpoint, requests in self.request_log.items():
                for req in requests:
                    if req["duration_ms"] > threshold_ms:
                        slow_requests.append({
                            **req,
                            "endpoint": endpoint
                        })

            # 按时长排序
            slow_requests.sort(key=lambda x: x["duration_ms"], reverse=True)

            return slow_requests[:limit]


# 装饰器
def measure_performance(middleware: PerformanceMiddleware):
    """性能测量装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = func.__name__

            try:
                result = func(*args, **kwargs)

                # 计算响应大小（估算）
                response_size = len(json.dumps(result)) if result else 0

                # 记录成功请求
                duration = (time.time() - start_time) * 1000
                middleware.record_request(endpoint, duration, 200, response_size)

                return result

            except Exception as e:
                # 记录失败请求
                duration = (time.time() - start_time) * 1000
                middleware.record_request(endpoint, duration, 500, 0)
                raise e

        return wrapper

    return decorator


def cache_api_response(
    cache: APICache,
    ttl: Optional[int] = None
):
    """API 响应缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            endpoint = func.__name__
            params = kwargs if kwargs else None

            cached = cache.get(endpoint, params)
            if cached is not None:
                return cached

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(endpoint, result, ttl, params)

            return result

        return wrapper

    return decorator


def rate_limit(
    limiter: RateLimiter,
    key_func: Optional[Callable] = None
):
    """速率限制装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成限流 key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "default"

            # 检查是否允许请求
            allowed, error_msg = limiter.is_allowed(key)

            if not allowed:
                raise Exception(error_msg or "Rate limit exceeded")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# 全局实例
_compressor = ResponseCompressor()
_rate_limiter = RateLimiter()
_api_cache = APICache()
_perf_monitor = PerformanceMiddleware()


def get_compressor() -> ResponseCompressor:
    """获取压缩器单例"""
    return _compressor


def get_rate_limiter() -> RateLimiter:
    """获取速率限制器单例"""
    return _rate_limiter


def get_api_cache() -> APICache:
    """获取 API 缓存单例"""
    return _api_cache


def get_perf_monitor() -> PerformanceMiddleware:
    """获取性能监控器单例"""
    return _perf_monitor

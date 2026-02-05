"""
数据库优化模块
提供高性能的数据库访问和优化策略
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DatabaseConfig:
    """数据库配置"""
    database_path: str = "aion_stories.db"
    enable_wal: bool = True
    cache_size: int = -64000  # 64MB cache
    page_size: int = 4096
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    temp_store: str = "MEMORY"
    mmap_size: int = 268435456  # 256MB
    connection_pool_size: int = 5


class DatabaseOptimizer:
    """数据库优化器"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.local = threading.local()
        self._initialize_optimization()

    def _initialize_optimization(self):
        """初始化数据库优化设置"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 启用 WAL 模式
        if self.config.enable_wal:
            cursor.execute(f"PRAGMA journal_mode={self.config.journal_mode}")

        # 性能优化设置
        cursor.execute(f"PRAGMA cache_size={self.config.cache_size}")
        cursor.execute(f"PRAGMA page_size={self.config.page_size}")
        cursor.execute(f"PRAGMA synchronous={self.config.synchronous}")
        cursor.execute(f"PRAGMA temp_store={self.config.temp_store}")
        cursor.execute(f"PRAGMA mmap_size={self.config.mmap_size}")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA optimize")

        conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """获取线程本地连接"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(
                self.config.database_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN")
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def create_indexes(self):
        """创建性能优化索引"""
        index_sqls = [
            # Stories 表索引
            "CREATE INDEX IF NOT EXISTS idx_stories_updated ON stories(updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_stories_created ON stories(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status)",

            # Nodes 表索引
            "CREATE INDEX IF NOT EXISTS idx_nodes_story ON nodes(story_id)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_position ON nodes(position)",
            "CREATE INDEX IF NOT EXISTS idx_nodes_updated ON nodes(updated_at DESC)",

            # Media 表索引
            "CREATE INDEX IF NOT EXISTS idx_media_story ON media(story_id)",
            "CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type)",
            "CREATE INDEX IF NOT EXISTS idx_media_created ON media(created_at DESC)",
        ]

        with self.transaction() as cursor:
            for sql in index_sqls:
                try:
                    cursor.execute(sql)
                except sqlite3.OperationalError:
                    pass  # Index already exists

    def analyze_tables(self) -> Dict[str, Any]:
        """分析表统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            # 获取行数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # 获取表大小
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='{table}'")
            index_count = cursor.fetchone()[0]

            stats[table] = {
                "row_count": row_count,
                "index_count": index_count
            }

        return stats

    def get_slow_queries(self, threshold_ms: int = 100) -> List[Dict[str, Any]]:
        """获取慢查询（SQLite 限制，需要手动跟踪）"""
        # SQLite 没有内置的慢查询日志
        # 这里返回占位符，实际应用中需要在应用层记录
        return []

    def vacuum(self):
        """优化数据库文件大小"""
        conn = self.get_connection()
        conn.execute("VACUUM")

    def optimize(self):
        """优化数据库"""
        conn = self.get_connection()
        conn.execute("PRAGMA optimize")
        conn.execute("ANALYZE")

    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        conn = self.get_connection()
        cursor = conn.cursor()

        info = {}

        # 数据库大小
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size = cursor.fetchone()[0]
        info["size_bytes"] = size
        info["size_mb"] = round(size / (1024 * 1024), 2)

        # WAL 模式状态
        cursor.execute("PRAGMA journal_mode")
        info["journal_mode"] = cursor.fetchone()[0]

        # 页面大小
        cursor.execute("PRAGMA page_size")
        info["page_size"] = cursor.fetchone()[0]

        # 缓存大小
        cursor.execute("PRAGMA cache_size")
        info["cache_size_kb"] = abs(cursor.fetchone()[0])

        # 当前连接数（SQLite 限制，返回估计值）
        info["estimated_connections"] = self.config.connection_pool_size

        return info


class QueryOptimizer:
    """查询优化器"""

    def __init__(self, db: DatabaseOptimizer):
        self.db = db

    def optimize_story_query(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
        order_by: str = "updated_at"
    ) -> List[Dict[str, Any]]:
        """优化的故事查询"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 构建 SQL
        sql = "SELECT * FROM stories"
        params = []

        if status_filter:
            sql += " WHERE status = ?"
            params.append(status_filter)

        sql += f" ORDER BY {order_by} DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def batch_insert_nodes(self, nodes: List[Dict[str, Any]]) -> bool:
        """批量插入节点"""
        try:
            with self.db.transaction() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO nodes (
                        story_id, parent_id, position, content,
                        node_type, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            node['story_id'],
                            node.get('parent_id'),
                            node['position'],
                            node['content'],
                            node.get('node_type', 'text'),
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        )
                        for node in nodes
                    ]
                )
            return True
        except Exception as e:
            print(f"Batch insert error: {e}")
            return False

    def get_story_tree_optimized(self, story_id: str) -> Dict[str, Any]:
        """优化的故事树查询（使用递归 CTE）"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 使用递归 CTE 获取完整树结构
        sql = """
        WITH RECURSIVE tree AS (
            SELECT *, 0 as level, CAST(id as TEXT) as path
            FROM nodes
            WHERE story_id = ? AND parent_id IS NULL
            UNION ALL
            SELECT n.*, t.level + 1, t.path || '/' || n.id
            FROM nodes n
            JOIN tree t ON n.parent_id = t.id
        )
        SELECT * FROM tree ORDER BY path
        """

        cursor.execute(sql, (story_id,))
        rows = cursor.fetchall()

        return {
            "nodes": [dict(row) for row in rows],
            "total_count": len(rows)
        }


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, db: DatabaseOptimizer):
        self.db = db
        self.query_log: List[Dict[str, Any]] = []

    def log_query(
        self,
        query: str,
        duration_ms: float,
        row_count: int = 0
    ):
        """记录查询日志"""
        self.query_log.append({
            "query": query,
            "duration_ms": duration_ms,
            "row_count": row_count,
            "timestamp": datetime.now().isoformat()
        })

        # 只保留最近 1000 条记录
        if len(self.query_log) > 1000:
            self.query_log = self.query_log[-1000:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.query_log:
            return {
                "total_queries": 0,
                "avg_duration_ms": 0,
                "max_duration_ms": 0,
                "slow_queries": []
            }

        durations = [q["duration_ms"] for q in self.query_log]

        return {
            "total_queries": len(self.query_log),
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "slow_queries": [
                q for q in self.query_log
                if q["duration_ms"] > 100
            ][-10:]  # 最近 10 个慢查询
        }


# 全局数据库优化器实例
_db_optimizer: Optional[DatabaseOptimizer] = None


def get_db_optimizer(database_path: str = "aion_stories.db") -> DatabaseOptimizer:
    """获取数据库优化器单例"""
    global _db_optimizer
    if _db_optimizer is None:
        config = DatabaseConfig(database_path=database_path)
        _db_optimizer = DatabaseOptimizer(config)
        _db_optimizer.create_indexes()
    return _db_optimizer

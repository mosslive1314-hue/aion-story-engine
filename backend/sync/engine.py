"""
Cloud Sync Engine - 云同步引擎
基于Git的分布式同步系统，支持离线优先架构
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import sqlite3
import hashlib
import subprocess
from pathlib import Path


class SyncStatus(Enum):
    """同步状态"""
    SYNCED = "synced"  # 已同步
    PENDING = "pending"  # 待同步
    CONFLICT = "conflict"  # 冲突
    OFFLINE = "offline"  # 离线
    ERROR = "error"  # 错误


class ChangeType(Enum):
    """变更类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"


@dataclass
class ChangeSet:
    """变更集"""
    id: str
    timestamp: datetime = field(default_factory=datetime.now)
    changes: List[Dict[str, Any]] = field(default_factory=list)
    parent_id: Optional[str] = None
    synced: bool = False
    conflict_detected: bool = False

    def calculate_hash(self) -> str:
        """计算变更集哈希"""
        changes_str = json.dumps(self.changes, sort_keys=True)
        return hashlib.sha256(changes_str.encode()).hexdigest()


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    changes_synced: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    error_message: Optional[str] = None
    sync_time: timedelta = field(default_factory=lambda: timedelta(0))


class GitAdapter:
    """Git适配器"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def init_repo(self) -> bool:
        """初始化Git仓库"""
        try:
            if not (self.repo_path / ".git").exists():
                subprocess.run(
                    ["git", "init"],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git init failed: {e}")
            return False

    def commit(self, message: str, author: str = "AION <aion@local>") -> bool:
        """提交变更"""
        try:
            # 添加所有变更
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )

            # 提交
            subprocess.run(
                ["git", "commit", "-m", message, f"--author={author}"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            # 可能是空提交（没有变更）
            return False

    def pull(self, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
        """拉取远程变更"""
        try:
            result = subprocess.run(
                ["git", "pull", remote, branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)

    def push(self, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
        """推送本地变更"""
        try:
            result = subprocess.run(
                ["git", "push", remote, branch],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)

    def get_current_commit(self) -> Optional[str]:
        """获取当前提交哈希"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def has_conflicts(self) -> bool:
        """检查是否有冲突"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            # 检查是否有未合并的文件
            return "UU" in result.stdout or "AA" in result.stdout
        except subprocess.CalledProcessError:
            return False

    def create_branch(self, branch_name: str) -> bool:
        """创建分支"""
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def merge_branch(self, branch_name: str) -> Tuple[bool, str]:
        """合并分支"""
        try:
            result = subprocess.run(
                ["git", "merge", branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)


class SQLiteAdapter:
    """SQLite数据库适配器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建变更集表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_sets (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                parent_id TEXT,
                synced BOOLEAN DEFAULT 0,
                conflict_detected BOOLEAN DEFAULT 0,
                hash TEXT,
                data TEXT
            )
        """)

        # 创建同步状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_sync TEXT,
                status TEXT,
                remote_commit TEXT,
                local_commit TEXT,
                error_message TEXT
            )
        """)

        # 创建节点状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_states (
                node_id TEXT PRIMARY KEY,
                version INTEGER DEFAULT 0,
                last_modified TEXT,
                last_sync_hash TEXT,
                data TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save_change_set(self, change_set: ChangeSet) -> bool:
        """保存变更集"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO change_sets
                (id, timestamp, parent_id, synced, conflict_detected, hash, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                change_set.id,
                change_set.timestamp.isoformat(),
                change_set.parent_id,
                change_set.synced,
                change_set.conflict_detected,
                change_set.calculate_hash(),
                json.dumps([c for c in change_set.changes])
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving change set: {e}")
            return False

    def get_pending_change_sets(self) -> List[ChangeSet]:
        """获取待同步的变更集"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, timestamp, parent_id, synced, conflict_detected, data
                FROM change_sets
                WHERE synced = 0 AND conflict_detected = 0
                ORDER BY timestamp ASC
            """)

            change_sets = []
            for row in cursor.fetchall():
                changes = json.loads(row[5])
                change_set = ChangeSet(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    parent_id=row[2],
                    synced=bool(row[3]),
                    conflict_detected=bool(row[4]),
                    changes=changes
                )
                change_sets.append(change_set)

            conn.close()
            return change_sets
        except Exception as e:
            print(f"Error getting pending change sets: {e}")
            return []

    def mark_synced(self, change_set_id: str) -> bool:
        """标记变更集为已同步"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE change_sets
                SET synced = 1
                WHERE id = ?
            """, (change_set_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking synced: {e}")
            return False

    def update_sync_status(self, status: SyncStatus, error_message: str = None,
                          remote_commit: str = None, local_commit: str = None):
        """更新同步状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sync_status
                (last_sync, status, remote_commit, local_commit, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                status.value,
                remote_commit,
                local_commit,
                error_message
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating sync status: {e}")

    def get_last_sync_status(self) -> Dict[str, Any]:
        """获取最后同步状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT last_sync, status, remote_commit, local_commit, error_message
                FROM sync_status
                ORDER BY id DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "last_sync": row[0],
                    "status": row[1],
                    "remote_commit": row[2],
                    "local_commit": row[3],
                    "error_message": row[4]
                }
            else:
                return {"status": "never"}
        except Exception as e:
            print(f"Error getting sync status: {e}")
            return {"status": "error"}

    def update_node_state(self, node_id: str, version: int, data: Dict[str, Any]):
        """更新节点状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO node_states
                (node_id, version, last_modified, data)
                VALUES (?, ?, ?, ?)
            """, (
                node_id,
                version,
                datetime.now().isoformat(),
                json.dumps(data)
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating node state: {e}")

    def get_node_state(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT version, last_modified, data
                FROM node_states
                WHERE node_id = ?
            """, (node_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "version": row[0],
                    "last_modified": row[1],
                    "data": json.loads(row[2]) if row[2] else {}
                }
            else:
                return None
        except Exception as e:
            print(f"Error getting node state: {e}")
            return None


class SyncEngine:
    """同步引擎主类"""

    def __init__(self, workspace_path: str, remote_url: Optional[str] = None):
        self.workspace_path = Path(workspace_path)
        self.remote_url = remote_url

        # 初始化适配器
        self.git = GitAdapter(str(self.workspace_path))
        self.db = SQLiteAdapter(str(self.workspace_path / "sync.db"))

        # 初始化Git仓库
        self.git.init_repo()

        # 变更集跟踪
        self.current_change_set: Optional[ChangeSet] = None
        self.pending_changes: List[Dict[str, Any]] = []

    def track_change(self, change_type: ChangeType, node_id: str, data: Dict[str, Any]):
        """跟踪变更"""
        change = {
            "type": change_type.value,
            "node_id": node_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.pending_changes.append(change)

    def commit_changes(self, message: str = "Auto-commit") -> ChangeSet:
        """提交变更"""
        # 创建变更集
        import uuid
        change_set = ChangeSet(
            id=str(uuid.uuid4()),
            changes=self.pending_changes.copy()
        )

        # 保存到数据库
        self.db.save_change_set(change_set)

        # Git提交
        self.git.commit(message)

        # 清空待提交变更
        self.pending_changes.clear()

        self.current_change_set = change_set
        return change_set

    def sync(self, strategy: str = "merge") -> SyncResult:
        """
        同步到远程

        Args:
            strategy: 同步策略 ("merge", "rebase", "force")

        Returns:
            同步结果
        """
        start_time = datetime.now()
        result = SyncResult(success=False)

        try:
            # 检查远程
            if not self.remote_url:
                result.error_message = "No remote URL configured"
                self.db.update_sync_status(SyncStatus.OFFLINE, result.error_message)
                return result

            # 拉取远程变更
            pull_success, pull_output = self.git.pull()
            if not pull_success:
                # 可能是网络问题或首次推送
                if "fatal" in pull_output.lower() or "could not read" in pull_output.lower():
                    pass  # 继续尝试推送
                else:
                    result.error_message = f"Pull failed: {pull_output}"
                    self.db.update_sync_status(SyncStatus.ERROR, result.error_message)
                    return result

            # 检查冲突
            if self.git.has_conflicts():
                result.conflicts_detected = 1
                result.error_message = "Merge conflicts detected"
                self.db.update_sync_status(SyncStatus.CONFLICT, result.error_message)
                return result

            # 推送本地变更
            push_success, push_output = self.git.push()
            if not push_success:
                result.error_message = f"Push failed: {push_output}"
                self.db.update_sync_status(SyncStatus.ERROR, result.error_message)
                return result

            # 标记变更集为已同步
            pending_sets = self.db.get_pending_change_sets()
            for change_set in pending_sets:
                self.db.mark_synced(change_set.id)
                result.changes_synced += 1

            # 更新同步状态
            local_commit = self.git.get_current_commit()
            self.db.update_sync_status(SyncStatus.SYNCED, remote_commit=local_commit, local_commit=local_commit)

            result.success = True
            result.sync_time = datetime.now() - start_time

            return result

        except Exception as e:
            result.error_message = str(e)
            self.db.update_sync_status(SyncStatus.ERROR, result.error_message)
            result.sync_time = datetime.now() - start_time
            return result

    def get_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        pending_sets = self.db.get_pending_change_sets()
        last_sync = self.db.get_last_sync_status()
        current_commit = self.git.get_current_commit()

        return {
            "pending_changes": len(pending_sets),
            "last_sync": last_sync.get("last_sync"),
            "sync_status": last_sync.get("status"),
            "current_commit": current_commit,
            "remote_url": self.remote_url,
            "has_conflicts": self.git.has_conflicts()
        }

    def resolve_conflicts(self, resolution: str = "theirs") -> bool:
        """
        解决冲突

        Args:
            resolution: 解决策略 ("theirs", "ours", "manual")
        """
        try:
            if resolution == "theirs":
                # 使用远程版本
                subprocess.run(
                    ["git", "checkout", "--theirs", "."],
                    cwd=self.workspace_path,
                    check=True,
                    capture_output=True
                )
            elif resolution == "ours":
                # 使用本地版本
                subprocess.run(
                    ["git", "checkout", "--ours", "."],
                    cwd=self.workspace_path,
                    check=True,
                    capture_output=True
                )

            # 添加已解决文件
            subprocess.run(
                ["git", "add", "."],
                cwd=self.workspace_path,
                check=True,
                capture_output=True
            )

            return True
        except subprocess.CalledProcessError as e:
            print(f"Error resolving conflicts: {e}")
            return False

    def create_backup(self) -> str:
        """创建备份"""
        import shutil
        backup_path = self.workspace_path.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(self.workspace_path, backup_path)
        return str(backup_path)

    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
        import shutil
        try:
            # 删除当前工作区
            for item in self.workspace_path.iterdir():
                if item.name != ".git":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # 复制备份
            backup = Path(backup_path)
            for item in backup.iterdir():
                if item.name != ".git":
                    if item.is_dir():
                        shutil.copytree(item, self.workspace_path / item.name)
                    else:
                        shutil.copy2(item, self.workspace_path / item.name)

            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False


# 全局同步引擎实例
_sync_engine: Optional[SyncEngine] = None


def get_sync_engine(workspace_path: str, remote_url: Optional[str] = None) -> SyncEngine:
    """获取同步引擎单例"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = SyncEngine(workspace_path, remote_url)
    return _sync_engine

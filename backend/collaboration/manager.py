"""
Collaboration System - 多用户协作系统
管理多用户会话、权限、冲突检测和解决
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from collections import defaultdict


class UserRole(Enum):
    """用户角色"""
    OWNER = "owner"  # 所有者
    EDITOR = "editor"  # 编辑者
    COMMENTER = "commenter"  # 评论者
    VIEWER = "viewer"  # 查看者


class Permission(Enum):
    """权限类型"""
    READ = "read"  # 读取
    WRITE = "write"  # 写入
    DELETE = "delete"  # 删除
    COMMENT = "comment"  # 评论
    MANAGE = "manage"  # 管理


class ConflictType(Enum):
    """冲突类型"""
    CONCURRENT_EDIT = "concurrent_edit"  # 并发编辑
    DELETE_MODIFY = "delete_modify"  # 删除-修改冲突
    BRANCH_DIVERGENCE = "branch_divergence"  # 分支分歧
    VERSION_MISMATCH = "version_mismatch"  # 版本不匹配


@dataclass
class User:
    """用户"""
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Collaborator:
    """协作者"""
    user_id: str
    role: UserRole
    permissions: Set[Permission]
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class Change:
    """变更"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    node_id: str = ""
    change_type: str = ""  # create, update, delete
    old_value: Any = None
    new_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "node_id": self.node_id,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "metadata": self.metadata
        }


@dataclass
class Conflict:
    """冲突"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: ConflictType = ConflictType.CONCURRENT_EDIT
    changes: List[Change] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "conflict_type": self.conflict_type.value,
            "changes": [c.to_dict() for c in self.changes],
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolution": self.resolution
        }


@dataclass
class Session:
    """协作会话"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    story_id: str = ""
    collaborators: Dict[str, Collaborator] = field(default_factory=dict)
    changes: List[Change] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def add_collaborator(self, user: User, role: UserRole, permissions: Set[Permission]):
        """添加协作者"""
        collaborator = Collaborator(
            user_id=user.id,
            role=role,
            permissions=permissions
        )
        self.collaborators[user.id] = collaborator

    def remove_collaborator(self, user_id: str):
        """移除协作者"""
        if user_id in self.collaborators:
            del self.collaborators[user_id]

    def add_change(self, change: Change):
        """添加变更"""
        self.changes.append(change)

    def add_conflict(self, conflict: Conflict):
        """添加冲突"""
        self.conflicts.append(conflict)

    def get_active_users(self, timeout_minutes: int = 5) -> List[str]:
        """获取活跃用户"""
        timeout = datetime.now() - timedelta(minutes=timeout_minutes)
        return [
            user_id
            for user_id, collab in self.collaborators.items()
            if collab.last_active > timeout
        ]


class PermissionManager:
    """权限管理器"""

    # 角色默认权限
    ROLE_PERMISSIONS = {
        UserRole.OWNER: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.COMMENT, Permission.MANAGE},
        UserRole.EDITOR: {Permission.READ, Permission.WRITE, Permission.COMMENT},
        UserRole.COMMENTER: {Permission.READ, Permission.COMMENT},
        UserRole.VIEWER: {Permission.READ},
    }

    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[Permission]:
        """获取角色的默认权限"""
        return cls.ROLE_PERMISSIONS.get(role, set())

    @classmethod
    def has_permission(cls, permissions: Set[Permission], required: Permission) -> bool:
        """检查是否有权限"""
        return required in permissions


class ConflictDetector:
    """冲突检测器"""

    def detect_conflicts(self, changes: List[Change]) -> List[Conflict]:
        """检测冲突"""
        conflicts = []

        # 按节点分组变更
        changes_by_node = defaultdict(list)
        for change in changes:
            changes_by_node[change.node_id].append(change)

        # 检测每个节点的冲突
        for node_id, node_changes in changes_by_node.items():
            if len(node_changes) < 2:
                continue

            # 并发编辑冲突
            if self._is_concurrent(node_changes):
                conflicts.append(Conflict(
                    conflict_type=ConflictType.CONCURRENT_EDIT,
                    changes=node_changes
                ))

            # 删除-修改冲突
            if self._is_delete_modify(node_changes):
                conflicts.append(Conflict(
                    conflict_type=ConflictType.DELETE_MODIFY,
                    changes=node_changes
                ))

        return conflicts

    def _is_concurrent(self, changes: List[Change]) -> bool:
        """检查是否是并发编辑"""
        # 如果同一节点在短时间内有多个更新
        updates = [c for c in changes if c.change_type == "update"]
        if len(updates) < 2:
            return False

        # 检查时间窗口（5秒内）
        timestamps = [c.timestamp for c in updates]
        if max(timestamps) - min(timestamps) < timedelta(seconds=5):
            return True

        return False

    def _is_delete_modify(self, changes: List[Change]) -> bool:
        """检查是否是删除-修改冲突"""
        has_delete = any(c.change_type == "delete" for c in changes)
        has_modify = any(c.change_type in ["update", "create"] for c in changes)
        return has_delete and has_modify


class ConflictResolver:
    """冲突解决器"""

    def resolve_conflict(self, conflict: Conflict, strategy: str = "last_write_wins") -> Change:
        """解决冲突"""
        if conflict.conflict_type == ConflictType.CONCURRENT_EDIT:
            return self._resolve_concurrent_edit(conflict, strategy)
        elif conflict.conflict_type == ConflictType.DELETE_MODIFY:
            return self._resolve_delete_modify(conflict, strategy)
        else:
            # 默认：保留最后一个变更
            return conflict.changes[-1]

    def _resolve_concurrent_edit(self, conflict: Conflict, strategy: str) -> Change:
        """解决并发编辑冲突"""
        if strategy == "last_write_wins":
            # 最后写入胜出
            return max(conflict.changes, key=lambda c: c.timestamp)
        elif strategy == "first_write_wins":
            # 第一写入胜出
            return min(conflict.changes, key=lambda c: c.timestamp)
        elif strategy == "merge":
            # 合并变更
            return self._merge_changes(conflict.changes)
        else:
            return conflict.changes[-1]

    def _resolve_delete_modify(self, conflict: Conflict, strategy: str) -> Change:
        """解决删除-修改冲突"""
        if strategy == "delete_wins":
            # 删除操作优先
            delete_changes = [c for c in conflict.changes if c.change_type == "delete"]
            return delete_changes[0] if delete_changes else conflict.changes[-1]
        else:
            # 修改操作优先
            modify_changes = [c for c in conflict.changes if c.change_type != "delete"]
            return modify_changes[0] if modify_changes else conflict.changes[-1]

    def _merge_changes(self, changes: List[Change]) -> Change:
        """合并多个变更"""
        # 简化实现：保留最后一个变更
        # 实际应用中可能需要更复杂的合并逻辑
        return changes[-1]


class CollaborationManager:
    """协作管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/collaboration.json"
        self.sessions: Dict[str, Session] = {}
        self.users: Dict[str, User] = {}
        self.permission_manager = PermissionManager()
        self.conflict_detector = ConflictDetector()
        self.conflict_resolver = ConflictResolver()

        # 加载数据
        self._load_data()

    def create_session(self, story_id: str, owner: User) -> Session:
        """创建协作会话"""
        session = Session(story_id=story_id)

        # 添加所有者
        owner_permissions = self.permission_manager.get_permissions(UserRole.OWNER)
        session.add_collaborator(owner, UserRole.OWNER, owner_permissions)

        # 保存会话
        self.sessions[session.id] = session
        self.users[owner.id] = owner

        self._save_data()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)

    def join_session(self, session_id: str, user: User, role: UserRole) -> bool:
        """加入会话"""
        session = self.get_session(session_id)
        if not session:
            return False

        # 获取角色权限
        permissions = self.permission_manager.get_permissions(role)
        session.add_collaborator(user, role, permissions)
        self.users[user.id] = user

        self._save_data()
        return True

    def leave_session(self, session_id: str, user_id: str) -> bool:
        """离开会话"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.remove_collaborator(user_id)
        self._save_data()
        return True

    def submit_change(self, session_id: str, change: Change) -> bool:
        """提交变更"""
        session = self.get_session(session_id)
        if not session:
            return False

        # 检查权限
        collaborator = session.collaborators.get(change.user_id)
        if not collaborator:
            return False

        if not self.permission_manager.has_permission(collaborator.permissions, Permission.WRITE):
            return False

        # 添加变更
        session.add_change(change)

        # 检测冲突
        conflicts = self.conflict_detector.detect_conflicts(session.changes)
        for conflict in conflicts:
            session.add_conflict(conflict)

        # 更新活跃时间
        collaborator.last_active = datetime.now()

        self._save_data()
        return True

    def resolve_conflict(self, session_id: str, conflict_id: str, resolution: str, strategy: str = "last_write_wins") -> bool:
        """解决冲突"""
        session = self.get_session(session_id)
        if not session:
            return False

        # 查找冲突
        conflict = None
        for c in session.conflicts:
            if c.id == conflict_id:
                conflict = c
                break

        if not conflict:
            return False

        # 解决冲突
        resolved_change = self.conflict_resolver.resolve_conflict(conflict, strategy)
        conflict.resolved = True
        conflict.resolution = resolution

        self._save_data()
        return True

    def get_active_users(self, session_id: str, timeout_minutes: int = 5) -> List[Dict[str, Any]]:
        """获取活跃用户"""
        session = self.get_session(session_id)
        if not session:
            return []

        active_user_ids = session.get_active_users(timeout_minutes)
        active_users = []

        for user_id in active_user_ids:
            if user_id in self.users:
                user = self.users[user_id]
                collaborator = session.collaborators.get(user_id)

                active_users.append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "role": collaborator.role.value if collaborator else "viewer",
                    "last_active": collaborator.last_active.isoformat() if collaborator else None
                })

        return active_users

    def get_session_changes(self, session_id: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """获取会话变更"""
        session = self.get_session(session_id)
        if not session:
            return []

        changes = session.changes
        if since:
            changes = [c for c in changes if c.timestamp > since]

        return [c.to_dict() for c in changes]

    def get_session_conflicts(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话冲突"""
        session = self.get_session(session_id)
        if not session:
            return []

        return [c.to_dict() for c in session.conflicts if not c.resolved]

    def _load_data(self):
        """加载数据"""
        import os
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载会话
            for session_data in data.get("sessions", []):
                session = Session(
                    id=session_data["id"],
                    story_id=session_data["story_id"],
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    active=session_data.get("active", True)
                )

                # 加载协作者
                for collab_data in session_data.get("collaborators", []):
                    collaborator = Collaborator(
                        user_id=collab_data["user_id"],
                        role=UserRole(collab_data["role"]),
                        permissions={Permission(p) for p in collab_data["permissions"]},
                        joined_at=datetime.fromisoformat(collab_data["joined_at"]),
                        last_active=datetime.fromisoformat(collab_data["last_active"])
                    )
                    session.collaborators[collaborator.user_id] = collaborator

                # 加载变更
                for change_data in session_data.get("changes", []):
                    change = Change(
                        id=change_data["id"],
                        user_id=change_data["user_id"],
                        timestamp=datetime.fromisoformat(change_data["timestamp"]),
                        node_id=change_data["node_id"],
                        change_type=change_data["change_type"],
                        old_value=change_data.get("old_value"),
                        new_value=change_data.get("new_value"),
                        metadata=change_data.get("metadata", {})
                    )
                    session.changes.append(change)

                # 加载冲突
                for conflict_data in session_data.get("conflicts", []):
                    conflict = Conflict(
                        id=conflict_data["id"],
                        conflict_type=ConflictType(conflict_data["conflict_type"]),
                        resolved=conflict_data.get("resolved", False),
                        resolution=conflict_data.get("resolution"),
                        detected_at=datetime.fromisoformat(conflict_data["detected_at"])
                    )
                    session.conflicts.append(conflict)

                self.sessions[session.id] = session

            # 加载用户
            for user_data in data.get("users", []):
                user = User(
                    id=user_data["id"],
                    name=user_data["name"],
                    email=user_data["email"],
                    avatar_url=user_data.get("avatar_url"),
                    created_at=datetime.fromisoformat(user_data["created_at"])
                )
                self.users[user.id] = user

        except Exception as e:
            print(f"Error loading collaboration data: {e}")

    def _save_data(self):
        """保存数据"""
        import os
        try:
            data = {
                "sessions": [
                    {
                        "id": session.id,
                        "story_id": session.story_id,
                        "created_at": session.created_at.isoformat(),
                        "active": session.active,
                        "collaborators": [
                            {
                                "user_id": collab.user_id,
                                "role": collab.role.value,
                                "permissions": [p.value for p in collab.permissions],
                                "joined_at": collab.joined_at.isoformat(),
                                "last_active": collab.last_active.isoformat()
                            }
                            for collab in session.collaborators.values()
                        ],
                        "changes": [c.to_dict() for c in session.changes],
                        "conflicts": [c.to_dict() for c in session.conflicts]
                    }
                    for session in self.sessions.values()
                ],
                "users": [
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "avatar_url": user.avatar_url,
                        "created_at": user.created_at.isoformat()
                    }
                    for user in self.users.values()
                ]
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving collaboration data: {e}")


# 全局协作管理器实例
_collaboration_manager: Optional[CollaborationManager] = None


def get_collaboration_manager(storage_path: Optional[str] = None) -> CollaborationManager:
    """获取协作管理器单例"""
    global _collaboration_manager
    if _collaboration_manager is None:
        _collaboration_manager = CollaborationManager(storage_path)
    return _collaboration_manager

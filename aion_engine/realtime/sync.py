"""
实时同步引擎

实现多用户实时协作编辑的同步机制，包括冲突解决和变更合并
支持高级功能：操作变换(OT)、撤销/重做、分支合并、快照、版本向量
"""

import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from collections import defaultdict, deque


class OperationType(Enum):
    """操作类型"""
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    REPLACE = "replace"
    BATCH = "batch"
    SNAPSHOT = "snapshot"


class BranchStatus(Enum):
    """分支状态"""
    ACTIVE = "active"
    MERGED = "merged"
    ARCHIVED = "archived"


class UndoRedoType(Enum):
    """撤销重做类型"""
    UNDO = "undo"
    REDO = "redo"


@dataclass
class Operation:
    """文档操作 - 增强版，支持撤销重做和分支"""
    id: str
    type: OperationType
    position: int
    user_id: str
    content: Optional[str] = None
    length: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 0

    # 新增字段
    branch_id: Optional[str] = None  # 分支ID
    base_version: Optional[int] = None  # 基础版本（用于转换）
    undo_of: Optional[str] = None  # 撤销的操作ID
    redo_of: Optional[str] = None  # 重做的操作ID
    transformed_from: Optional[str] = None  # 从哪个操作转换而来
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """从字典创建操作"""
        data = data.copy()
        data['type'] = OperationType(data['type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

    def copy_with_id(self, new_id: str) -> 'Operation':
        """创建当前操作的副本（用于转换）"""
        return Operation(
            id=new_id,
            type=self.type,
            position=self.position,
            user_id=self.user_id,
            content=self.content,
            length=self.length,
            timestamp=self.timestamp,
            version=self.version,
            branch_id=self.branch_id,
            base_version=self.base_version,
            undo_of=self.undo_of,
            redo_of=self.redo_of,
            transformed_from=self.transformed_from or self.id,
            metadata=self.metadata.copy()
        )


@dataclass
class DocumentState:
    """文档状态"""
    content: str
    version: int
    operations: List[Operation] = field(default_factory=list)
    last_modified: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'content': self.content,
            'version': self.version,
            'operations': [op.to_dict() for op in self.operations],
            'last_modified': self.last_modified.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentState':
        """从字典创建文档状态"""
        return cls(
            content=data['content'],
            version=data['version'],
            operations=[Operation.from_dict(op) for op in data.get('operations', [])],
            last_modified=datetime.fromisoformat(data['last_modified'])
        )


@dataclass
class DocumentSnapshot:
    """文档快照"""
    snapshot_id: str
    document_id: str
    content: str
    version: int
    timestamp: datetime = field(default_factory=datetime.now)
    operations_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'snapshot_id': self.snapshot_id,
            'document_id': self.document_id,
            'content': self.content,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'operations_count': self.operations_count,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentSnapshot':
        """从字典创建快照"""
        return cls(
            snapshot_id=data['snapshot_id'],
            document_id=data['document_id'],
            content=data['content'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            operations_count=data.get('operations_count', 0),
            metadata=data.get('metadata', {})
        )


@dataclass
class DocumentBranch:
    """文档分支"""
    branch_id: str
    name: str
    source_branch: str
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    status: BranchStatus = BranchStatus.ACTIVE
    operations: List[Operation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_operation_count(self) -> int:
        """获取操作数量"""
        return len(self.operations)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'branch_id': self.branch_id,
            'name': self.name,
            'source_branch': self.source_branch,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'status': self.status.value,
            'operations_count': self.get_operation_count(),
            'metadata': self.metadata
        }


@dataclass
class VersionVector:
    """版本向量用于分布式一致性"""
    document_id: str
    vector: Dict[str, int] = field(default_factory=dict)  # user_id -> version
    timestamp: datetime = field(default_factory=datetime.now)

    def update(self, user_id: str, version: int) -> None:
        """更新版本向量"""
        if user_id not in self.vector or version > self.vector[user_id]:
            self.vector[user_id] = version
            self.timestamp = datetime.now()

    def get_version(self, user_id: str) -> int:
        """获取用户版本"""
        return self.vector.get(user_id, 0)

    def is_after(self, other: 'VersionVector') -> bool:
        """检查是否在另一个向量之后"""
        for user_id, version in other.vector.items():
            if self.vector.get(user_id, 0) < version:
                return False
        return True

    def merge(self, other: 'VersionVector') -> 'VersionVector':
        """合并两个版本向量"""
        merged = VersionVector(
            document_id=self.document_id,
            vector=self.vector.copy()
        )
        for user_id, version in other.vector.items():
            merged.update(user_id, version)
        return merged

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'document_id': self.document_id,
            'vector': self.vector,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionVector':
        """从字典创建版本向量"""
        return cls(
            document_id=data['document_id'],
            vector=data.get('vector', {}),
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class Conflict:
    """冲突信息"""
    operation1_id: str
    operation2_id: str
    position: int
    type: str  # 'concurrent', 'overlap'
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class ConflictResolver:
    """冲突解决器"""

    @staticmethod
    def resolve_insert_insert(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决两个插入操作的冲突"""
        # 基于时间戳和用户ID的简单策略
        # 实际应用中可以使用更复杂的算法（如 OT、CRDT）

        if op1.timestamp < op2.timestamp:
            # op1 在前，op2 需要调整位置
            if op2.position >= op1.position:
                op2.position += len(op1.content) if op1.content else 0
        else:
            # op2 在前，op1 需要调整位置
            if op1.position >= op2.position:
                op1.position += len(op2.content) if op2.content else 0

        return op1, op2

    @staticmethod
    def resolve_insert_delete(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决插入和删除操作的冲突"""
        # 判断哪个操作先发生
        if op1.timestamp < op2.timestamp:
            # op1 在前
            if op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
                # 插入在前，删除在后
                delete_start = op2.position
                delete_end = op2.position + op2.length
                insert_pos = op1.position

                if delete_start <= insert_pos < delete_end:
                    # 插入位置在删除范围内，调整插入位置
                    op1.position = delete_start
                elif insert_pos >= delete_end:
                    # 插入位置在删除范围后，调整位置
                    op1.position -= op2.length
        else:
            # op2 在前
            if op2.type == OperationType.INSERT and op1.type == OperationType.DELETE:
                # 删除在前，插入在后
                delete_start = op1.position
                delete_end = op1.position + op1.length
                insert_pos = op2.position

                if delete_start <= insert_pos < delete_end:
                    # 插入位置在删除范围内，调整插入位置
                    op2.position = delete_start
                elif insert_pos >= delete_end:
                    # 插入位置在删除范围后，调整位置
                    op2.position -= op1.length

        return op1, op2

    @staticmethod
    def resolve_delete_delete(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决两个删除操作的冲突"""
        # 合并重叠的删除范围
        start1 = op1.position
        end1 = op1.position + op1.length
        start2 = op2.position
        end2 = op2.position + op2.length

        # 计算重叠范围
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start < overlap_end:
            # 有重叠，调整删除长度
            if start1 < start2:
                # op1 在前
                op1.length = start2 - start1
            else:
                # op2 在前
                op2.length = start1 - start2

class AdvancedConflictResolver:
    """高级冲突解决器 - 支持操作变换(OT)"""

    @staticmethod
    def transform_insert_insert(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """变换两个插入操作 - 改进的 OT 算法"""
        op1_new = op1.copy_with_id(op1.id)
        op2_new = op2.copy_with_id(op2.id)

        # 如果两个操作在同一位置
        if op1.position == op2.position:
            # 基于用户ID决定顺序
            if op1.user_id < op2.user_id:
                # op1 在前，op2 位置后移
                op2_new.position += len(op1.content or "")
            else:
                # op2 在前，op1 位置后移
                op1_new.position += len(op2.content or "")
        # 如果 op2 在 op1 之后插入
        elif op2.position > op1.position:
            op2_new.position += len(op1.content or "")
        # 如果 op2 在 op1 之前插入
        else:
            op1_new.position += len(op2.content or "")

        return op1_new, op2_new

    @staticmethod
    def transform_delete_delete(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """变换两个删除操作"""
        op1_new = op1.copy_with_id(op1.id)
        op2_new = op2.copy_with_id(op2.id)

        start1 = op1.position
        end1 = op1.position + op1.length
        start2 = op2.position
        end2 = op2.position + op2.length

        # 如果两个删除范围重叠
        if start1 < end2 and start2 < end1:
            # 找到实际要删除的部分
            if start1 <= start2:
                # op1 在前
                op1_new.length = start2 - start1
            else:
                # op2 在前
                op2_new.length = start1 - start2

        return op1_new, op2_new

    @staticmethod
    def transform_insert_delete(insert_op: Operation, delete_op: Operation) -> Tuple[Operation, Operation]:
        """变换插入和删除操作"""
        insert_new = insert_op.copy_with_id(insert_op.id)
        delete_new = delete_op.copy_with_id(delete_op.id)

        # 如果插入在删除范围内
        if delete_op.position <= insert_op.position < delete_op.position + delete_op.length:
            # 插入位置前移
            insert_new.position = delete_op.position
        # 如果插入在删除范围之后
        elif insert_op.position >= delete_op.position + delete_op.length:
            # 插入位置前移删除长度
            insert_new.position -= delete_op.length

        return insert_new, delete_new

    @staticmethod
    def transform_operations(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """主变换函数 - 根据操作类型调用对应变换"""
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            return AdvancedConflictResolver.transform_insert_insert(op1, op2)
        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            return AdvancedConflictResolver.transform_delete_delete(op1, op2)
        elif op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
            return AdvancedConflictResolver.transform_insert_delete(op1, op2)
        elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
            # 交换操作顺序
            ins, dele = AdvancedConflictResolver.transform_insert_delete(op2, op1)
            return dele, ins

        return op1, op2

    @staticmethod
    def resolve_insert_insert(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决两个插入操作的冲突 - 兼容旧版本"""
        return AdvancedConflictResolver.transform_insert_insert(op1, op2)

    @staticmethod
    def resolve_insert_delete(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决插入和删除操作的冲突 - 兼容旧版本"""
        if op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
            return AdvancedConflictResolver.transform_insert_delete(op1, op2)
        elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
            ins, dele = AdvancedConflictResolver.transform_insert_delete(op2, op1)
            return dele, ins
        return op1, op2

    @staticmethod
    def resolve_delete_delete(op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决两个删除操作的冲突 - 兼容旧版本"""
        return AdvancedConflictResolver.transform_delete_delete(op1, op2)


class RealtimeSyncEngine:
    """实时同步引擎 - 增强版，支持分支、快照、版本向量"""

    def __init__(self):
        self.documents: Dict[str, DocumentState] = {}
        self.conflicts: Dict[str, List[Conflict]] = {}
        self.pending_operations: Dict[str, List[Operation]] = {}

        # 新增：分支、快照、版本向量
        self.branches: Dict[str, Dict[str, DocumentBranch]] = {}  # doc_id -> branch_id -> branch
        self.snapshots: Dict[str, List[DocumentSnapshot]] = {}  # doc_id -> snapshots
        self.version_vectors: Dict[str, VersionVector] = {}  # doc_id -> version_vector
        self.undo_history: Dict[str, Dict[str, deque]] = {}  # doc_id -> user_id -> undo_stack
        self.redo_history: Dict[str, Dict[str, deque]] = {}  # doc_id -> user_id -> redo_stack

    def create_document(self, doc_id: str, initial_content: str = "", created_by: str = "system") -> DocumentState:
        """创建新文档并初始化分支和版本向量"""
        state = DocumentState(
            content=initial_content,
            version=1
        )
        self.documents[doc_id] = state

        # 初始化主分支
        self.branches[doc_id] = {
            'main': DocumentBranch(
                branch_id='main',
                name='Main Branch',
                source_branch='',
                created_by=created_by
            )
        }

        # 初始化版本向量
        self.version_vectors[doc_id] = VersionVector(document_id=doc_id)

        # 初始化撤销/重做历史
        self.undo_history[doc_id] = defaultdict(deque)
        self.redo_history[doc_id] = defaultdict(deque)

        return state

    def get_document(self, doc_id: str) -> Optional[DocumentState]:
        """获取文档"""
        return self.documents.get(doc_id)

    def apply_operation(self, doc_id: str, operation: Operation) -> Tuple[bool, List[Conflict]]:
        """
        应用操作到文档（增强版，支持 OT）
        """
        if doc_id not in self.documents:
            return False, []

        doc = self.documents[doc_id]

        # 检查版本冲突并应用操作变换
        conflicts = []
        transformed_op = operation

        if operation.version < doc.version:
            # 版本落后，需要进行操作变换
            # 检查最近的操作是否有冲突
            recent_ops = [op for op in doc.operations if op.timestamp > datetime.fromtimestamp(operation.timestamp.timestamp() - 1)]

            for recent_op in recent_ops:
                conflict = self._detect_conflict(transformed_op, recent_op)
                if conflict:
                    conflicts.append(conflict)

                    # 使用高级冲突解决器进行操作变换
                    op1, op2 = AdvancedConflictResolver.transform_operations(transformed_op, recent_op)
                    transformed_op = op1

        # 应用操作到内容
        self._apply_to_content(doc, transformed_op)

        # 更新文档
        transformed_op.id = transformed_op.id or str(uuid.uuid4())
        doc.operations.append(transformed_op)
        doc.version += 1
        doc.last_modified = datetime.now()

        # 存储冲突
        if doc_id not in self.conflicts:
            self.conflicts[doc_id] = []
        self.conflicts[doc_id].extend(conflicts)

        # 添加到撤销历史
        if doc_id in self.undo_history:
            undo_stack = self.undo_history[doc_id][transformed_op.user_id]
            undo_stack.append(transformed_op)
            # 限制撤销栈大小
            if len(undo_stack) > 100:
                undo_stack.popleft()

        # 更新版本向量
        if doc_id in self.version_vectors:
            self.version_vectors[doc_id].update(transformed_op.user_id, doc.version)

        # 添加到分支（如果指定了分支）
        if transformed_op.branch_id and doc_id in self.branches:
            branch_id = transformed_op.branch_id
            if branch_id in self.branches[doc_id]:
                self.branches[doc_id][branch_id].operations.append(transformed_op)

        return True, conflicts

    def _detect_conflict(self, op1: Operation, op2: Operation) -> Optional[Conflict]:
        """检测两个操作之间的冲突"""
        # 简化的时间戳检查
        time_diff = abs((op1.timestamp - op2.timestamp).total_seconds())

        if time_diff > 1.0:  # 如果时间差超过1秒，认为是顺序执行
            return None

        # 检查位置重叠
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            if self._ranges_overlap(op1.position, op1.position + len(op1.content or ""),
                                   op2.position, op2.position + len(op2.content or "")):
                return Conflict(
                    operation1_id=op1.id,
                    operation2_id=op2.id,
                    position=min(op1.position, op2.position),
                    type='concurrent'
                )

        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            if self._ranges_overlap(op1.position, op1.position + op1.length,
                                   op2.position, op2.position + op2.length):
                return Conflict(
                    operation1_id=op1.id,
                    operation2_id=op2.id,
                    position=min(op1.position, op2.position),
                    type='overlap'
                )

        elif op1.type != op2.type:
            # 插入和删除冲突
            if self._ranges_overlap(op1.position, op1.position + (len(op1.content or "") if op1.type == OperationType.INSERT else op1.length),
                                   op2.position, op2.position + (len(op2.content or "") if op2.type == OperationType.INSERT else op2.length)):
                return Conflict(
                    operation1_id=op1.id,
                    operation2_id=op2.id,
                    position=min(op1.position, op2.position),
                    type='concurrent'
                )

        return None

    def _resolve_conflict(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """解决操作冲突"""
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            return ConflictResolver.resolve_insert_insert(op1, op2)
        elif (op1.type == OperationType.INSERT and op2.type == OperationType.DELETE) or \
             (op1.type == OperationType.DELETE and op2.type == OperationType.INSERT):
            return ConflictResolver.resolve_insert_delete(op1, op2)
        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            return ConflictResolver.resolve_delete_delete(op1, op2)

        return op1, op2

    def _apply_to_content(self, doc: DocumentState, operation: Operation):
        """将操作应用到文档内容"""
        if operation.type == OperationType.INSERT:
            # 插入内容
            if 0 <= operation.position <= len(doc.content):
                before = doc.content[:operation.position]
                after = doc.content[operation.position:]
                doc.content = before + (operation.content or "") + after

        elif operation.type == OperationType.DELETE:
            # 删除内容
            if 0 <= operation.position < len(doc.content):
                end_pos = min(operation.position + operation.length, len(doc.content))
                deleted_content = doc.content[operation.position:end_pos]
                before = doc.content[:operation.position]
                after = doc.content[end_pos:]
                doc.content = before + after
                # 存储删除的内容到操作的元数据中，用于撤销
                operation.metadata['deleted_content'] = deleted_content

        elif operation.type == OperationType.UPDATE:
            # 更新内容（简化实现）
            if 0 <= operation.position < len(doc.content):
                end_pos = min(operation.position + operation.length, len(doc.content))
                before = doc.content[:operation.position]
                after = doc.content[end_pos:]
                doc.content = before + (operation.content or "") + after

    def _ranges_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """检查两个范围是否重叠"""
        return max(start1, start2) < min(end1, end2)

    def get_document_history(self, doc_id: str, limit: int = 100) -> List[Operation]:
        """获取文档操作历史"""
        if doc_id not in self.documents:
            return []

        doc = self.documents[doc_id]
        return doc.operations[-limit:]

    def get_conflicts(self, doc_id: str) -> List[Conflict]:
        """获取文档的冲突列表"""
        return self.conflicts.get(doc_id, [])

    def resolve_conflict(self, doc_id: str, conflict_id: str, resolution: str) -> bool:
        """解决冲突"""
        if doc_id not in self.conflicts:
            return False

        # 简化的冲突解决
        for conflict in self.conflicts[doc_id]:
            if conflict.operation1_id == conflict_id or conflict.operation2_id == conflict_id:
                conflict.resolved = True
                return True

        return False

    def get_sync_state(self, doc_id: str) -> Dict[str, Any]:
        """获取同步状态"""
        if doc_id not in self.documents:
            return {}

        doc = self.documents[doc_id]
        return {
            'document': doc.to_dict(),
            'conflicts': [c.to_dict() for c in self.get_conflicts(doc_id)],
            'pending_operations': len(self.pending_operations.get(doc_id, []))
        }

    def merge_documents(self, source_id: str, target_id: str) -> bool:
        """合并两个文档（简化实现）"""
        if source_id not in self.documents or target_id not in self.documents:
            return False

        source_doc = self.documents[source_id]
        target_doc = self.documents[target_id]

        # 简单追加内容（实际应用中需要更复杂的合并逻辑）
        target_doc.content += "\n" + source_doc.content
        target_doc.version += 1
        target_doc.operations.extend(source_doc.operations)

        return True

    # ==================== 新增功能：分支管理 ====================

    def create_branch(self, doc_id: str, branch_id: str, source_branch: str = 'main', created_by: str = "") -> bool:
        """创建新分支"""
        if doc_id not in self.documents or doc_id not in self.branches:
            return False

        if source_branch not in self.branches[doc_id]:
            return False

        if branch_id in self.branches[doc_id]:
            return False

        self.branches[doc_id][branch_id] = DocumentBranch(
            branch_id=branch_id,
            name=f"Branch {branch_id}",
            source_branch=source_branch,
            created_by=created_by
        )

        return True

    def get_branch(self, doc_id: str, branch_id: str) -> Optional[DocumentBranch]:
        """获取分支"""
        return self.branches.get(doc_id, {}).get(branch_id)

    def get_all_branches(self, doc_id: str) -> List[DocumentBranch]:
        """获取所有分支"""
        return list(self.branches.get(doc_id, {}).values())

    def merge_branch(self, doc_id: str, source_branch: str, target_branch: str = 'main') -> Tuple[bool, List[Conflict]]:
        """合并分支"""
        if doc_id not in self.branches:
            return False, []

        if source_branch not in self.branches[doc_id] or target_branch not in self.branches[doc_id]:
            return False, []

        source = self.branches[doc_id][source_branch]
        target = self.branches[doc_id][target_branch]

        conflicts = []
        # 简化实现：应用所有源分支操作到目标分支
        for operation in source.operations:
            # 应用操作到主文档
            success, ops_conflicts = self.apply_operation(doc_id, operation)
            if not success:
                return False, []
            conflicts.extend(ops_conflicts)

        # 更新分支状态
        source.status = BranchStatus.MERGED

        return True, conflicts

    # ==================== 新增功能：快照管理 ====================

    def create_snapshot(self, doc_id: str, snapshot_id: str, metadata: Dict[str, Any] = None) -> bool:
        """创建文档快照"""
        if doc_id not in self.documents:
            return False

        if metadata is None:
            metadata = {}

        doc = self.documents[doc_id]
        snapshot = DocumentSnapshot(
            snapshot_id=snapshot_id,
            document_id=doc_id,
            content=doc.content,
            version=doc.version,
            operations_count=len(doc.operations),
            metadata=metadata
        )

        if doc_id not in self.snapshots:
            self.snapshots[doc_id] = []
        self.snapshots[doc_id].append(snapshot)

        return True

    def restore_snapshot(self, doc_id: str, snapshot_id: str) -> bool:
        """从快照恢复文档"""
        if doc_id not in self.snapshots:
            return False

        snapshot = None
        for snap in self.snapshots[doc_id]:
            if snap.snapshot_id == snapshot_id:
                snapshot = snap
                break

        if snapshot is None:
            return False

        doc = self.documents[doc_id]
        doc.content = snapshot.content
        doc.version = snapshot.version
        doc.operations = doc.operations[:snapshot.operations_count]
        doc.last_modified = datetime.now()

        return True

    def get_snapshots(self, doc_id: str) -> List[DocumentSnapshot]:
        """获取文档快照列表"""
        return self.snapshots.get(doc_id, [])

    # ==================== 新增功能：撤销/重做 ====================

    def undo(self, doc_id: str, user_id: str) -> Tuple[bool, Optional[Operation]]:
        """撤销操作"""
        if doc_id not in self.documents:
            return False, None

        # 检查用户的撤销栈是否存在且非空
        if doc_id not in self.undo_history or user_id not in self.undo_history[doc_id]:
            return False, None

        undo_stack = self.undo_history[doc_id][user_id]
        redo_stack = self.redo_history[doc_id][user_id]

        if not undo_stack:
            return False, None

        # 弹出最后一个操作
        operation = undo_stack.pop()

        # 创建逆操作
        inverse_op = self._create_inverse_operation(operation)
        if inverse_op:
            self._apply_to_content(self.documents[doc_id], inverse_op)
            redo_stack.append(operation)

            # 更新文档版本
            self.documents[doc_id].version += 1
            self.documents[doc_id].operations.append(inverse_op)
            self.documents[doc_id].last_modified = datetime.now()

            return True, inverse_op

        return False, None

    def redo(self, doc_id: str, user_id: str) -> Tuple[bool, Optional[Operation]]:
        """重做操作"""
        if doc_id not in self.documents:
            return False, None

        # 检查用户的重做栈是否存在且非空
        if doc_id not in self.redo_history or user_id not in self.redo_history[doc_id]:
            return False, None

        redo_stack = self.redo_history[doc_id][user_id]
        undo_stack = self.undo_history[doc_id][user_id]

        if not redo_stack:
            return False, None

        # 弹出最后一个重做操作
        operation = redo_stack.pop()

        # 应用操作
        self._apply_to_content(self.documents[doc_id], operation)
        undo_stack.append(operation)

        # 更新文档版本
        self.documents[doc_id].version += 1
        self.documents[doc_id].operations.append(operation)
        self.documents[doc_id].last_modified = datetime.now()

        return True, operation

    def _create_inverse_operation(self, operation: Operation) -> Optional[Operation]:
        """创建逆操作"""
        if operation.type == OperationType.INSERT:
            # 插入的逆操作是删除
            return Operation(
                id=str(uuid.uuid4()),
                type=OperationType.DELETE,
                position=operation.position,
                user_id=operation.user_id,
                length=len(operation.content or ""),
                timestamp=datetime.now(),
                version=operation.version + 1,
                undo_of=operation.id
            )
        elif operation.type == OperationType.DELETE:
            # 删除的逆操作是插入
            return Operation(
                id=str(uuid.uuid4()),
                type=OperationType.INSERT,
                position=operation.position,
                user_id=operation.user_id,
                content=self._get_deleted_content(operation),
                timestamp=datetime.now(),
                version=operation.version + 1,
                undo_of=operation.id
            )

        return None

    def _get_deleted_content(self, operation: Operation) -> str:
        """获取被删除的内容"""
        # 首先尝试从操作的元数据中获取
        deleted_content = operation.metadata.get('deleted_content')
        if deleted_content:
            return deleted_content

        # 如果元数据中没有，尝试从文档历史中重建（简化实现）
        # 在实际应用中，应该始终在删除时存储删除的内容
        return ""

    def get_undo_stack(self, doc_id: str, user_id: str) -> List[Operation]:
        """获取撤销栈"""
        return list(self.undo_history.get(doc_id, {}).get(user_id, []))

    def get_redo_stack(self, doc_id: str, user_id: str) -> List[Operation]:
        """获取重做栈"""
        return list(self.redo_history.get(doc_id, {}).get(user_id, []))

    # ==================== 新增功能：批量操作 ====================

    def apply_batch_operations(self, doc_id: str, operations: List[Operation]) -> Tuple[bool, List[Conflict]]:
        """批量应用操作"""
        if doc_id not in self.documents:
            return False, []

        all_conflicts = []

        for operation in operations:
            success, conflicts = self.apply_operation(doc_id, operation)
            if not success:
                return False, all_conflicts
            all_conflicts.extend(conflicts)

        return True, all_conflicts

    # ==================== 新增功能：版本向量 ====================

    def get_version_vector(self, doc_id: str) -> Optional[VersionVector]:
        """获取版本向量"""
        return self.version_vectors.get(doc_id)

    def update_version_vector(self, doc_id: str, user_id: str, version: int) -> None:
        """更新版本向量"""
        if doc_id in self.version_vectors:
            self.version_vectors[doc_id].update(user_id, version)

    def compare_versions(self, doc_id: str, other_vector: VersionVector) -> bool:
        """比较版本向量"""
        local_vector = self.version_vectors.get(doc_id)
        if local_vector is None:
            return False
        return local_vector.is_after(other_vector)

    def merge_version_vectors(self, doc_id: str, other_vector: VersionVector) -> Optional[VersionVector]:
        """合并版本向量"""
        local_vector = self.version_vectors.get(doc_id)
        if local_vector is None:
            return None
        return local_vector.merge(other_vector)
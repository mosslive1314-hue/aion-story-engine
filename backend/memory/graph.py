"""
Memory Graph System - 记忆图谱系统
构建概念关系网络和场景记忆
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class RelationType(Enum):
    """关系类型"""
    IS_A = "is_a"  # 是一种
    PART_OF = "part_of"  # 是一部分
    RELATED_TO = "related_to"  # 相关
    CAUSES = "causes"  # 导致
    CAUSED_BY = "caused_by"  # 由...导致
    LOCATED_AT = "located_at"  # 位于
    CONTAINS = "contains"  # 包含
    PRECEDES = "precedes"  # 先于
    FOLLOWS = "follows"  # 后于
    OPPOSES = "opposes"  # 对立
    SIMILAR_TO = "similar_to"  # 相似于


@dataclass
class ConceptNode:
    """概念节点"""
    id: str
    label: str
    node_type: str  # 节点类型
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    strength: float = 1.0  # 节点强度（记忆强度）

    def update_access(self):
        """更新访问记录"""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def decay(self, decay_rate: float = 0.01):
        """记忆衰减"""
        self.strength = max(0.1, self.strength - decay_rate)


@dataclass
class ConceptRelation:
    """概念关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0  # 关系权重
    created_at: datetime = field(default_factory=datetime.now)
    last_confirmed: datetime = field(default_factory=datetime.now)

    def update_weight(self, delta: float):
        """更新权重"""
        self.weight = max(0.1, min(5.0, self.weight + delta))
        self.last_confirmed = datetime.now()


@dataclass
class EpisodicMemory:
    """情节记忆"""
    id: str
    timestamp: datetime
    context: Dict[str, Any]  # 上下文信息
    concepts: List[str]  # 涉及的概念ID
    narrative: str  # 叙述内容
    importance: float = 1.0  # 重要性
    decay_rate: float = 0.001  # 衰减率

    def get_age(self) -> timedelta:
        """获取记忆年龄"""
        return datetime.now() - self.timestamp

    def decay(self):
        """记忆衰减"""
        age = self.get_age()
        decay_factor = age.total_seconds() / 86400 * self.decay_rate  # 每日衰减
        self.importance = max(0.1, self.importance - decay_factor)


class MemoryGraph:
    """记忆图谱"""

    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.relations: Dict[str, ConceptRelation] = {}
        self.episodic_memories: List[EpisodicMemory] = []

    def add_node(
        self,
        label: str,
        node_type: str,
        attributes: Dict[str, Any] = None
    ) -> ConceptNode:
        """添加节点"""
        node_id = f"{node_type}_{label}_{datetime.now().timestamp()}"

        node = ConceptNode(
            id=node_id,
            label=label,
            node_type=node_type,
            attributes=attributes or {}
        )

        self.nodes[node_id] = node
        return node

    def get_or_create_node(
        self,
        label: str,
        node_type: str,
        attributes: Dict[str, Any] = None
    ) -> ConceptNode:
        """获取或创建节点"""
        # 查找是否存在相似的节点
        for node in self.nodes.values():
            if node.label == label and node.node_type == node_type:
                node.update_access()
                return node

        # 创建新节点
        return self.add_node(label, node_type, attributes)

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0
    ) -> ConceptRelation:
        """添加关系"""
        relation_id = f"{source_id}_{relation_type.value}_{target_id}"

        relation = ConceptRelation(
            id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight
        )

        self.relations[relation_id] = relation
        return relation

    def get_related_nodes(
        self,
        node_id: str,
        relation_type: Optional[RelationType] = None,
        max_depth: int = 1,
        min_weight: float = 0.3
    ) -> List[Tuple[ConceptNode, float]]:
        """获取相关节点"""
        if node_id not in self.nodes:
            return []

        related = []
        visited = set()
        queue = [(node_id, 0, 1.0)]  # (node_id, depth, weight)

        while queue:
            current_id, depth, weight = queue.pop(0)

            if depth > max_depth:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)

            # 查找相关关系
            for relation in self.relations.values():
                if relation.source_id == current_id:
                    target = self.nodes.get(relation.target_id)
                    if target and relation.weight >= min_weight:
                        if relation_type is None or relation.relation_type == relation_type:
                            new_weight = weight * relation.weight
                            related.append((target, new_weight))
                            queue.append((target.id, depth + 1, new_weight))

                elif relation.target_id == current_id:
                    source = self.nodes.get(relation.source_id)
                    if source and relation.weight >= min_weight:
                        if relation_type is None or relation.relation_type == relation_type:
                            new_weight = weight * relation.weight
                            related.append((source, new_weight))
                            queue.append((source.id, depth + 1, new_weight))

        # 按权重排序
        related.sort(key=lambda x: x[1], reverse=True)
        return related

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_length: int = 5
    ) -> Optional[List[str]]:
        """查找节点间路径"""
        # BFS 搜索
        queue = [(start_id, [start_id])]
        visited = set()

        while queue:
            current_id, path = queue.pop(0)

            if current_id == end_id:
                return path

            if len(path) > max_length:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)

            # 查找邻居
            neighbors = []
            for relation in self.relations.values():
                if relation.source_id == current_id:
                    neighbors.append(relation.target_id)
                elif relation.target_id == current_id:
                    neighbors.append(relation.source_id)

            for neighbor_id in neighbors:
                if neighbor_id not in visited and neighbor_id not in path:
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def memorize(self, context: Dict[str, Any], concepts: List[str], narrative: str):
        """记忆情节"""
        memory = EpisodicMemory(
            id=f"memory_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            context=context,
            concepts=concepts,
            narrative=narrative
        )

        self.episodic_memories.append(memory)

        # 创建或更新概念节点
        for concept_label in concepts:
            node = self.get_or_create_node(
                label=concept_label,
                node_type="concept",
                attributes={"context": context}
            )
            node.update_access()

    def recall(self, concepts: List[str], limit: int = 10) -> List[EpisodicMemory]:
        """回忆相关情节"""
        # 查找包含指定概念的记忆
        relevant_memories = []

        for memory in self.episodic_memories:
            # 计算概念重叠度
            overlap = len(set(memory.concepts) & set(concepts))
            if overlap > 0:
                relevant_memories.append((memory, overlap))

        # 按重叠度和重要性排序
        relevant_memories.sort(key=lambda x: (x[1] * x[0].importance), reverse=True)

        # 应用衰减
        for memory, _ in relevant_memories:
            memory.decay()

        return [memory for memory, _ in relevant_memories[:limit] if memory.importance > 0.3]

    def cleanup(self, min_strength: float = 0.2, max_age_days: int = 30):
        """清理弱记忆"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        # 清理弱节点
        weak_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.strength < min_strength
        ]

        # 清理旧记忆
        old_memories = [
            memory for memory in self.episodic_memories
            if memory.timestamp < cutoff_date or memory.importance < 0.2
        ]

        for node_id in weak_nodes:
            del self.nodes[node_id]

        # 清理相关关系
        self.relations = {
            rel_id: rel
            for rel_id, rel in self.relations.items()
            if rel.source_id not in weak_nodes and rel.target_id not in weak_nodes
        }

        self.episodic_memories = [
            memory for memory in self.episodic_memories
            if memory not in old_memories
        ]

        return {
            "removed_nodes": len(weak_nodes),
            "removed_memories": len(old_memories),
            "remaining_nodes": len(self.nodes),
            "remaining_memories": len(self.episodic_memories),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1

        relation_types = {}
        for relation in self.relations.values():
            rtype = relation.relation_type.value
            relation_types[rtype] = relation_types.get(rtype, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_relations": len(self.relations),
            "episodic_memories": len(self.episodic_memories),
            "node_types": node_types,
            "relation_types": relation_types,
        }


class SmartSuggestionEngine:
    """智能建议引擎"""

    def __init__(self, memory_graph: MemoryGraph):
        self.memory_graph = memory_graph

    def generate_suggestions(
        self,
        current_context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """生成智能建议"""
        suggestions = []

        # 1. 基于当前概念的建议
        current_concepts = current_context.get("concepts", [])
        if current_concepts:
            # 查找相关概念
            for concept_label in current_concepts:
                node = self.memory_graph.nodes.get(f"concept_{concept_label}")
                if node:
                    related = self.memory_graph.get_related_nodes(
                        node.id,
                        min_weight=0.5
                    )

                    for related_node, weight in related[:3]:
                        suggestions.append({
                            "type": "related_concept",
                            "title": f"探索 {related_node.label}",
                            "description": f"从 {concept_label} 到 {related_node.label} 的关联",
                            "confidence": weight,
                            "metadata": {
                                "concept": related_node.label,
                                "relation": "related"
                            }
                        })

        # 2. 基于历史情节的建议
        memories = self.memory_graph.recall(current_concepts, limit=limit)
        for memory in memories:
            if memory.importance > 0.6:
                suggestions.append({
                    "type": "similar_episode",
                    "title": f"类似情节参考",
                    "description": f"之前在 {memory.context.get('location', '某处')} 发生的类似情况",
                    "confidence": memory.importance,
                    "metadata": {
                        "timestamp": memory.timestamp.isoformat(),
                        "narrative": memory.narrative[:100] + "..."
                    }
                })

        # 3. 基于上下文的建议
        if "story_id" in current_context:
            suggestions.append({
                "type": "continue_story",
                "title": "继续创作",
                "description": "基于当前情节继续发展故事",
                "confidence": 0.8,
                "metadata": {}
            })

        # 排序和限制
        suggestions.sort(key=lambda s: s["confidence"], reverse=True)

        return suggestions[:limit]

    def learn_from_feedback(
        self,
        suggestion_id: str,
        feedback: bool,
        context: Dict[str, Any]
    ):
        """从反馈中学习"""
        # 更新相关概念节点的强度
        if feedback:
            # 正反馈：增强关联
            pass
        else:
            # 负反馈：降低关联
            pass


class DigitalTwin:
    """数字孪生：主类"""

    def __init__(self):
        self.memory_graph = MemoryGraph()
        self.suggestion_engine = SmartSuggestionEngine(self.memory_graph)
        self.intent_engine = None  # 将从 intent.engine 导入

    def process_interaction(
        self,
        user_input: str,
        context: Dict[str, Any],
        extracted_concepts: List[str]
    ) -> Dict[str, Any]:
        """处理用户交互"""
        # 1. 记忆当前情节
        narrative = context.get("narrative", user_input)
        self.memory_graph.memorize(
            context=context,
            concepts=extracted_concepts,
            narrative=narrative
        )

        # 2. 生成建议
        suggestions = self.suggestion_engine.generate_suggestions(context)

        return {
            "memorized": True,
            "suggestions": suggestions,
            "memory_stats": self.memory_graph.get_statistics()
        }

    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户画像摘要"""
        stats = self.memory_graph.get_statistics()

        return {
            "memory_graph_stats": stats,
            "total_interactions": len(self.memory_graph.episodic_memories),
            "concept_count": stats["total_nodes"],
            "relation_count": stats["total_relations"],
        }

    def cleanup_memories(self, max_age_days: int = 30):
        """清理旧记忆"""
        return self.memory_graph.cleanup(max_age_days=max_age_days)


# 全局数字孪生实例
_digital_twin: Optional[DigitalTwin] = None


def get_digital_twin() -> DigitalTwin:
    """获取数字孪生单例"""
    global _digital_twin
    if _digital_twin is None:
        _digital_twin = DigitalTwin()
    return _digital_twin

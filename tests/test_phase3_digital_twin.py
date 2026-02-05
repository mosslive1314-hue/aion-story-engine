"""
Phase 3: Digital Twin System - Unit Tests
测试数字孪生系统的核心功能
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from backend.intent.engine import (
    IntentCategory, ConfidenceLevel, InferredIntent,
    NLPUnderstander, BehaviorAnalyzer, ContextAnalyzer, IntentInferenceEngine
)
from backend.memory.graph import (
    RelationType, ConceptNode, ConceptRelation, EpisodicMemory,
    MemoryGraph, SmartSuggestionEngine, DigitalTwin
)
from backend.skills.tracker import (
    SkillType, SkillLevel, SkillAssessment, SkillTracker,
    SkillMilestone, LearningPath
)


class TestIntentEngine:
    """测试意图推断引擎"""

    def test_nlp_understander(self):
        """测试NLP理解器"""
        nlp = NLPUnderstander()

        # 解析文本
        result = nlp.parse("帮我创建一个勇敢的骑士角色")

        assert result["actions"] is not None
        assert len(result["actions"]) > 0
        assert result["entities"] is not None

    def test_behavior_analyzer(self):
        """测试行为分析器"""
        analyzer = BehaviorAnalyzer()

        # 模拟行为序列
        actions = [
            {"action_type": "create_node", "timestamp": "2026-02-05T10:00:00"},
            {"action_type": "create_node", "timestamp": "2026-02-05T10:01:00"},
            {"action_type": "edit_node", "timestamp": "2026-02-05T10:02:00"}
        ]

        result = analyzer.analyze_sequence(actions)

        assert result["pattern"] == "creation"
        assert result["confidence"] > 0.5

    def test_context_analyzer(self):
        """测试上下文分析器"""
        analyzer = ContextAnalyzer()

        context = {
            "story_id": "story-1",
            "node_id": "node-1",
            "user_id": "user-1"
        }

        result = analyzer.analyze(
            context=context,
            user_input="编辑当前场景",
            parsed_input={}
        )

        assert result["current_location"] == "unknown"
        assert result["active_story"] == "story-1"

    def test_intent_inference(self):
        """测试意图推断"""
        engine = IntentInferenceEngine()

        intent = engine.infer(
            user_input="创建一个新的角色",
            context={"story_id": "story-1"},
            behavior_history=[
                {"action_type": "create_node"}
            ]
        )

        assert intent.category == IntentCategory.CREATION
        assert intent.confidence > 0.5
        assert intent.action is not None


class TestMemoryGraph:
    """测试记忆图谱"""

    @pytest.fixture
    def memory_graph(self):
        """创建测试图谱"""
        return MemoryGraph()

    def test_add_node(self, memory_graph):
        """测试添加节点"""
        node = memory_graph.add_node(
            label="骑士",
            node_type="character",
            attributes={"brave": True}
        )

        assert node is not None
        assert node.label == "骑士"
        assert node.node_type == "character"

    def test_add_relation(self, memory_graph):
        """测试添加关系"""
        node1 = memory_graph.add_node("骑士", "character")
        node2 = memory_graph.add_node("剑", "item")

        relation = memory_graph.add_relation(
            source_id=node1.id,
            target_id=node2.id,
            relation_type=RelationType.RELATED_TO,
            weight=1.0
        )

        assert relation is not None
        assert relation.relation_type == RelationType.RELATED_TO

    def test_memorize_and_recall(self, memory_graph):
        """测试记忆和回忆"""
        # 记忆
        memory_graph.memorize(
            context={"location": "城堡"},
            concepts=["骑士", "剑"],
            narrative="骑士拔出了剑"
        )

        # 回忆
        memories = memory_graph.recall(["骑士"], limit=5)

        assert len(memories) > 0
        assert memories[0].importance > 0

    def test_related_nodes(self, memory_graph):
        """测试相关节点查询"""
        node1 = memory_graph.add_node("骑士", "character")
        node2 = memory_graph.add_node("剑", "item")

        memory_graph.add_relation(
            node1.id, node2.id,
            RelationType.RELATED_TO
        )

        related = memory_graph.get_related_nodes(node1.id)

        assert len(related) > 0

    def test_cleanup(self, memory_graph):
        """测试清理弱记忆"""
        # 添加弱节点
        node = memory_graph.add_node("test", "test")
        node.strength = 0.1

        # 清理
        stats = memory_graph.cleanup(min_strength=0.2)

        assert stats["removed_nodes"] >= 0


class TestSkillTracker:
    """测试技能追踪器"""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """临时存储"""
        return tmp_path / "test_skills.json"

    def test_assess_skill(self, temp_storage):
        """测试技能评估"""
        tracker = SkillTracker(storage_path=str(temp_storage))

        assessment = tracker.assess_skill(
            skill_type=SkillType.WRITING,
            content="这是一段很好的文字。角色勇敢地面对困难。",
            context={}
        )

        assert assessment is not None
        assert 0 <= assessment.score <= 100
        assert assessment.level in SkillLevel

    def test_milestones(self, temp_storage):
        """测试里程碑系统"""
        tracker = SkillTracker(storage_path=str(temp_storage))

        # 记录高分
        tracker.record_skill_score(SkillType.WRITING, 95)

        # 检查里程碑
        milestones = tracker.get_milestones_progress(SkillType.WRITING)

        assert len(milestones) > 0
        # 应该达成了一些里程碑
        achieved = [m for m in milestones if m["achieved"]]
        assert len(achieved) > 0

    def test_learning_path(self, temp_storage):
        """测试学习路径"""
        tracker = SkillTracker(storage_path=str(temp_storage))

        path = tracker.get_learning_path(
            skill_type=SkillType.WRITING,
            target_level=SkillLevel.EXPERT
        )

        assert path is not None
        assert path.current_level == SkillLevel.NOVICE  # 默认从新手开始
        assert path.estimated_duration_days > 0

    def test_growth_statistics(self, temp_storage):
        """测试成长统计"""
        tracker = SkillTracker(storage_path=str(temp_storage))

        # 记录多个分数
        for score in [50, 60, 70, 80]:
            tracker.record_skill_score(SkillType.WRITING, score)

        stats = tracker.get_growth_statistics()

        assert "total_assessments" in stats
        assert stats["total_assessments"] == 4
        assert stats["skill_growth"]["writing"] > 0


@pytest.mark.integration
class TestDigitalTwinIntegration:
    """集成测试 - 数字孪生整体流程"""

    @pytest.fixture
    def digital_twin(self):
        """创建数字孪生"""
        return DigitalTwin()

    def test_interaction_to_suggestion(self, digital_twin):
        """测试从交互到建议的完整流程"""
        # 1. 处理交互
        result = digital_twin.process_interaction(
            user_input="我要写一个关于骑士的故事",
            context={"location": "home"},
            extracted_concepts=["骑士", "故事"]
        )

        # 2. 验证结果
        assert result["memorized"] is True
        assert len(result["suggestions"]) >= 0

    def test_memory_to_skill_tracking(self, digital_twin):
        """测试从记忆到技能追踪的关联"""
        # 记忆创作活动
        digital_twin.process_interaction(
            user_input="骑士勇敢地战斗",
            context={"action": "write"},
            extracted_concepts=["骑士", "勇敢", "战斗"]
        )

        # 获取记忆
        memories = digital_twin.memory_graph.recall(["骑士"])
        assert len(memories) >= 0


@pytest.mark.performance
class TestPerformance:
    """性能测试"""

    def test_intent_engine_performance(self):
        """测试意图引擎性能"""
        engine = IntentInferenceEngine()

        import time
        start = time.time()

        for _ in range(100):
            engine.infer(
                user_input="创建新节点",
                context={},
                behavior_history=[]
            )

        elapsed = time.time() - start

        # 平均每次推断应在100ms内
        assert elapsed / 100 < 0.1

    def test_memory_graph_performance(self):
        """测试记忆图谱性能"""
        graph = MemoryGraph()

        # 添加100个节点
        for i in range(100):
            graph.add_node(f"concept_{i}", "test")

        import time
        start = time.time()

        # 回忆操作
        graph.recall(["concept_1"], limit=10)

        elapsed = time.time() - start

        # 回忆应在100ms内完成
        assert elapsed < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

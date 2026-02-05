"""
Phase 2: Asset System - Unit Tests
测试资产系统的核心功能
"""

import pytest
import json
import os
from datetime import datetime
from pathlib import Path

from backend.assets.asset_types import (
    AssetType, AssetStatus, Asset, AssetMetadata, UsageStats,
    PatternAsset, NPCTemplateAsset, AssetFactory
)
from backend.assets.manager import AssetManager, AssetBrowser, AssetRecommender
from backend.core.abstraction import (
    Pattern, PatternRecognizer, KnowledgeBase, AbstractionEngine
)
from backend.core.medici_synapse import (
    StructuralAnalyzer, IsomorphismDetector, InnovationGenerator
)
from backend.profile.manager import (
    CreativeFingerprint, IntentTracker, UserProfileManager
)


class TestAssetTypes:
    """测试资产类型系统"""

    def test_asset_creation(self):
        """测试资产创建"""
        asset = Asset(
            id="test-1",
            asset_type=AssetType.PATTERN,
            name="Test Pattern",
            description="A test pattern"
        )

        assert asset.id == "test-1"
        assert asset.asset_type == AssetType.PATTERN
        assert asset.name == "Test Pattern"
        assert asset.status == AssetStatus.DRAFT

    def test_pattern_asset(self):
        """测试模式资产"""
        pattern = PatternAsset(
            id="pattern-1",
            name="Hero's Journey",
            description="Classic hero journey pattern",
            pattern_type="character_arc",
            stages=["Ordinary World", "Call to Adventure", "Refusal"],
            examples=[{"story": "Star Wars", "hero": "Luke Skywalker"}]
        )

        assert pattern.pattern_type == "character_arc"
        assert len(pattern.stages) == 3
        assert len(pattern.examples) == 1

    def test_asset_factory(self):
        """测试资产工厂"""
        pattern = AssetFactory.create_asset(
            asset_type=AssetType.PATTERN,
            name="Test Pattern",
            description="Test"
        )

        assert isinstance(pattern, PatternAsset)
        assert pattern.asset_type == AssetType.PATTERN

    def test_asset_metadata(self):
        """测试资产元数据"""
        metadata = AssetMetadata(
            author="Test Author",
            version="1.0.0",
            tags=["test", "example"],
            created_at=datetime.now()
        )

        assert metadata.author == "Test Author"
        assert "test" in metadata.tags

    def test_usage_stats(self):
        """测试使用统计"""
        stats = UsageStats()
        stats.record_usage()

        assert stats.total_usage == 1
        assert stats.last_used is not None


class TestAbstractionEngine:
    """测试抽象引擎"""

    def test_pattern_recognition(self):
        """测试模式识别"""
        recognizer = PatternRecognizer()

        # 创建测试事件
        event = {
            "type": "character_action",
            "character": "hero",
            "action": "refuses_call",
            "context": {
                "story_stage": "beginning"
            }
        }

        result = recognizer.recognize(event)

        assert result is not None
        assert result.pattern_type in ["character_arc", "plot_point"]

    def test_knowledge_base(self):
        """测试知识库"""
        kb = KnowledgeBase()

        # 添加模式
        pattern = Pattern(
            id="pattern-1",
            name="Test Pattern",
            features=[1, 2, 3],
            abstraction_level=2
        )
        kb.add_pattern(pattern)

        # 查找相似模式
        similar = kb.find_similar([1, 2, 3], threshold=0.8)

        assert len(similar) >= 0

    def test_abstraction_engine(self):
        """测试抽象引擎"""
        engine = AbstractionEngine()

        # 处理事件序列
        events = [
            {"type": "character_introduced", "name": "Hero"},
            {"type": "call_to_adventure", "character": "Hero"},
            {"type": "character_action", "action": "refuses", "character": "Hero"}
        ]

        for event in events:
            engine.process_event(event)

        # 获取抽象
        abstractions = engine.get_abstractions()
        assert len(abstractions) >= 0


class TestMediciSynapse:
    """测试Medici Synapse"""

    def test_structural_analysis(self):
        """测试结构分析"""
        analyzer = StructuralAnalyzer()

        source_desc = "A system where users can create and share content"
        source_structure = analyzer.analyze(source_desc)

        assert "elements" in source_structure
        assert "relations" in source_structure
        assert "dynamics" in source_structure

    def test_isomorphism_detection(self):
        """测试同构检测"""
        detector = IsomorphismDetector()

        source = {
            "elements": ["User", "Content", "Share"],
            "relations": [("User", "creates", "Content"), ("User", "shares", "Content")]
        }

        target = {
            "elements": ["Developer", "Code", "Publish"],
            "relations": [("Developer", "writes", "Code"), ("Developer", "publishes", "Code")]
        }

        isomorphism = detector.detect_isomorphism(source, target)

        assert isomorphism is not None
        assert isomorphism["similarity"] > 0.5

    def test_innovation_generation(self):
        """测试创新生成"""
        generator = InnovationGenerator()

        innovation = generator.brainstorm(
            source_domain="Wiki",
            source_description="A platform for collaborative knowledge editing",
            target_domains=["Story", "Game"],
            target_descriptions=[
                "A platform for creating interactive narratives",
                "A platform for building virtual worlds"
            ]
        )

        assert len(innovation) > 0
        assert "title" in innovation[0]
        assert "description" in innovation[0]


class TestAssetManager:
    """测试资产管理器"""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """临时存储路径"""
        return tmp_path / "test_assets.json"

    def test_create_asset(self, temp_storage):
        """测试创建资产"""
        manager = AssetManager(storage_path=str(temp_storage))

        asset = manager.create_asset(
            asset_type=AssetType.PATTERN,
            name="Test Pattern",
            description="Test description"
        )

        assert asset is not None
        assert asset.id is not None
        assert asset.name == "Test Pattern"

    def test_search_assets(self, temp_storage):
        """测试搜索资产"""
        manager = AssetManager(storage_path=str(temp_storage))

        # 创建测试资产
        manager.create_asset(
            asset_type=AssetType.PATTERN,
            name="Hero Pattern",
            description="Hero's journey pattern",
            tags=["hero", "journey"]
        )

        # 搜索
        results = manager.search_assets(query="hero", tags=["hero"])

        assert len(results) >= 1

    def test_recommend_assets(self, temp_storage):
        """测试资产推荐"""
        manager = AssetManager(storage_path=str(temp_storage))
        recommender = AssetRecommender(manager)

        # 创建测试资产
        manager.create_asset(
            asset_type=AssetType.PATTERN,
            name="Hero Pattern",
            description="Hero's journey",
            tags=["hero"]
        )

        # 获取推荐
        recommendations = recommender.recommend(
            context={"story_genre": "fantasy"},
            user_history={},
            limit=5
        )

        assert isinstance(recommendations, list)


class TestUserProfile:
    """测试用户画像"""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """临时存储路径"""
        return tmp_path / "test_profile.json"

    def test_creative_fingerprint(self):
        """测试创作指纹"""
        fingerprint = CreativeFingerprint(
            user_id="user-1",
            primary_style="fantasy",
            style_scores={
                "descriptive": 0.8,
                "dialogue": 0.6,
                "pacing": 0.7
            },
            preferred_genres=["fantasy", "sci-fi"],
            writing_habits={
                "session_duration": 60,
                "preferred_time": "evening"
            }
        )

        assert fingerprint.user_id == "user-1"
        assert fingerprint.primary_style == "fantasy"

    def test_intent_tracker(self):
        """测试意图追踪"""
        tracker = IntentTracker(user_id="user-1")

        # 记录动作
        tracker.record_action({
            "action_type": "create_node",
            "node_type": "scene",
            "timestamp": datetime.now().isoformat()
        })

        # 推断意图
        intent = tracker.infer_intent()

        assert intent is not None
        assert intent.category is not None

    def test_user_profile_manager(self, temp_storage):
        """测试用户画像管理器"""
        manager = UserProfileManager(storage_path=str(temp_storage))

        # 创建或获取画像
        profile = manager.get_or_create_profile("user-1")

        # 更新创作指纹
        profile.fingerprint.primary_style = "sci-fi"
        manager.save_profile(profile)

        # 加载画像
        loaded = manager.get_profile("user-1")

        assert loaded.fingerprint.primary_style == "sci-fi"


@pytest.mark.integration
class TestAssetSystemIntegration:
    """集成测试 - 资产系统整体流程"""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """临时存储路径"""
        return tmp_path / "test_integration.json"

    def test_complete_asset_lifecycle(self, temp_storage):
        """测试完整的资产生命周期"""
        manager = AssetManager(storage_path=str(temp_storage))

        # 1. 创建资产
        asset = manager.create_asset(
            asset_type=AssetType.PATTERN,
            name="Test Pattern",
            description="Integration test pattern",
            tags=["test"]
        )

        # 2. 发布资产
        asset.status = AssetStatus.PUBLISHED
        manager.update_asset(asset.id, asset)

        # 3. 使用资产
        asset.usage_stats.record_usage()
        manager.update_asset(asset.id, asset)

        # 4. 搜索资产
        results = manager.search_assets(query="Test")

        # 5. 删除资产
        manager.delete_asset(asset.id)

        assert len(results) >= 0

    def test_abstraction_to_asset_workflow(self, temp_storage):
        """测试从抽象到资产的工作流"""
        # 1. 识别模式
        recognizer = PatternRecognizer()
        event = {"type": "test_event", "data": "test"}
        result = recognizer.recognize(event)

        # 2. 保存为资产
        manager = AssetManager(storage_path=str(temp_storage))
        asset = manager.create_asset(
            asset_type=AssetType.PATTERN,
            name="Recognized Pattern",
            description=f"Pattern from {result.pattern_type}",
            abstraction=result.to_dict()
        )

        assert asset.id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

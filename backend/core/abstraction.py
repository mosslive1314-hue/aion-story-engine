"""
Layer 4 - Abstraction Engine
抽象引擎：模式识别、知识存储和应用
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re
from collections import Counter

from .asset_types import Asset, PatternAsset, AssetType


@dataclass
class Pattern:
    """抽象模式"""
    id: str
    name: str
    pattern_type: str
    features: Dict[str, Any]  # 模式特征
    examples: List[Dict[str, Any]] = field(default_factory=list)
    usage_count: int = 0
    success_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count


@dataclass
class AbstractionResult:
    """抽象结果"""
    patterns: List[Pattern]
    confidence: float
    features: Dict[str, Any]
    source_event: Dict[str, Any]


class PatternRecognizer:
    """模式识别器"""

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.feature_extractors = {
            "character_arc": self._extract_character_arc_features,
            "plot_structure": self._extract_plot_structure_features,
            "dialogue_pattern": self._extract_dialogue_features,
            "conflict_type": self._extract_conflict_features,
        }

    def recognize(self, event: Dict[str, Any]) -> AbstractionResult:
        """从事件中识别模式"""
        results = []

        # 提取事件特征
        features = self._extract_features(event)

        # 匹配已知模式
        for pattern_id, pattern in self.patterns.items():
            similarity = self._calculate_similarity(features, pattern.features)
            if similarity > 0.7:  # 相似度阈值
                results.append(pattern)

        # 如果没有匹配的模式，创建新模式
        if not results:
            new_pattern = self._create_pattern_from_event(event, features)
            results.append(new_pattern)

        # 按相似度排序
        results.sort(key=lambda p: self._calculate_similarity(features, p.features), reverse=True)

        return AbstractionResult(
            patterns=results,
            confidence=min(0.95, 0.5 + len(results) * 0.1),
            features=features,
            source_event=event
        )

    def _extract_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取事件特征"""
        features = {
            "action_type": event.get("action", ""),
            "entities": event.get("entities", []),
            "context": event.get("context", {}),
            "outcome": event.get("outcome", ""),
        }

        # 提取特定类型的特征
        for pattern_type, extractor in self.feature_extractors.items():
            try:
                type_features = extractor(event)
                features[pattern_type] = type_features
            except:
                pass

        return features

    def _extract_character_arc_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取角色弧线特征"""
        return {
            "has_character": bool(event.get("character")),
            "has_change": "change" in str(event.get("outcome", "")).lower(),
            "emotional_impact": self._detect_emotion(event.get("narrative", "")),
        }

    def _extract_plot_structure_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取情节结构特征"""
        action = event.get("action", "").lower()

        return {
            "is_intro": any(word in action for word in ["开始", "介绍", "进入"]),
            "is_conflict": any(word in action for word in ["冲突", "战斗", "对抗"]),
            "is_climax": any(word in action for word in ["高潮", "决战", "最终"]),
            "is_resolution": any(word in action for word in ["解决", "结束", "完成"]),
        }

    def _extract_dialogue_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取对话模式特征"""
        narrative = event.get("narrative", "")
        return {
            "has_dialogue": '"' in narrative or '"' in narrative,
            "dialogue_count": narrative.count('"') // 2,
            "speaker_count": len(set(re.findall(r'["\`](.*?)["\`]', narrative))),
        }

    def _extract_conflict_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取冲突类型特征"""
        action = event.get("action", "").lower()
        return {
            "conflict_intensity": self._assess_conflict_intensity(action),
            "conflict_type": self._classify_conflict(action),
        }

    def _detect_emotion(self, text: str) -> str:
        """检测情感"""
        emotion_words = {
            "joy": ["开心", "快乐", "高兴", "喜悦", "幸福"],
            "sadness": ["悲伤", "难过", "痛苦", "伤心", "哀伤"],
            "anger": ["愤怒", "生气", "暴怒", "恼火", "愤慨"],
            "fear": ["恐惧", "害怕", "惊恐", "担心", "忧虑"],
        }

        max_count = 0
        detected_emotion = "neutral"

        for emotion, words in emotion_words.items():
            count = sum(1 for word in words if word in text)
            if count > max_count:
                max_count = count
                detected_emotion = emotion

        return detected_emotion

    def _assess_conflict_intensity(self, action: str) -> float:
        """评估冲突强度"""
        intensity_keywords = {
            "high": ["决战", "毁灭", "死亡", "终极"],
            "medium": ["战斗", "冲突", "对抗", "竞争"],
            "low": ["分歧", "争论", "不同", "异议"],
        }

        for intensity, keywords in intensity_keywords.items():
            if any(keyword in action for keyword in keywords):
                return {"high": 0.9, "medium": 0.6, "low": 0.3}[intensity]

        return 0.1

    def _classify_conflict(self, action: str) -> str:
        """分类冲突类型"""
        if any(word in action for word in ["战斗", "打", "攻击"]):
            return "physical"
        elif any(word in action for word in ["争论", "辩论", "说服"]):
            return "verbal"
        elif any(word in action for word in ["内心", "挣扎", "选择"]):
            return "internal"
        else:
            return "other"

    def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """计算特征相似度"""
        # 简化实现：计算共同特征的比例
        keys1 = set(features1.keys())
        keys2 = set(features2.keys())

        common_keys = keys1 & keys2
        total_keys = keys1 | keys2

        if not total_keys:
            return 0.0

        return len(common_keys) / len(total_keys)

    def _create_pattern_from_event(self, event: Dict[str, Any], features: Dict[str, Any]) -> Pattern:
        """从事件创建新模式"""
        pattern_id = f"pattern_{datetime.now().timestamp()}"

        # 确定模式类型
        pattern_type = "general"
        for key in features.keys():
            if key in self.feature_extractors:
                pattern_type = key
                break

        pattern = Pattern(
            id=pattern_id,
            name=f"Auto-generated {pattern_type}",
            pattern_type=pattern_type,
            features=features,
            examples=[event]
        )

        self.patterns[pattern_id] = pattern
        return pattern

    def add_pattern(self, pattern: Pattern):
        """添加模式"""
        self.patterns[pattern.id] = pattern

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """获取模式"""
        return self.patterns.get(pattern_id)

    def get_patterns_by_type(self, pattern_type: str) -> List[Pattern]:
        """按类型获取模式"""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.pattern_type == pattern_type
        ]

    def update_pattern_stats(self, pattern_id: str, success: bool):
        """更新模式统计"""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.usage_count += 1
            if success:
                pattern.success_count += 1


class KnowledgeBase:
    """知识库：存储和管理模式"""

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.assets: Dict[str, Asset] = {}
        self.pattern_relations: Dict[str, List[str]] = {}  # 模式关系

    def store_pattern(self, pattern: Pattern):
        """存储模式"""
        self.patterns[pattern.id] = pattern

    def store_asset(self, asset: Asset):
        """存储资产"""
        self.assets[asset.id] = asset

    def find_similar_patterns(
        self,
        features: Dict[str, Any],
        threshold: float = 0.6,
        limit: int = 5
    ) -> List[Pattern]:
        """查找相似模式"""
        similarities = []

        for pattern in self.patterns.values():
            similarity = self._calculate_similarity(features, pattern.features)
            if similarity >= threshold:
                similarities.append((pattern, similarity))

        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        return [pattern for pattern, _ in similarities[:limit]]

    def _calculate_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """计算相似度"""
        keys1 = set(str(k) for k in features1.keys())
        keys2 = set(str(k) for k in features2.keys())

        if not keys1 or not keys2:
            return 0.0

        intersection = keys1 & keys2
        union = keys1 | keys2

        return len(intersection) / len(union) if union else 0.0

    def relate_patterns(self, pattern1_id: str, pattern2_id: str):
        """关联两个模式"""
        if pattern1_id not in self.pattern_relations:
            self.pattern_relations[pattern1_id] = []
        if pattern2_id not in self.pattern_relations:
            self.pattern_relations[pattern2_id] = []

        if pattern2_id not in self.pattern_relations[pattern1_id]:
            self.pattern_relations[pattern1_id].append(pattern2_id)
        if pattern1_id not in self.pattern_relations[pattern2_id]:
            self.pattern_relations[pattern2_id].append(pattern1_id)

    def get_pattern_relations(self, pattern_id: str) -> List[Pattern]:
        """获取相关模式"""
        related_ids = self.pattern_relations.get(pattern_id, [])
        return [
            self.patterns[pid]
            for pid in related_ids
            if pid in self.patterns
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计"""
        pattern_types = Counter(p.pattern_type for p in self.patterns.values())

        return {
            "total_patterns": len(self.patterns),
            "total_assets": len(self.assets),
            "pattern_types": dict(pattern_types),
            "total_relations": sum(len(rels) for rels in self.pattern_relations.values()),
        }


class AbstractionEngine:
    """抽象引擎：Layer 4 核心引擎"""

    def __init__(self):
        self.recognizer = PatternRecognizer()
        self.knowledge_base = KnowledgeBase()

    def process_event(self, event: Dict[str, Any]) -> AbstractionResult:
        """处理事件，提取抽象"""
        # 识别模式
        result = self.recognizer.recognize(event)

        # 存储新模式到知识库
        for pattern in result.patterns:
            if pattern.id not in self.knowledge_base.patterns:
                self.knowledge_base.store_pattern(pattern)

        return result

    def suggest_patterns(
        self,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[Pattern]:
        """基于上下文推荐模式"""
        # 从上下文中提取特征
        features = self.recognizer._extract_features(context)

        # 查找相似模式
        similar_patterns = self.knowledge_base.find_similar_patterns(
            features,
            threshold=0.4,
            limit=limit
        )

        return similar_patterns

    def apply_pattern(
        self,
        pattern_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用模式到上下文"""
        pattern = self.knowledge_base.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_id}")

        # 更新使用统计
        self.recognizer.update_pattern_stats(pattern_id, success=True)

        # 生成应用结果
        return {
            "pattern": pattern.name,
            "type": pattern.pattern_type,
            "features": pattern.features,
            "context": context,
            "suggestions": self._generate_suggestions(pattern, context)
        }

    def _generate_suggestions(
        self,
        pattern: Pattern,
        context: Dict[str, Any]
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        # 基于模式类型生成建议
        if pattern.pattern_type == "character_arc":
            suggestions = [
                "考虑角色的成长弧线",
                "设置角色面临的挑战",
                "安排角色的转变时刻"
            ]
        elif pattern.pattern_type == "plot_structure":
            suggestions = [
                "确保铺垫充分",
                "冲突要逐步升级",
                "高潮要具有冲击力",
                "结局要符合逻辑"
            ]
        elif pattern.pattern_type == "dialogue_pattern":
            suggestions = [
                "对话要符合角色性格",
                "保持对话的自然流畅",
                "通过对话推动情节"
            ]

        return suggestions

    def learn_from_feedback(
        self,
        pattern_id: str,
        success: bool,
        feedback: Optional[str] = None
    ):
        """从反馈中学习"""
        self.recognizer.update_pattern_stats(pattern_id, success)

    def get_engine_stats(self) -> Dict[str, Any]:
        """获取引擎统计"""
        kb_stats = self.knowledge_base.get_statistics()

        return {
            "knowledge_base": kb_stats,
            "recognizer": {
                "total_patterns": len(self.recognizer.patterns),
                "pattern_types": dict(
                    Counter(p.pattern_type for p in self.recognizer.patterns.values())
                )
            }
        }


# 全局引擎实例
_abstraction_engine: Optional[AbstractionEngine] = None


def get_abstraction_engine() -> AbstractionEngine:
    """获取抽象引擎单例"""
    global _abstraction_engine
    if _abstraction_engine is None:
        _abstraction_engine = AbstractionEngine()
    return _abstraction_engine

"""
Intent Inference Engine - 意图推断引擎
理解用户的模糊输入和深层意图
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import Counter


class IntentCategory(Enum):
    """意图类别"""
    CREATION = "creation"  # 创作意图
    EDITING = "editing"  # 编辑意图
    NAVIGATION = "navigation"  # 导航意图
    INFORMATION = "information"  # 信息查询
    SOCIAL = "social"  # 社交意图
    EXPLORATION = "exploration"  # 探索意图
    ORGANIZATION = "organization"  # 组织意图
    EXPORT = "export"  # 导出意图


class ConfidenceLevel(Enum):
    """置信度级别"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class InferredIntent:
    """推断出的意图"""
    category: IntentCategory
    action: str  # 具体动作
    parameters: Dict[str, Any]  # 参数
    confidence: float  # 置信度 0-1
    context: Dict[str, Any] = field(default_factory=dict)
    alternative_intents: List['InferredIntent'] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "category": self.category.value,
            "action": self.action,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "context": self.context,
            "alternatives": [
                {
                    "category": alt.category.value,
                    "action": alt.action,
                    "confidence": alt.confidence
                }
                for alt in self.alternative_intents
            ],
            "timestamp": self.timestamp.isoformat()
        }


class NLPUnderstander:
    """自然语言理解器"""

    def __init__(self):
        # 动作关键词映射
        self.action_keywords = {
            # 创作类
            "create": ["创建", "新建", "添加", "写", "生成", "创作"],
            "edit": ["编辑", "修改", "改", "更新", "优化", "润色"],
            "delete": ["删除", "移除", "去掉", "清除"],

            # 导航类
            "open": ["打开", "进入", "查看", "显示"],
            "close": ["关闭", "退出", "隐藏"],
            "go_to": ["跳到", "前往", "定位"],

            # 信息类
            "search": ["搜索", "查找", "找", "检索"],
            "list": ["列出", "显示所有", "看看"],

            # 导出类
            "export": ["导出", "保存", "下载", "输出"],
            "share": ["分享", "发布", "公开"],

            # 探索类
            "explore": ["探索", "看看", "浏览", "发现"],
            "suggest": ["建议", "推荐", "启发"],
        }

        # 实体关键词
        self.entity_keywords = {
            "story": ["故事", "小说", "文章", "内容"],
            "chapter": ["章节", "部分", "幕"],
            "scene": ["场景", "情节", "片段"],
            "character": ["角色", "人物", "NPC", "主角"],
            "location": ["地点", "场所", "场景"],
            "asset": ["资产", "模板", "素材"],
            "setting": ["设置", "配置", "选项"],
        }

    def parse(self, text: str) -> Dict[str, Any]:
        """解析文本"""
        result = {
            "actions": [],
            "entities": [],
            "modifiers": [],
            "questions": False,  # 是否是问句
            "imperative": False,  # 是否是祈使句
            "sentiment": "neutral"
        }

        # 检查是否是问句
        result["questions"] = "?" in text or "吗" in text or "如何" in text or "怎么" in text

        # 检查是否是祈使句
        result["imperative"] = any(text.startswith(m) for m in ["请", "帮我", "能不能", "可以"])

        # 提取动作
        for action, keywords in self.action_keywords.items():
            if any(keyword in text for keyword in keywords):
                result["actions"].append(action)
                break

        # 提取实体
        for entity, keywords in self.entity_keywords.items():
            if any(keyword in text for keyword in keywords):
                result["entities"].append(entity)

        # 情感分析（简化）
        positive_words = ["好", "棒", "优秀", "喜欢", "爱"]
        negative_words = ["差", "坏", "讨厌", "不好", "糟糕"]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            result["sentiment"] = "positive"
        elif negative_count > positive_count:
            result["sentiment"] = "negative"

        return result


class BehaviorAnalyzer:
    """行为分析器"""

    def __init__(self):
        self.action_patterns = {
            "creation": ["create_node", "write_content", "add_asset"],
            "editing": ["edit_node", "update_content", "modify_asset"],
            "navigation": ["navigate", "open_story", "switch_view"],
            "search": ["search", "filter", "query"],
            "organization": ["organize", "categorize", "tag"],
            "export": ["export", "save", "download"],
            "exploration": ["browse", "suggest", "recommend"],
        }

    def analyze_sequence(
        self,
        actions: List[Dict[str, Any]],
        window_size: int = 5
    ) -> Dict[str, Any]:
        """分析行为序列"""
        if not actions:
            return {"pattern": "unknown", "confidence": 0.0}

        # 获取最近的操作
        recent = actions[-window_size:]

        # 统计动作类型
        action_counts = Counter(
            self._classify_action(action)
            for action in recent
        )

        # 判断主导模式
        if action_counts:
            dominant = action_counts.most_common(1)[0]
            count = action_counts[dominant]
            confidence = min(1.0, count / len(recent))

            return {
                "pattern": dominant,
                "confidence": confidence,
                "action_counts": dict(action_counts),
                "sequence_length": len(recent)
            }

        return {"pattern": "unknown", "confidence": 0.0}

    def _classify_action(self, action: Dict[str, Any]) -> str:
        """分类单个动作"""
        action_type = action.get("action_type", "")
        action_name = action.get("action", "")

        # 精确匹配
        if action_type in self.action_patterns:
            return action_type

        # 模糊匹配
        for pattern, keywords in self.action_patterns.items():
            if any(keyword in action_name for keyword in keywords):
                return pattern

        return "unknown"

    def detect_transition(self, actions: List[Dict[str, Any]]) -> Optional[str]:
        """检测模式转换"""
        if len(actions) < 2:
            return None

        recent = actions[-3:]
        patterns = [self._classify_action(a) for a in recent]

        # 检测转换
        if len(set(patterns)) > 1:
            # 如果最后一个模式与之前不同
            if patterns[-1] != patterns[-2]:
                return f"{patterns[-2]} → {patterns[-1]}"

        return None


class ContextAnalyzer:
    """上下文分析器"""

    def __init__(self):
        pass

    def analyze(
        self,
        current_context: Dict[str, Any],
        user_input: str,
        parsed_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析上下文"""
        analysis = {
            "has_selection": bool(current_context.get("selection")),
            "current_location": current_context.get("location", "unknown"),
            "active_story": current_context.get("story_id"),
            "active_node": current_context.get("node_id"),
            "recent_actions": current_context.get("recent_actions", []),
        }

        # 分析输入与上下文的关系
        if analysis["has_selection"]:
            analysis["intent_focus"] = "selection"
        elif analysis["active_node"]:
            analysis["intent_focus"] = "current_node"
        elif analysis["active_story"]:
            analysis["intent_focus"] = "story"

        # 时间分析
        if "timestamp" in current_context:
            current_time = datetime.fromisoformat(current_context["timestamp"])
            analysis["time_of_day"] = self._get_time_of_day(current_time)

        return analysis

    def _get_time_of_day(self, dt: datetime) -> str:
        """获取时间段"""
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"


class IntentInferenceEngine:
    """意图推断引擎主类"""

    def __init__(self):
        self.nlp = NLPUnderstander()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.context_analyzer = ContextAnalyzer()

        # 意图历史
        self.intent_history: List[InferredIntent] = []

    def infer(
        self,
        user_input: str,
        context: Dict[str, Any],
        behavior_history: List[Dict[str, Any]] = None
    ) -> InferredIntent:
        """推断用户意图"""
        # 1. NLP 解析
        parsed = self.nlp.parse(user_input)

        # 2. 上下文分析
        context_analysis = self.context_analyzer.analyze(context, user_input, parsed)

        # 3. 行为序列分析
        behavior_analysis = {}
        if behavior_history:
            behavior_analysis = self.behavior_analyzer.analyze_sequence(behavior_history)

        # 4. 综合推断
        intent = self._synthesize_intent(
            parsed,
            context_analysis,
            behavior_analysis
        )

        # 5. 生成备选意图
        alternatives = self._generate_alternatives(intent, parsed)

        # 6. 计算置信度
        confidence = self._calculate_confidence(intent, parsed, context_analysis)

        inferred_intent = InferredIntent(
            category=intent["category"],
            action=intent["action"],
            parameters=intent["parameters"],
            confidence=confidence,
            context={
                "parsed": parsed,
                "context_analysis": context_analysis,
                "behavior_analysis": behavior_analysis
            },
            alternative_intents=alternatives
        )

        # 保存到历史
        self.intent_history.append(inferred_intent)

        return inferred_intent

    def _synthesize_intent(
        self,
        parsed: Dict[str, Any],
        context_analysis: Dict[str, Any],
        behavior_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合推断意图"""
        # 基于动作关键词
        action_map = {
            "create": (IntentCategory.CREATION, "create_content"),
            "edit": (IntentCategory.EDITING, "edit_content"),
            "delete": (IntentCategory.EDITING, "delete_content"),
            "search": (IntentCategory.INFORMATION, "search"),
            "open": (IntentCategory.NAVIGATION, "open_item"),
            "export": (IntentCategory.EXPORT, "export_content"),
            "suggest": (IntentCategory.EXPLORATION, "get_suggestions"),
        }

        # 确定动作
        if parsed["actions"]:
            primary_action = parsed["actions"][0]
        elif parsed["questions"]:
            primary_action = "search"
        else:
            primary_action = "explore"

        # 确定类别
        if primary_action in action_map:
            category, action = action_map[primary_action]
        else:
            category = IntentCategory.EXPLORATION
            action = "explore"

        # 提取参数
        parameters = {}
        if parsed["entities"]:
            parameters["entity_type"] = parsed["entities"][0]

        if context_analysis.get("active_story"):
            parameters["story_id"] = context_analysis["active_story"]

        if context_analysis.get("active_node"):
            parameters["node_id"] = context_analysis["active_node"]

        return {
            "category": category,
            "action": action,
            "parameters": parameters
        }

    def _generate_alternatives(
        self,
        primary_intent: Dict[str, Any],
        parsed: Dict[str, Any]
    ) -> List['InferredIntent']:
        """生成备选意图"""
        alternatives = []

        # 如果主意图是创作，备选可能是编辑
        if primary_intent["category"] == IntentCategory.CREATION:
            alternatives.append(InferredIntent(
                category=IntentCategory.EDITING,
                action="edit_content",
                parameters={},
                confidence=0.3
            ))

        # 如果主意图是搜索，备选可能是导航
        if primary_intent["category"] == IntentCategory.INFORMATION:
            alternatives.append(InferredIntent(
                category=IntentCategory.NAVIGATION,
                action="navigate_to",
                parameters={},
                confidence=0.4
            ))

        return alternatives

    def _calculate_confidence(
        self,
        intent: Dict[str, Any],
        parsed: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度

        # 基于动作关键词
        if parsed["actions"]:
            confidence += 0.2

        # 基于实体识别
        if parsed["entities"]:
            confidence += 0.1

        # 基于上下文匹配度
        if "active_node" in context and context["active_node"]:
            confidence += 0.1

        # 基于行为模式
        if "behavior_analysis" in context:
            behavior = context["behavior_analysis"]
            if behavior.get("confidence", 0) > 0.7:
                confidence += 0.1

        return min(1.0, confidence)

    def validate_intent(
        self,
        intent: InferredIntent,
        user_feedback: bool
    ):
        """根据反馈验证意图"""
        if user_feedback:
            # 提高该类别的权重
            pass
        else:
            # 降低权重
            pass

        intent.confidence = max(0.1, min(1.0, intent.confidence + (0.1 if user_feedback else -0.1)))

    def get_intent_stats(self) -> Dict[str, Any]:
        """获取意图统计"""
        if not self.intent_history:
            return {"total": 0}

        category_counts = Counter(intent.category for intent in self.intent_history)
        avg_confidence = sum(intent.confidence for intent in self.intent_history) / len(self.intent_history)

        return {
            "total_intents": len(self.intent_history),
            "category_distribution": dict(category_counts),
            "average_confidence": round(avg_confidence, 2),
        }


# 全局意图引擎实例
_intent_engine: Optional[IntentInferenceEngine] = None


def get_intent_engine() -> IntentInferenceEngine:
    """获取意图引擎单例"""
    global _intent_engine
    if _intent_engine is None:
        _intent_engine = IntentInferenceEngine()
    return _intent_engine

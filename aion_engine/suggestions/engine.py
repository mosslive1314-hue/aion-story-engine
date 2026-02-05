from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Suggestion:
    """A smart suggestion for the user"""
    type: str
    title: str
    description: str
    confidence: float
    reasoning: str
    action: Optional[str] = None
    asset_id: Optional[str] = None


class SuggestionsEngine:
    """Context-aware intelligent suggestions"""

    def __init__(self, memory_graph=None, user_profile=None):
        self.memory_graph = memory_graph
        self.user_profile = user_profile
        self.suggestion_history: List[Suggestion] = []

    def generate_suggestions(
        self,
        context: Dict[str, Any],
        user_state: Dict[str, Any],
        limit: int = 5,
    ) -> List[Suggestion]:
        """Generate contextual suggestions"""
        suggestions = []

        # Detect stuck points
        stuck_suggestion = self._detect_stuck_point(context, user_state)
        if stuck_suggestion:
            suggestions.append(stuck_suggestion)

        # Asset-based suggestions
        asset_suggestions = self._suggest_assets(context)
        suggestions.extend(asset_suggestions)

        # Skill gap suggestions
        skill_suggestions = self._suggest_skill_gaps(user_state)
        suggestions.extend(skill_suggestions)

        # Memory-based suggestions
        memory_suggestions = self._suggest_from_memory(context)
        suggestions.extend(memory_suggestions)

        # Sort by confidence
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return suggestions[:limit]

    def _detect_stuck_point(
        self, context: Dict[str, Any], user_state: Dict[str, Any]
    ) -> Optional[Suggestion]:
        """Detect when user is stuck"""
        # Check if no progress for too long
        if user_state.get("idle_time", 0) > 300:  # 5 minutes
            return Suggestion(
                type="help",
                title="卡住了？试试这个",
                description="看起来你已经思考了一段时间。需要一些灵感吗？",
                confidence=0.9,
                reasoning="用户空闲时间过长",
                action="provide_inspiration",
            )

        # Check if trying the same thing repeatedly
        if user_state.get("repeated_actions", 0) > 5:
            return Suggestion(
                type="strategy",
                title="换个思路",
                description="你试了同样的方法很多次。试试不同的方法吧！",
                confidence=0.85,
                reasoning="重复动作检测",
                action="suggest_alternative",
            )

        return None

    def _suggest_assets(self, context: Dict[str, Any]) -> List[Suggestion]:
        """Suggest relevant assets based on context"""
        suggestions = []

        # Fire scenario
        if context.get("fire_active"):
            suggestions.append(
                Suggestion(
                    type="asset",
                    title="火物理规则",
                    description="应用热力学规则让火灾更真实",
                    confidence=0.92,
                    reasoning="当前场景有火灾",
                    asset_id="fire-physics-rule",
                )
            )

        # NPC issue
        if context.get("npc_issue"):
            suggestions.append(
                Suggestion(
                    type="asset",
                    title="NPC 行为模板",
                    description="使用认知引擎规则改进 NPC 行为",
                    confidence=0.88,
                    reasoning="检测到 NPC 问题",
                    asset_id="npc-behavior-template",
                )
            )

        return suggestions

    def _suggest_skill_gaps(self, user_state: Dict[str, Any]) -> List[Suggestion]:
        """Suggest skill improvements"""
        suggestions = []

        # Low physics realism
        if user_state.get("physics_realism", 1.0) < 0.6:
            suggestions.append(
                Suggestion(
                    type="learning",
                    title="提升物理真实性",
                    description="你的强项是物理，可以增加更多物理约束",
                    confidence=0.83,
                    reasoning="物理真实性评分较低",
                    action="apply_physics_rules",
                )
            )

        # New to story branching
        if user_state.get("story_branching_skill", 1.0) < 0.5:
            suggestions.append(
                Suggestion(
                    type="learning",
                    title="学习分支叙事",
                    description="尝试创建分支情节，让故事更丰富",
                    confidence=0.78,
                    reasoning="分支叙事技能较低",
                    action="try_branching",
                )
            )

        return suggestions

    def _suggest_from_memory(self, context: Dict[str, Any]) -> List[Suggestion]:
        """Suggest based on memory graph"""
        suggestions = []

        if not self.memory_graph:
            return suggestions

        # Get top concepts
        top_concepts = self.memory_graph.get_top_concepts(limit=3)

        for concept_name, concept in top_concepts:
            if concept.satisfaction > 4.0:  # High satisfaction
                suggestions.append(
                    Suggestion(
                        type="memory",
                        title=f"再次使用 '{concept_name}'",
                        description=f"你在 '{concept_name}' 上很成功，再试试？",
                        confidence=0.8,
                        reasoning=f"高满意度概念: {concept_name}",
                        asset_id=None,
                    )
                )

        return suggestions

    def get_breakthrough_suggestion(
        self, user_state: Dict[str, Any]
    ) -> Optional[Suggestion]:
        """Detect breakthrough moments and suggest next steps"""
        # Check if user just achieved something
        if user_state.get("just_achieved"):
            return Suggestion(
                type="breakthrough",
                title="突破！继续前进",
                description="你刚完成了一个突破！试试更高级的概念。",
                confidence=0.95,
                reasoning="刚完成突破检测",
                action="advance_skill",
            )

        # Check for skill plateau
        skill_growth = user_state.get("skill_growth_rate", 0.0)
        if skill_growth < 0.1 and user_state.get("time_since_improvement", 0) > 600:
            return Suggestion(
                type="breakthrough",
                title="寻找新灵感",
                description="技能提升缓慢，试试 Medice Synapse 创新引擎？",
                confidence=0.87,
                reasoning="技能增长停滞",
                action="try_innovation",
            )

        return None

    def record_feedback(
        self, suggestion: Suggestion, helpful: bool, feedback: str = ""
    ):
        """Record user feedback on suggestions"""
        # Update suggestion confidence based on feedback
        if helpful:
            suggestion.confidence = min(0.99, suggestion.confidence + 0.05)
        else:
            suggestion.confidence = max(0.1, suggestion.confidence - 0.1)

        # Store in history
        self.suggestion_history.append(suggestion)

    def get_statistics(self) -> Dict[str, Any]:
        """Get suggestion engine statistics"""
        return {
            "total_suggestions": len(self.suggestion_history),
            "avg_confidence": (
                sum(s.confidence for s in self.suggestion_history)
                / len(self.suggestion_history)
                if self.suggestion_history
                else 0.0
            ),
            "suggestion_types": {
                s.type: sum(1 for x in self.suggestion_history if x.type == s.type)
                for s in self.suggestion_history
            },
        }

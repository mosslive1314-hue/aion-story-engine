from typing import Dict, List, Any, Optional
import re
from collections import defaultdict


class IntentEngine:
    """Infer user intentions from vague inputs"""

    def __init__(self):
        # Intent patterns
        self.patterns = {
            "fire_scenario": ["火", "燃烧", "火灾", "点燃烧", "实验室起火"],
            "npc_issue": ["NPC", "角色", "行为", "表现", "反应"],
            "story_branching": ["分叉", "分支", "多个结局", "选择"],
            "physics_rule": ["物理", "力学", "热力学", "能量"],
            "narrative": ["故事", "情节", "叙事", "描述"],
        }

        # Pattern memory for learning
        self.pattern_memory = defaultdict(list)

        # User corrections
        self.corrections = {}

    def infer_intent(self, vague_input: str) -> Dict[str, Any]:
        """Infer intent from vague user input"""
        input_lower = vague_input.lower()

        # Score each intent
        intent_scores = {}
        for intent, keywords in self.patterns.items():
            score = self._calculate_match_score(input_lower, keywords)
            if score > 0:
                intent_scores[intent] = score

        # Also check pattern memory
        for intent, patterns in self.pattern_memory.items():
            for pattern_info in patterns:
                if pattern_info["pattern"].lower() in input_lower:
                    intent_scores[intent] = intent_scores.get(intent, 0) + pattern_info["weight"]

        if not intent_scores:
            # No clear match, return default
            return {
                "intent": "unknown",
                "confidence": 0.3,
                "reasoning": "No clear pattern matched",
            }

        # Get best match
        best_intent = max(intent_scores.items(), key=lambda x: x[1])

        # Check for corrections
        if vague_input in self.corrections:
            corrected_intent = self.corrections[vague_input]
            # Boost confidence for corrected intents
            confidence = min(0.95, best_intent[1] + 0.2)
            return {
                "intent": corrected_intent,
                "confidence": confidence,
                "reasoning": f"Corrected pattern: {vague_input}",
            }

        return {
            "intent": best_intent[0],
            "confidence": min(0.95, best_intent[1]),
            "reasoning": f"Matched keywords for {best_intent[0]}",
        }

    def _calculate_match_score(self, input_text: str, keywords: List[str]) -> float:
        """Calculate match score for keywords"""
        score = 0.0
        matched_keywords = 0

        for keyword in keywords:
            if keyword.lower() in input_text:
                score += 1.0
                matched_keywords += 1

        if matched_keywords == 0:
            return 0.0

        # Single keyword match gets high confidence
        if matched_keywords == 1:
            score = 0.85
        else:
            # Multiple matches get even higher confidence
            score = min(0.95, 0.7 + (matched_keywords * 0.2))

        return score

    def add_pattern(self, pattern: str, intent: str, weight: float):
        """Add a pattern to memory"""
        self.pattern_memory[intent].append({"pattern": pattern, "weight": weight})

    def correct_intent(self, vague_input: str, correct_intent: str):
        """Learn from user corrections"""
        self.corrections[vague_input] = correct_intent

        # Also update patterns
        if correct_intent in self.patterns:
            # Extract keywords from the input
            keywords = self._extract_keywords(vague_input)
            self.patterns[correct_intent].extend(keywords)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from text"""
        # Simple keyword extraction
        keywords = []
        words = text.split()
        for word in words:
            if len(word) > 1:
                keywords.append(word)

        return keywords

    def get_top_intents(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get most likely intents based on history"""
        intent_counts = defaultdict(int)

        # Count from corrections
        for intent in self.corrections.values():
            intent_counts[intent] += 1

        # Sort by count
        sorted_intents = sorted(
            intent_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [{"intent": intent, "count": count} for intent, count in sorted_intents[:limit]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get intent engine statistics"""
        return {
            "total_patterns": sum(len(keywords) for keywords in self.patterns.values()),
            "total_corrections": len(self.corrections),
            "intent_distribution": {
                intent: len(keywords)
                for intent, keywords in self.patterns.items()
            },
        }

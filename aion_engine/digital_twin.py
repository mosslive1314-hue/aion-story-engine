from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .profile.fingerprint import UserProfile
from .intent.engine import IntentEngine
from .memory.graph import MemoryGraph
from .suggestions.engine import SuggestionsEngine


class DigitalTwin:
    """Unified digital twin interface"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile = UserProfile(user_id=user_id)
        self.intent_engine = IntentEngine()
        self.memory_graph = MemoryGraph()
        self.suggestions_engine = SuggestionsEngine(
            memory_graph=self.memory_graph, user_profile=self.profile
        )

    def process_user_input(self, vague_input: str) -> Dict[str, Any]:
        """Process vague user input and generate response"""
        # Infer intent
        intent_result = self.intent_engine.infer_intent(vague_input)

        # Update profile with inferred intent
        self.profile.record_intent(
            vague_input=vague_input,
            inferred_intent=intent_result["intent"],
            confidence=intent_result["confidence"],
        )

        # Update memory
        self._update_memory_from_input(vague_input, intent_result)

        # Generate suggestions
        context = self._build_context()
        user_state = self._build_user_state()
        suggestions = self.suggestions_engine.generate_suggestions(
            context, user_state, limit=3
        )

        return {
            "intent": intent_result,
            "suggestions": [asdict(s) for s in suggestions],
            "context": context,
            "profile_stats": {
                "genre_preferences": self.profile.creative_fingerprint.genre_preferences,
                "intent_history_count": len(self.profile.intent_history),
            },
        }

    def _update_memory_from_input(
        self, input_text: str, intent_result: Dict[str, Any]
    ):
        """Update memory graph from user input"""
        # Add concept if intent is clear
        if intent_result["confidence"] > 0.7:
            intent_name = intent_result["intent"]
            concept = self.memory_graph.get_concept(intent_name)
            if concept:
                self.memory_graph.update_usage(intent_name)
            else:
                self.memory_graph.add_concept(
                    name=intent_name,
                    related_assets=[],
                    initial_strength=1.0,
                )

    def _build_context(self) -> Dict[str, Any]:
        """Build current context for suggestions"""
        return {
            "user_id": self.user_id,
            "top_concepts": [
                concept_name for concept_name, _ in self.memory_graph.get_top_concepts(5)
            ],
        }

    def _build_user_state(self) -> Dict[str, Any]:
        """Build current user state"""
        return {
            "physics_realism": self.profile.creative_fingerprint.style_markers.get(
                "physics_realism", 0.5
            ),
            "story_branching_skill": 0.5,  # Simplified
            "idle_time": 0,  # Would track this externally
            "repeated_actions": 0,  # Would track this externally
        }

    def update_skill_rating(self, skill: str, rating: float):
        """Update skill rating in profile"""
        if skill in self.profile.satisfaction_scores:
            # Exponential moving average
            old = self.profile.satisfaction_scores[skill]
            self.profile.satisfaction_scores[skill] = 0.7 * old + 0.3 * rating
        else:
            self.profile.satisfaction_scores[skill] = rating

    def add_memory_concept(
        self, concept_name: str, related_assets: List[str] = None
    ):
        """Add concept to memory graph"""
        self.memory_graph.add_concept(
            name=concept_name, related_assets=related_assets or []
        )

    def get_digital_twin_stats(self) -> Dict[str, Any]:
        """Get comprehensive digital twin statistics"""
        return {
            "user_id": self.user_id,
            "profile_stats": {
                "genre_count": len(self.profile.creative_fingerprint.genre_preferences),
                "intent_history_count": len(self.profile.intent_history),
                "asset_usage_count": len(self.profile.asset_usage),
            },
            "memory_stats": self.memory_graph.get_statistics(),
            "intent_stats": self.intent_engine.get_statistics(),
            "suggestions_stats": self.suggestions_engine.get_statistics(),
        }

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CreativeFingerprint:
    """User's creative preferences and patterns"""
    genre_preferences: Dict[str, float] = field(default_factory=dict)
    style_markers: Dict[str, Any] = field(default_factory=dict)
    creation_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    creative_fingerprint: CreativeFingerprint = field(default_factory=CreativeFingerprint)
    intent_history: List[Dict[str, Any]] = field(default_factory=list)
    asset_usage: Dict[str, int] = field(default_factory=dict)
    satisfaction_scores: Dict[str, float] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def update_genre_preference(self, genre: str, weight: float):
        """Update genre preference"""
        if genre in self.creative_fingerprint.genre_preferences:
            # Update with exponential moving average
            old = self.creative_fingerprint.genre_preferences[genre]
            self.creative_fingerprint.genre_preferences[genre] = 0.7 * old + 0.3 * weight
        else:
            self.creative_fingerprint.genre_preferences[genre] = weight

    def record_intent(self, vague_input: str, inferred_intent: str, confidence: float):
        """Record user intent"""
        self.intent_history.append({
            "timestamp": datetime.now().isoformat(),
            "vague_input": vague_input,
            "inferred_intent": inferred_intent,
            "confidence": confidence,
        })

    def record_asset_usage(self, asset_id: str):
        """Record asset usage"""
        self.asset_usage[asset_id] = self.asset_usage.get(asset_id, 0) + 1

    def get_top_genres(self, n: int = 3) -> List[Tuple[str, float]]:
        """Get top N genres"""
        return sorted(
            self.creative_fingerprint.genre_preferences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

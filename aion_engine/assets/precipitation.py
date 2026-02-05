from typing import Dict, List, Any, Optional
from datetime import datetime

from ..assets.asset import Asset
from ..assets.asset_types import AssetType
from ..core.abstraction import AbstractionEngine


class AssetPrecipitation:
    """Automatic pattern detection and asset creation"""

    def __init__(self):
        self.engine = AbstractionEngine()

    def detect_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect reusable patterns from events"""
        patterns = self.engine.extract_patterns(events)

        suggestions = []
        for pattern in patterns:
            suggestions.append({
                "type": "pattern_detected",
                "name": pattern.name,
                "description": pattern.description,
                "confidence": 1.0,
                "suggested_asset": {
                    "asset_type": AssetType.PATTERN.value,
                    "name": pattern.name,
                    "description": pattern.description,
                    "content": {"pattern_events": pattern.events},
                    "tags": ["auto-detected", "pattern"],
                }
            })

        return suggestions

    def create_asset_from_pattern(
        self,
        pattern_name: str,
        pattern_description: str,
        events: List[Dict[str, Any]],
        user_id: str = "system",
    ) -> Asset:
        """Create an asset from a detected pattern"""
        import uuid

        asset = Asset(
            id=str(uuid.uuid4())[:8],
            asset_type=AssetType.PATTERN,
            name=pattern_name,
            description=pattern_description,
            content={"events": events, "source": "auto-detection"},
            metadata={
                "created_by": user_id,
                "auto_generated": True,
                "detection_timestamp": datetime.now().isoformat(),
            },
            tags=["auto-detected", "pattern"],
        )

        return asset

    def get_usage_suggestions(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions for asset usage based on context"""
        suggestions = []

        # Simple context-based suggestions
        if current_context.get("fire_active"):
            suggestions.append({
                "type": "asset_recommendation",
                "asset_type": AssetType.WORLD_RULE.value,
                "description": "Fire physics rules might be relevant",
                "confidence": 0.8,
            })

        return suggestions

from typing import Dict, List, Any, Optional
from ..assets.asset import Asset
from ..assets.asset_types import AssetType
from ..profile.fingerprint import UserProfile


class RecommendationEngine:
    """Intelligent asset recommendation system"""

    def __init__(self, asset_manager):
        self.asset_manager = asset_manager

    def recommend_assets(
        self,
        user_profile: Optional[UserProfile] = None,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Recommend assets based on user profile and context"""
        recommendations = []

        # Get all assets
        all_assets = self.asset_manager.get_all_assets()

        for asset in all_assets:
            score = self._calculate_relevance_score(asset, user_profile, context)
            if score > 0.3:  # Minimum threshold
                recommendations.append({
                    "asset": asset,
                    "score": score,
                    "reasons": self._get_recommendation_reasons(asset, user_profile, context),
                })

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return recommendations[:limit]

    def _calculate_relevance_score(
        self,
        asset: Asset,
        user_profile: Optional[UserProfile],
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate relevance score for an asset"""
        score = 0.0

        # Base score from usage and rating
        score += min(asset.usage_count / 10.0, 0.5)  # Usage weight
        score += asset.rating / 5.0 * 0.3  # Rating weight

        # Context-based scoring
        if context:
            if context.get("fire_active") and "fire" in asset.name.lower():
                score += 0.4

            if context.get("genre") and context["genre"] in asset.tags:
                score += 0.3

        # User preference-based scoring
        if user_profile:
            # Check if asset type matches user preferences
            if asset.asset_type.value in user_profile.asset_usage:
                usage = user_profile.asset_usage[asset.asset_type.value]
                score += min(usage / 20.0, 0.2)

        return min(score, 1.0)

    def _get_recommendation_reasons(
        self,
        asset: Asset,
        user_profile: Optional[UserProfile],
        context: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Get reasons why asset was recommended"""
        reasons = []

        if asset.rating >= 4.0:
            reasons.append(f"Highly rated ({asset.rating}/5.0)")

        if asset.usage_count >= 5:
            reasons.append(f"Popular choice ({asset.usage_count} uses)")

        if context and context.get("fire_active") and "fire" in asset.name.lower():
            reasons.append("Relevant to current fire scenario")

        return reasons

    def create_asset_pack_recommendation(
        self,
        user_profile: Optional[UserProfile] = None,
        theme: str = "general",
    ) -> Dict[str, Any]:
        """Recommend a pack of assets for a theme"""
        if theme == "fire":
            fire_assets = [
                a for a in self.asset_manager.get_all_assets()
                if "fire" in a.name.lower()
            ]
            return {
                "name": "Fire Scenarios Pack",
                "description": "Assets for fire-related stories",
                "assets": fire_assets,
                "confidence": 0.85,
            }

        return {
            "name": "General Purpose Pack",
            "description": "Commonly used assets",
            "assets": self.asset_manager.get_all_assets()[:5],
            "confidence": 0.6,
        }

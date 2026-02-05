import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .asset import Asset
from .asset_types import AssetType


class AssetManager:
    """Manages asset storage, retrieval, and statistics"""

    def __init__(self, storage_path: str = "data/assets"):
        self.storage_path = storage_path
        self.assets: Dict[str, Asset] = {}
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)

    def save_asset(self, asset: Asset) -> None:
        """Save an asset to storage"""
        self.assets[asset.id] = asset

        # Save to disk
        asset_file = os.path.join(self.storage_path, f"{asset.id}.json")
        with open(asset_file, "w") as f:
            json.dump(asset.to_dict(), f, indent=2)

    def load_asset(self, asset_id: str) -> Optional[Asset]:
        """Load an asset from storage"""
        if asset_id in self.assets:
            return self.assets[asset_id]

        asset_file = os.path.join(self.storage_path, f"{asset_id}.json")
        if os.path.exists(asset_file):
            with open(asset_file, "r") as f:
                data = json.load(f)
                asset = Asset.from_dict(data)
                self.assets[asset_id] = asset
                return asset

        return None

    def get_all_assets(self) -> List[Asset]:
        """Get all assets"""
        return list(self.assets.values())

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """Get assets by type"""
        return [a for a in self.assets.values() if a.asset_type == asset_type]

    def search_assets(self, query: str) -> List[Asset]:
        """Search assets by name or description"""
        query = query.lower()
        return [
            a for a in self.assets.values()
            if query in a.name.lower() or query in a.description.lower()
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get asset statistics"""
        total_assets = len(self.assets)
        total_usage = sum(a.usage_count for a in self.assets.values())
        avg_rating = sum(a.rating for a in self.assets.values()) / total_assets if total_assets > 0 else 0

        by_type = {}
        for asset_type in AssetType:
            by_type[asset_type.value] = len(self.get_assets_by_type(asset_type))

        return {
            "total_assets": total_assets,
            "total_usage": total_usage,
            "avg_rating": avg_rating,
            "by_type": by_type,
        }

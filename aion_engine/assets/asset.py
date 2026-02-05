from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime

from .asset_types import AssetType


@dataclass
class Asset:
    """Represents a reusable asset in the system"""
    id: str
    asset_type: AssetType
    name: str
    description: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    rating: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary"""
        return {
            "id": self.id,
            "asset_type": self.asset_type.value,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "metadata": self.metadata,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "created_at": self.created_at,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        """Create asset from dictionary"""
        return cls(
            id=data["id"],
            asset_type=AssetType(data["asset_type"]),
            name=data["name"],
            description=data["description"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            usage_count=data.get("usage_count", 0),
            rating=data.get("rating", 0.0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            tags=data.get("tags", []),
        )

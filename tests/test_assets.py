from aion_engine.assets.asset_types import AssetType
from aion_engine.assets.asset import Asset


def test_asset_creation():
    """Test creating a new asset"""
    asset = Asset(
        id="test-1",
        asset_type=AssetType.WORLD_RULE,
        name="Fire Physics Rule",
        description="Rules governing fire behavior",
        content={"fire_spreads": True, "temperature_effects": True},
    )

    assert asset.id == "test-1"
    assert asset.asset_type == AssetType.WORLD_RULE
    assert asset.name == "Fire Physics Rule"
    assert asset.usage_count == 0
    assert asset.rating == 0.0


def test_asset_to_dict():
    """Test converting asset to dictionary"""
    asset = Asset(
        id="test-1",
        asset_type=AssetType.WORLD_RULE,
        name="Fire Physics Rule",
        description="Rules governing fire behavior",
        content={"fire_spreads": True},
    )

    data = asset.to_dict()

    assert data["id"] == "test-1"
    assert data["asset_type"] == "world_rule"
    assert data["name"] == "Fire Physics Rule"
    assert data["content"]["fire_spreads"] is True


def test_asset_from_dict():
    """Test creating asset from dictionary"""
    data = {
        "id": "test-1",
        "asset_type": "world_rule",
        "name": "Fire Physics Rule",
        "description": "Rules governing fire behavior",
        "content": {"fire_spreads": True},
        "usage_count": 5,
        "rating": 4.5,
    }

    asset = Asset.from_dict(data)

    assert asset.id == "test-1"
    assert asset.asset_type == AssetType.WORLD_RULE
    assert asset.usage_count == 5
    assert asset.rating == 4.5


def test_asset_lifecycle():
    """Test asset lifecycle: creation, usage, rating"""
    asset = Asset(
        id="test-1",
        asset_type=AssetType.PATTERN,
        name="Fire Pattern",
        description="Common fire pattern",
        content={"events": ["fire_start", "temperature_rise"]},
    )

    # Use the asset
    asset.usage_count += 1
    assert asset.usage_count == 1

    # Rate the asset
    asset.rating = 4.5
    assert asset.rating == 4.5

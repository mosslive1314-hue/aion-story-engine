import tempfile
import os
from aion_engine.assets.manager import AssetManager
from aion_engine.assets.precipitation import AssetPrecipitation
from aion_engine.assets.asset import Asset
from aion_engine.assets.asset_types import AssetType
from aion_engine.medici import MediciSynapse
from aion_engine.profile import UserProfile
from aion_engine.recommendation import RecommendationEngine


def test_phase2_complete_workflow():
    """Test complete Phase 2 workflow"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Create asset manager
        manager = AssetManager(storage_path=os.path.join(tmpdir, "assets"))

        # 2. Create an asset
        fire_rule = Asset(
            id="fire-1",
            asset_type=AssetType.WORLD_RULE,
            name="Fire Physics",
            description="Rules for fire behavior",
            content={"temperature_rise": 150, "spread_rate": 0.8},
            usage_count=5,
            rating=4.5,
        )
        manager.save_asset(fire_rule)

        # 3. Test precipitation
        precipitation = AssetPrecipitation()
        events = [
            {"type": "fire_start", "source": "alcohol"},
            {"type": "temperature_rise", "value": 150},
        ]
        suggestions = precipitation.detect_patterns(events)

        assert len(suggestions) > 0
        assert suggestions[0]["type"] == "pattern_detected"

        # 4. Test Medici Synapse
        medici = MediciSynapse()
        innovation = medici.generate_innovation("physics", "magic", "storytelling")

        assert "name" in innovation
        assert innovation["domain1"] == "physics"
        assert innovation["domain2"] == "magic"

        # 5. Test user profile
        profile = UserProfile(user_id="test-user")
        profile.update_genre_preference("sci-fi", 0.8)
        profile.record_intent("I want fire", "fire scenario", 0.9)

        assert profile.creative_fingerprint.genre_preferences["sci-fi"] == 0.8
        assert len(profile.intent_history) == 1

        # 6. Test recommendation
        recommender = RecommendationEngine(manager)
        recommendations = recommender.recommend_assets(
            user_profile=profile,
            context={"fire_active": True},
            limit=5,
        )

        assert len(recommendations) > 0

        # 7. Test statistics
        stats = manager.get_statistics()
        assert stats["total_assets"] >= 1
        assert stats["total_usage"] >= 5

        print("✅ Phase 2 complete workflow test passed!")


def test_asset_lifecycle():
    """Test complete asset lifecycle"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AssetManager(storage_path=os.path.join(tmpdir, "assets"))

        # Create
        asset = Asset(
            id="test-1",
            asset_type=AssetType.PATTERN,
            name="Test Pattern",
            description="A test pattern",
            content={"events": ["event1", "event2"]},
        )

        # Save
        manager.save_asset(asset)
        assert asset.id in manager.assets

        # Load
        loaded = manager.load_asset(asset.id)
        assert loaded is not None
        assert loaded.name == "Test Pattern"

        # Search
        results = manager.search_assets("test")
        assert len(results) == 1

        # Get by type
        patterns = manager.get_assets_by_type(AssetType.PATTERN)
        assert len(patterns) == 1

        print("✅ Asset lifecycle test passed!")


def test_medici_synapse_innovation():
    """Test Medici Synapse innovation generation"""
    medici = MediciSynapse()

    # Test cross-domain innovation
    innovation = medici.generate_innovation("physics", "biology", "story")

    assert "name" in innovation
    assert "description" in innovation
    assert innovation["confidence"] > 0

    # Convert to asset
    asset_suggestion = medici.create_asset_from_innovation(innovation)

    assert asset_suggestion["asset_type"] == "world_rule"
    assert "tags" in asset_suggestion

    print("✅ Medici Synapse innovation test passed!")


def test_user_profile_evolution():
    """Test user profile evolution"""
    profile = UserProfile(user_id="test")

    # Initial state
    assert len(profile.creative_fingerprint.genre_preferences) == 0

    # Update preferences
    profile.update_genre_preference("sci-fi", 0.8)
    profile.update_genre_preference("fantasy", 0.6)

    assert profile.creative_fingerprint.genre_preferences["sci-fi"] == 0.8

    # Record intents
    profile.record_intent("I want lasers", "sci-fi technology", 0.85)

    assert len(profile.intent_history) == 1

    # Get top genres
    top = profile.get_top_genres(1)
    assert top[0][0] == "sci-fi"

    print("✅ User profile evolution test passed!")


def test_recommendation_engine():
    """Test recommendation engine"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AssetManager(storage_path=os.path.join(tmpdir, "assets"))

        # Add assets
        assets = [
            Asset(
                id=f"asset-{i}",
                asset_type=AssetType.WORLD_RULE,
                name=f"Fire Rule {i}",
                description=f"Fire rule {i}",
                content={},
                usage_count=i * 2,
                rating=4.0 + i * 0.2,
            )
            for i in range(1, 4)
        ]

        for asset in assets:
            manager.save_asset(asset)

        # Create profile
        profile = UserProfile(user_id="test")
        profile.update_genre_preference("sci-fi", 0.9)

        # Get recommendations
        recommender = RecommendationEngine(manager)
        recs = recommender.recommend_assets(
            user_profile=profile,
            context={"fire_active": True},
        )

        assert len(recs) > 0

        # Test asset pack
        pack = recommender.create_asset_pack_recommendation(
            user_profile=profile,
            theme="fire",
        )

        assert "name" in pack
        assert "assets" in pack

        print("✅ Recommendation engine test passed!")

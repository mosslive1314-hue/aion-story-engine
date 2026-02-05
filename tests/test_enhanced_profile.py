from aion_engine.profile.fingerprint import CreativeFingerprint


def test_enhanced_creative_fingerprint():
    """Test enhanced creative fingerprint with style markers"""
    fp = CreativeFingerprint()

    # Test style markers
    fp.style_markers["physics_realism"] = 0.92
    fp.style_markers["npc_depth"] = 0.88
    fp.style_markers["narrative_structure"] = "non-linear"
    fp.style_markers["detail_level"] = "high"

    assert fp.style_markers["physics_realism"] == 0.92
    assert fp.style_markers["npc_depth"] == 0.88
    assert fp.style_markers["narrative_structure"] == "non-linear"
    assert fp.style_markers["detail_level"] == "high"


def test_creation_patterns():
    """Test creation patterns tracking"""
    fp = CreativeFingerprint()

    # Test creation patterns
    fp.creation_patterns["peak_hours"] = [23, 0, 1, 2]
    fp.creation_patterns["avg_session_duration"] = 180
    fp.creation_patterns["iteration_count"] = 5.3

    assert 23 in fp.creation_patterns["peak_hours"]
    assert fp.creation_patterns["avg_session_duration"] == 180
    assert fp.creation_patterns["iteration_count"] == 5.3


def test_genre_preferences():
    """Test genre preferences with multiple updates"""
    from aion_engine.profile.fingerprint import UserProfile

    profile = UserProfile(user_id="test-user")

    # Update genre preferences
    profile.update_genre_preference("科幻", 0.5)
    profile.update_genre_preference("奇幻", 0.3)
    profile.update_genre_preference("科幻", 0.7)  # Update

    # Check exponential moving average
    assert profile.creative_fingerprint.genre_preferences["科幻"] == 0.5 * 0.7 + 0.7 * 0.3
    assert profile.creative_fingerprint.genre_preferences["奇幻"] == 0.3


def test_top_genres():
    """Test getting top genres"""
    from aion_engine.profile.fingerprint import UserProfile

    profile = UserProfile(user_id="test-user")
    profile.update_genre_preference("科幻", 0.8)
    profile.update_genre_preference("奇幻", 0.6)
    profile.update_genre_preference("悬疑", 0.4)

    top = profile.get_top_genres(2)

    assert len(top) == 2
    assert top[0][0] == "科幻"
    assert top[0][1] == 0.8
    assert top[1][0] == "奇幻"
    assert top[1][1] == 0.6

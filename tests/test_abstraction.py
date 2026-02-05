from aion_engine.core.abstraction import AbstractionEngine
from aion_engine.core.blackboard import Blackboard


def test_pattern_recognition():
    """Test that abstraction engine can recognize patterns from events"""
    engine = AbstractionEngine()

    # Simulate a series of events (fire scenario)
    events = [
        {"type": "fire_start", "source": "alcohol", "target": "plant"},
        {"type": "temperature_rise", "from": 25, "to": 150},
        {"type": "npc_stress_increase", "npc": "isaac", "level": 0.8},
        {"type": "npc_action", "action": "extinguish_fire"},
    ]

    patterns = engine.extract_patterns(events)

    assert len(patterns) > 0
    assert any("fire" in p.name.lower() for p in patterns)


def test_knowledge_storage():
    """Test that patterns can be stored and retrieved"""
    engine = AbstractionEngine()

    # Create a pattern
    pattern = engine.create_pattern(
        name="Fire Panic Chain",
        description="Fire causes temperature rise, NPC stress, and panic response",
        events=[
            {"type": "fire_start"},
            {"type": "temperature_rise"},
            {"type": "npc_stress_increase"},
        ],
    )

    assert pattern.id is not None
    assert pattern.name == "Fire Panic Chain"

    # Store and retrieve
    engine.save_pattern(pattern)
    retrieved = engine.get_pattern(pattern.id)

    assert retrieved is not None
    assert retrieved.name == pattern.name


def test_pattern_application():
    """Test that patterns can be applied to new scenarios"""
    engine = AbstractionEngine()

    # Save a pattern
    pattern = engine.create_pattern(
        name="Basic Fire Response",
        description="Fire triggers灭火 response",
        events=[
            {"type": "fire_start", "intensity": "high"},
        ],
    )
    engine.save_pattern(pattern)

    # Apply to new scenario
    new_events = [
        {"type": "fire_start", "intensity": "high", "location": "kitchen"},
    ]
    matches = engine.apply_patterns(new_events)

    assert len(matches) > 0
    assert matches[0].pattern.name == "Basic Fire Response"
    assert matches[0].confidence > 0.5

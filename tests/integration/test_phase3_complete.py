from aion_engine.digital_twin import DigitalTwin
from aion_engine.memory.graph import MemoryGraph, Concept
from aion_engine.suggestions.engine import SuggestionsEngine, Suggestion


def test_memory_graph():
    """Test memory graph functionality"""
    mg = MemoryGraph()

    # Add concepts
    mg.add_concept("Fire Physics", ["fire-rule-1"], initial_strength=1.0)
    mg.add_concept("NPC Behavior", ["npc-template-1"], initial_strength=1.0)

    # Add relationships
    mg.add_relationship("Fire Physics", "NPC Behavior", 0.8)

    # Test usage update
    mg.update_usage("Fire Physics")
    mg.update_satisfaction("Fire Physics", 4.5)

    concept = mg.get_concept("Fire Physics")
    assert concept.usage_count == 1
    assert concept.satisfaction > 0

    # Test related concepts
    related = mg.get_related_concepts("Fire Physics")
    assert "NPC Behavior" in related

    print("✅ Memory graph test passed!")


def test_suggestions_engine():
    """Test suggestions engine"""
    suggestions = SuggestionsEngine()

    # Generate suggestions
    context = {"fire_active": True}
    user_state = {"physics_realism": 0.8, "idle_time": 0}
    suggestions_list = suggestions.generate_suggestions(context, user_state, limit=5)

    assert len(suggestions_list) > 0

    # Check for fire-related suggestion
    fire_suggestion = next(
        (s for s in suggestions_list if s.type == "asset" and "火" in s.title),
        None
    )
    assert fire_suggestion is not None
    assert fire_suggestion.confidence > 0.8

    print("✅ Suggestions engine test passed!")


def test_digital_twin_complete_workflow():
    """Test complete digital twin workflow"""
    dt = DigitalTwin(user_id="test-user")

    # Process vague input
    result = dt.process_user_input("实验室起火了")

    assert "intent" in result
    assert result["intent"]["intent"] == "fire_scenario"
    assert result["intent"]["confidence"] > 0.7

    # Check suggestions
    assert "suggestions" in result
    assert len(result["suggestions"]) > 0

    # Update skill
    dt.update_skill_rating("physics", 4.5)
    assert dt.profile.satisfaction_scores["physics"] == 4.5

    # Add memory concept
    dt.add_memory_concept("Quantum Magic", ["quantum-asset", "magic-asset"])
    concept = dt.memory_graph.get_concept("Quantum Magic")
    assert concept is not None

    # Get stats
    stats = dt.get_digital_twin_stats()
    assert "user_id" in stats
    assert "profile_stats" in stats
    assert "memory_stats" in stats

    print("✅ Digital twin workflow test passed!")


def test_intent_inference():
    """Test intent inference with vague input"""
    dt = DigitalTwin(user_id="test-user")

    # Test vague input
    result1 = dt.process_user_input("就是那种...你懂的")
    assert result1["intent"]["confidence"] >= 0.3

    # Correct the intent
    dt.intent_engine.correct_intent("就是那种...你懂的", "fire_scenario")

    # Re-infer with correction
    result2 = dt.process_user_input("就是那种...你懂的")
    assert result2["intent"]["intent"] == "fire_scenario"
    assert result2["intent"]["confidence"] > result1["intent"]["confidence"]

    print("✅ Intent inference test passed!")


def test_memory_concept_evolution():
    """Test memory concept evolution"""
    mg = MemoryGraph()

    # Add concept
    mg.add_concept("Hard Physics", initial_strength=1.0)

    # Update usage multiple times
    for _ in range(5):
        mg.update_usage("Hard Physics")

    # Update satisfaction (initial was 0.0, then 0.7*0.0 + 0.3*4.8 = 1.44)
    # We need to call it multiple times to reach > 4.0
    for _ in range(10):
        mg.update_satisfaction("Hard Physics", 4.8)

    concept = mg.get_concept("Hard Physics")
    assert concept.usage_count == 5
    # After 10 updates: 0.7^10*0.0 + (1-0.7^10)*4.8 ≈ 4.6 > 4.0
    assert concept.satisfaction > 4.0

    # Get top concepts
    top = mg.get_top_concepts(limit=1)
    assert len(top) == 1
    assert top[0][0] == "Hard Physics"

    print("✅ Memory evolution test passed!")


def test_breakthrough_detection():
    """Test breakthrough detection"""
    suggestions = SuggestionsEngine()

    # Simulate breakthrough state
    user_state = {"just_achieved": True, "skill_growth_rate": 0.2}
    breakthrough = suggestions.get_breakthrough_suggestion(user_state)

    assert breakthrough is not None
    assert breakthrough.type == "breakthrough"
    assert breakthrough.confidence > 0.9

    print("✅ Breakthrough detection test passed!")

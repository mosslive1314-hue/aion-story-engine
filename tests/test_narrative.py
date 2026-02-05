from aion_engine.core.blackboard import Blackboard
from aion_engine.core.narrative import NarrativeEngine

def test_generate_narrative():
    bb = Blackboard()
    bb.update_world_state("fire_active", True)
    bb.update_npc_state("isaac", "stress_level", 0.8)

    engine = NarrativeEngine()
    result = engine.generate(bb)

    assert len(result) > 0
    assert "fire" in result.lower() or "艾萨克" in result

def test_timeline_prediction():
    bb = Blackboard()
    bb.update_world_state("fire_active", True)

    engine = NarrativeEngine()
    prediction = engine.predict_next_event(bb)

    assert "火灾" in prediction or "extinguish" in prediction

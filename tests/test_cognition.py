from aion_engine.core.blackboard import Blackboard
from aion_engine.core.cognition import CognitionEngine

def test_npc_decision_making():
    bb = Blackboard()
    bb.update_npc_state("isaac", "stress_level", 0.8)
    bb.update_world_state("fire_active", True)
    bb.update_npc_state("isaac", "priority_protect", True)

    engine = CognitionEngine()
    result = engine.process(bb)

    assert "isaac" in result.npc_actions
    assert len(result.npc_actions["isaac"]) > 0

def test_isaac_fire_response():
    bb = Blackboard()
    bb.update_npc_state("isaac", "role", "scientist")
    bb.update_world_state("fire_active", True)

    engine = CognitionEngine()
    result = engine.process(bb)

    assert result.npc_actions["isaac"][0]["action"] in [
        "extinguish_fire", "escape", "prioritize_notes"
    ]

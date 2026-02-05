from aion_engine.core.blackboard import Blackboard


def test_blackboard_initialization():
    bb = Blackboard()
    assert bb.world_state == {}
    assert bb.npcs == {}
    assert bb.event_queue == []


def test_blackboard_update():
    bb = Blackboard()
    bb.update_world_state("temperature", 25.0)
    assert bb.world_state["temperature"] == 25.0

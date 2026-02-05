from aion_engine.core.blackboard import Blackboard
from aion_engine.core.physics import PhysicsEngine


def test_fire_spreads():
    bb = Blackboard()
    bb.update_world_state("fire_active", True)
    bb.update_world_state("oxygen_level", 0.21)
    bb.update_world_state("fuel_available", True)

    engine = PhysicsEngine()
    result = engine.process(bb)

    assert result.world_state["temperature"] > 100
    assert any(event.get("type") == "fire_has_spread" for event in result.events)


def test_conservation_of_energy():
    bb = Blackboard()
    bb.update_world_state("energy_total", 1000)

    engine = PhysicsEngine()
    result = engine.process(bb)

    assert "energy_total" in result.world_state

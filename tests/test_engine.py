from aion_engine.engine import StoryEngine


def test_full_cycle():
    engine = StoryEngine()
    result = engine.advance("点燃酒精", {"location": "实验室"})

    assert "temperature" in result.world_state
    assert len(result.narrative) > 0


def test_lab_fire_scenario():
    engine = StoryEngine()
    result = engine.advance("打翻酒精瓶", {"location": "实验室"})

    assert result.world_state.get("fire_active") == True
    assert "isaac" in result.npc_actions

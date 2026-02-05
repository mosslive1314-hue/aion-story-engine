import os
import tempfile

from aion_engine.session import Session


def test_lab_fire_scenario():
    """Integration test: Full lab fire scenario"""
    with tempfile.TemporaryDirectory() as tmpdir:
        session = Session.create(tmpdir, "实验室火灾测试")

        # Step 1: Start in lab
        result1 = session.advance("进入实验室", {"location": "实验室"})
        assert "实验室" in result1.narrative

        # Step 2: Ignite fire
        result2 = session.advance("打翻酒精瓶并点火", {"location": "实验室"})
        assert result2.world_state.get("fire_active") == True

        # Step 3: NPC reacts
        assert "isaac" in result2.npc_actions

        # Save and verify
        session.save()
        assert os.path.exists(os.path.join(session.session_dir, "metadata.json"))

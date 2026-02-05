from aion_engine.collaboration.manager import CollaborationManager
from aion_engine.collaboration.consensus import ConsensusEngine


def test_multi_user_session():
    """Test multi-user collaboration session"""
    manager = CollaborationManager()

    # Create a session
    session = manager.create_session("lab-fire-story", owner_id="alice")
    assert session.session_id is not None
    assert session.owner_id == "alice"

    # Add collaborators
    manager.add_collaborator(session.session_id, "bob", role="editor")
    manager.add_collaborator(session.session_id, "charlie", role="viewer")

    # Verify collaborators
    session = manager.get_session(session.session_id)
    assert len(session.collaborators) == 2
    assert "bob" in session.collaborators
    assert "charlie" in session.collaborators


def test_change_tracking():
    """Test change tracking in collaborative editing"""
    manager = CollaborationManager()
    session = manager.create_session("test-story", owner_id="alice")

    # Alice makes a change
    change1 = manager.record_change(
        session_id=session.session_id,
        user_id="alice",
        change_type="add_node",
        content={"action": "点燃酒精", "location": "实验室"},
    )

    assert change1.change_id is not None
    assert change1.user_id == "alice"

    # Bob makes a change
    change2 = manager.record_change(
        session_id=session.session_id,
        user_id="bob",
        change_type="update_npc",
        content={"npc": "isaac", "state": "panic"},
    )

    assert change2.change_id != change1.change_id
    assert len(session.changes) == 2


def test_consensus_engine():
    """Test consensus engine for conflict resolution"""
    consensus = ConsensusEngine()

    # Simulate conflicting changes
    changes = [
        {"user_id": "alice", "change_type": "fire_spreads", "value": True},
        {"user_id": "bob", "change_type": "fire_spreads", "value": False},
    ]

    decision = consensus.resolve_conflict(changes)
    assert decision is not None
    assert "resolved_changes" in decision


def test_permission_check():
    """Test user permission checking"""
    manager = CollaborationManager()
    session = manager.create_session("test-story", owner_id="alice")

    # Owner can do anything
    assert manager.check_permission(session.session_id, "alice", "edit") == True
    assert manager.check_permission(session.session_id, "alice", "admin") == True

    # Editor can edit
    manager.add_collaborator(session.session_id, "bob", role="editor")
    assert manager.check_permission(session.session_id, "bob", "edit") == True
    assert manager.check_permission(session.session_id, "bob", "admin") == False

    # Viewer can only view
    manager.add_collaborator(session.session_id, "charlie", role="viewer")
    assert manager.check_permission(session.session_id, "charlie", "edit") == False
    assert manager.check_permission(session.session_id, "charlie", "view") == True

from aion_engine.collaboration.manager import CollaborationManager
from aion_engine.economy.marketplace import Marketplace
from aion_engine.cli.main import CLIInterface
from aion_engine.api.main import api


def test_collaboration_workflow():
    """Test complete collaboration workflow"""
    # Create a session
    manager = CollaborationManager()
    session = manager.create_session("Epic Lab Fire", owner_id="alice")

    # Add collaborators
    manager.add_collaborator(session.session_id, "bob", role="editor")
    manager.add_collaborator(session.session_id, "charlie", role="viewer")

    # Record changes
    change1 = manager.record_change(
        session_id=session.session_id,
        user_id="alice",
        change_type="add_node",
        content={"action": "点燃酒精"},
    )

    change2 = manager.record_change(
        session_id=session.session_id,
        user_id="bob",
        change_type="update_npc",
        content={"npc": "isaac", "state": "panic"},
    )

    # Verify
    assert len(session.changes) == 2
    assert "bob" in session.collaborators

    print("✅ Collaboration workflow test passed!")


def test_marketplace_workflow():
    """Test complete marketplace workflow"""
    marketplace = Marketplace()

    # List an asset
    listing = marketplace.list_asset(
        asset_id="fire-rule-1",
        creator_id="alice",
        title="硬核热力学规则",
        description="详细的火灾物理模拟规则",
        price=0.0,
        license="MIT",
    )

    assert listing.listing_id in marketplace.listings

    # Add review
    review = marketplace.add_review(
        listing_id=listing.listing_id,
        user_id="bob",
        rating=5,
        comment="非常好用！",
    )

    assert listing.rating == 5.0

    # Get statistics
    stats = marketplace.get_statistics()
    assert stats["total_listings"] == 1

    print("✅ Marketplace workflow test passed!")


def test_cli_workflow():
    """Test CLI interface"""
    cli = CLIInterface()

    # Create story
    result = cli.execute("create", {"name": "My Story"})
    assert "Creating" in result

    # Show marketplace
    result = cli.execute("marketplace", {})
    assert "Asset Marketplace" in result

    # List assets
    result = cli.execute("assets", {})
    assert "Your Assets" in result

    print("✅ CLI workflow test passed!")


def test_api_workflow():
    """Test API interface"""
    # Get session
    response = api.handle_request("GET", "/sessions/123")
    assert response["status_code"] == 200

    # Create session
    response = api.handle_request("POST", "/sessions", {"name": "Test Story"})
    assert response["status_code"] == 200
    assert response["data"]["name"] == "Test Story"

    # Get assets
    response = api.handle_request("GET", "/assets")
    assert response["status_code"] == 200
    assert "assets" in response["data"]

    print("✅ API workflow test passed!")


def test_sync_workflow():
    """Test sync engine"""
    from aion_engine.sync.engine import SyncEngine

    sync = SyncEngine()

    # Create change set
    changes = [{"type": "add_node", "data": "test"}]
    change_set = sync.create_change_set("session-123", changes)

    assert change_set["session_id"] == "session-123"

    # Detect conflicts
    local = {"key1": "value1"}
    remote = {"key1": "value2"}
    conflicts = sync.detect_conflicts(local, remote)

    assert len(conflicts) > 0

    print("✅ Sync workflow test passed!")


def test_phase4_complete_integration():
    """Test complete Phase 4 integration"""
    # 1. Create collaboration session
    manager = CollaborationManager()
    session = manager.create_session("Collaborative Story", owner_id="alice")

    # 2. Add marketplace listing
    marketplace = Marketplace()
    listing = marketplace.list_asset(
        asset_id="pattern-1",
        creator_id="alice",
        title="Collaborative Fire Pattern",
        description="Pattern for collaborative fire scenarios",
        price=5.0,
        license="CC BY",
    )

    # 3. Execute CLI commands
    cli = CLIInterface()
    create_result = cli.execute("create", {"name": "Test"})

    # 4. Use API
    api_response = api.handle_request("GET", "/assets")

    # 5. Verify integration
    assert len(marketplace.listings) == 1
    assert "Test" in create_result
    assert api_response["status_code"] == 200

    print("✅ Complete Phase 4 integration test passed!")

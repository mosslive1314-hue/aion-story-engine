"""
Phase 4 & 5: API Tests
测试API端点的功能
"""

import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path

# 导入API应用
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestCollaborationAPI:
    """测试协作API"""

    def test_create_session(self, client):
        """测试创建会话"""
        response = client.post("/api/collaboration/sessions", json={
            "story_id": "story-1",
            "user_id": "user-1",
            "name": "Test User",
            "email": "test@example.com"
        })

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["story_id"] == "story-1"

    def test_join_session(self, client):
        """测试加入会话"""
        # 先创建会话
        create_response = client.post("/api/collaboration/sessions", json={
            "story_id": "story-1",
            "user_id": "user-1",
            "name": "User 1",
            "email": "user1@example.com"
        })

        session_id = create_response.json()["session_id"]

        # 加入会话
        response = client.post(f"/api/collaboration/sessions/{session_id}/join", json={
            "user_id": "user-2",
            "name": "User 2",
            "email": "user2@example.com",
            "role": "editor"
        })

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_get_active_users(self, client):
        """测试获取活跃用户"""
        # 创建会话
        create_response = client.post("/api/collaboration/sessions", json={
            "story_id": "story-1",
            "user_id": "user-1",
            "name": "Test User",
            "email": "test@example.com"
        })

        session_id = create_response.json()["session_id"]

        # 获取活跃用户
        response = client.get(f"/api/collaboration/sessions/{session_id}/users")

        assert response.status_code == 200
        data = response.json()
        assert "active_users" in data

    def test_submit_change(self, client):
        """测试提交变更"""
        # 创建会话
        create_response = client.post("/api/collaboration/sessions", json={
            "story_id": "story-1",
            "user_id": "user-1",
            "name": "Test User",
            "email": "test@example.com"
        })

        session_id = create_response.json()["session_id"]

        # 提交变更
        response = client.post("/api/collaboration/changes", json={
            "session_id": session_id,
            "user_id": "user-1",
            "node_id": "node-1",
            "change_type": "update",
            "new_value": "Updated content"
        })

        assert response.status_code == 200
        assert response.json()["success"] is True


class TestSyncAPI:
    """测试同步API"""

    def test_get_sync_status(self, client):
        """测试获取同步状态"""
        response = client.get("/api/sync/status")

        assert response.status_code == 200
        data = response.json()
        assert "pending_changes" in data
        assert "sync_status" in data


class TestMarketplaceAPI:
    """测试市场API"""

    def test_search_assets(self, client):
        """测试搜索资产"""
        response = client.post("/api/marketplace/assets/search", json={
            "query": "test",
            "limit": 10
        })

        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "count" in data

    def test_get_trending_assets(self, client):
        """测试获取热门资产"""
        response = client.get("/api/marketplace/assets/trending?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "assets" in data

    def test_get_marketplace_statistics(self, client):
        """测试获取市场统计"""
        response = client.get("/api/marketplace/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "total_creators" in data


class TestMultiverseAPI:
    """测试多元宇宙API"""

    def test_create_world(self, client):
        """测试创建世界"""
        response = client.post("/api/multiverse/worlds", json={
            "name": "Test World",
            "world_type": "fantasy",
            "scale": "world",
            "description": "A test world"
        })

        assert response.status_code == 200
        data = response.json()
        assert "world_id" in data

    def test_search_worlds(self, client):
        """测试搜索世界"""
        response = client.post("/api/multiverse/worlds/search", json={
            "query": "test",
            "limit": 10
        })

        assert response.status_code == 200
        data = response.json()
        assert "worlds" in data


class TestDAOAPI:
    """测试DAO API"""

    def test_create_dao(self, client):
        """测试创建DAO"""
        response = client.post("/api/dao/create", json={
            "dao_id": "dao-1",
            "name": "Test DAO",
            "description": "A test DAO"
        })

        assert response.status_code == 200
        data = response.json()
        assert "dao_id" in data

    def test_create_proposal(self, client):
        """测试创建提案"""
        response = client.post("/api/dao/proposals", json={
            "dao_id": "dao-1",
            "title": "Test Proposal",
            "description": "A test proposal",
            "proposal_type": "governance",
            "proposer_id": "user-1"
        })

        assert response.status_code == 200
        data = response.json()
        assert "proposal_id" in data


class TestEconomyAPI:
    """测试经济API"""

    def test_stake_tokens(self, client):
        """测试质押代币"""
        response = client.post("/api/economy/stake", json={
            "user_id": "user-1",
            "token_type": "governance",
            "amount": 100.0,
            "lock_period_days": 30
        })

        assert response.status_code == 200
        data = response.json()
        assert "position_id" in data

    def test_get_portfolio(self, client):
        """测试获取投资组合"""
        response = client.get("/api/economy/portfolio?user_id=user-1")

        assert response.status_code == 200
        data = response.json()
        assert "token_balances" in data


@pytest.mark.integration
class TestAPIIntegration:
    """集成测试 - API整体流程"""

    def test_complete_collaboration_workflow(self, client):
        """测试完整的协作工作流"""
        # 1. 创建会话
        session_response = client.post("/api/collaboration/sessions", json={
            "story_id": "story-1",
            "user_id": "user-1",
            "name": "User 1",
            "email": "user1@example.com"
        })

        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]

        # 2. 加入会话
        join_response = client.post(f"/api/collaboration/sessions/{session_id}/join", json={
            "user_id": "user-2",
            "name": "User 2",
            "email": "user2@example.com",
            "role": "editor"
        })

        assert join_response.status_code == 200

        # 3. 提交变更
        change_response = client.post("/api/collaboration/changes", json={
            "session_id": session_id,
            "user_id": "user-1",
            "node_id": "node-1",
            "change_type": "create",
            "new_value": {"content": "Chapter 1"}
        })

        assert change_response.status_code == 200

        # 4. 获取变更历史
        changes_response = client.get(f"/api/collaboration/sessions/{session_id}/changes")

        assert changes_response.status_code == 200
        changes = changes_response.json()
        assert changes["count"] >= 1

    def test_complete_marketplace_workflow(self, client):
        """测试完整的市场工作流"""
        # 1. 创建创作者档案
        profile_response = client.post("/api/marketplace/creators", json={
            "user_id": "creator-1",
            "display_name": "Test Creator",
            "bio": "A test creator"
        })

        assert profile_response.status_code == 200
        creator_id = profile_response.json()["creator_id"]

        # 2. 发布资产
        asset_response = client.post("/api/marketplace/assets", json={
            "creator_id": creator_id,
            "asset_type": "pattern",
            "name": "Test Pattern",
            "description": "A test pattern",
            "price": 9.99
        })

        assert asset_response.status_code == 200
        asset_id = asset_response.json()["asset_id"]

        # 3. 搜索资产
        search_response = client.post("/api/marketplace/assets/search", json={
            "query": "Test",
            "limit": 10
        })

        assert search_response.status_code == 200

        # 4. 获取统计
        stats_response = client.get("/api/marketplace/statistics")
        assert stats_response.status_code == 200


@pytest.mark.performance
class TestAPIPerformance:
    """性能测试"""

    def test_api_response_time(self, client):
        """测试API响应时间"""
        import time

        # 测试搜索资产性能
        start = time.time()

        for _ in range(10):
            response = client.get("/api/marketplace/assets/trending?limit=10")
            assert response.status_code == 200

        elapsed = time.time() - start

        # 平均响应时间应在100ms内
        assert elapsed / 10 < 0.1

    def test_concurrent_requests(self, client):
        """测试并发请求"""
        import threading
        import time

        def make_request():
            response = client.get("/api/marketplace/statistics")
            assert response.status_code == 200

        threads = []
        start = time.time()

        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        elapsed = time.time() - start

        # 10个并发请求应在2秒内完成
        assert elapsed < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

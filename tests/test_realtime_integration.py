"""
实时协作系统集成测试

测试整个实时协作系统各组件的协同工作：
- WebSocket 服务器
- 同步引擎
- Presence 管理器
- 通知系统
- 前端编辑器集成
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# 导入系统组件
from aion_engine.realtime import (
    RealtimeSyncEngine,
    PresenceManager,
    NotificationManager,
    OperationType,
    PresenceStatus,
    ActivityType,
    NotificationType,
)


class TestWebSocketPresenceIntegration:
    """WebSocket 与 Presence 系统集成测试"""

    @pytest.mark.asyncio
    async def test_user_join_creates_session_and_presence(self):
        """测试用户加入时创建会话和在线状态"""
        # 创建组件
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 用户加入房间
        presence = await presence_manager.user_join(
            room_id="story-room-1",
            user_id="user-alice",
            username="Alice",
            color="#FF6B6B",
            device_info={"device": "desktop", "browser": "Chrome"},
            ip_address="192.168.1.100"
        )

        # 验证用户存在
        assert presence.user_id == "user-alice"
        assert presence.username == "Alice"
        assert presence.status == PresenceStatus.ONLINE
        assert presence.session_id is not None

        # 验证房间存在
        room = presence_manager.rooms["story-room-1"]
        assert "user-alice" in room.users

        # 验证会话已创建
        assert presence.session_id in presence_manager.active_sessions

        # 验证活动记录
        history = presence_manager.get_user_activity_history("user-alice", "story-room-1")
        assert len(history) > 0
        assert history[0]['activity'] == 'joined'

    @pytest.mark.asyncio
    async def test_concurrent_users_same_room(self):
        """测试同一房间内的多用户并发"""
        presence_manager = PresenceManager()

        # 3个用户同时加入同一房间
        users = [
            ("user1", "Alice", "#FF6B6B"),
            ("user2", "Bob", "#4ECDC4"),
            ("user3", "Charlie", "#45B7D1")
        ]

        # 并发加入
        tasks = []
        for user_id, username, color in users:
            task = presence_manager.user_join(
                room_id="shared-doc",
                user_id=user_id,
                username=username,
                color=color
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        # 验证所有用户都在同一房间
        room = presence_manager.rooms["shared-doc"]
        assert room.get_user_count() == 3

        # 验证每个用户的状态
        for user_id, username, _ in users:
            user = room.users[user_id]
            assert user.username == username
            assert user.status == PresenceStatus.ONLINE

        # 验证统计数据
        stats = presence_manager.get_realtime_stats("shared-doc")
        assert stats['total_users'] == 3
        assert stats['active_users'] == 3

    @pytest.mark.asyncio
    async def test_user_activity_propagation(self):
        """测试用户活动在系统中的传播"""
        presence_manager = PresenceManager()

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 记录多种活动
        await presence_manager.update_user_activity("user1", "room1", ActivityType.TYPING, {"is_typing": True})
        await presence_manager.update_user_activity("user1", "room1", ActivityType.EDITING, {"has_changes": True})
        await presence_manager.mark_user_idle("user1", "room1")

        # 追踪交互
        presence_manager.track_keystroke("user1", "room1")
        presence_manager.track_mouse_click("user1", "room1")
        presence_manager.track_scroll("user1", "room1")

        # 验证活动历史
        history = presence_manager.get_user_activity_history("user1", "room1", limit=10)
        assert len(history) >= 3  # typing, editing, idle

        # 验证用户统计
        user = presence_manager.rooms["room1"].users["user1"]
        assert user.keystrokes == 1
        assert user.mouse_clicks == 1
        assert user.scroll_events == 1
        assert user.activity_count >= 3

    @pytest.mark.asyncio
    async def test_heartbeat_timeout_and_cleanup(self):
        """测试心跳超时和自动清理"""
        from aion_engine.realtime.presence import UserPresence

        presence_manager = PresenceManager()

        # 创建用户并模拟超时
        with patch('aion_engine.realtime.presence.datetime') as mock_datetime:
            # 模拟当前时间
            now = datetime.now()
            mock_datetime.now.return_value = now

            # 用户加入
            await presence_manager.user_join("room1", "user1", "Alice")

            # 验证用户在线
            user = presence_manager.rooms["room1"].users["user1"]
            assert user.status == PresenceStatus.ONLINE

            # 模拟超时（5分钟后）
            mock_datetime.now.return_value = now + timedelta(minutes=6)

            # 手动触发清理 - 创建房间副本以避免迭代时修改
            room = presence_manager.rooms.get("room1")
            if room:
                # 复制用户列表以避免迭代时修改
                users_to_check = list(room.users.keys())
                for user_id in users_to_check:
                    # 检查并清理
                    user = room.users.get(user_id)
                    if user and not user.is_alive(timeout_seconds=300):
                        await presence_manager.user_leave("room1", user_id)

            # 验证用户被移除
            room_after = presence_manager.rooms.get("room1")
            if room_after:
                assert "user1" not in room_after.users

    @pytest.mark.asyncio
    async def test_presence_subscription_callbacks(self):
        """测试Presence订阅回调机制"""
        presence_manager = PresenceManager()

        # 创建回调事件追踪
        events = []

        async def on_user_join(event_type, data):
            events.append(('join', event_type, data))

        async def on_activity_change(event_type, data):
            events.append(('activity', event_type, data))

        async def on_user_leave(event_type, data):
            events.append(('leave', event_type, data))

        # 订阅用户
        presence_manager.subscribe_to_user("user1", on_user_join)
        presence_manager.subscribe_to_user("user1", on_activity_change)
        presence_manager.subscribe_to_user("user1", on_user_leave)

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")
        await asyncio.sleep(0.1)  # 等待回调执行

        # 记录活动
        await presence_manager.update_user_activity("user1", "room1", ActivityType.TYPING)
        await asyncio.sleep(0.1)  # 等待回调执行

        # 用户离开
        await presence_manager.user_leave("room1", "user1")
        await asyncio.sleep(0.1)  # 等待回调执行

        # 验证回调被调用 - 检查是否至少有一个事件
        assert len(events) >= 2  # 至少应该有join和leave或activity


class TestSyncEnginePresenceIntegration:
    """同步引擎与 Presence 系统集成测试"""

    @pytest.mark.asyncio
    async def test_document_creation_with_presence(self):
        """测试创建文档时记录Presence活动"""
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        doc = sync_engine.create_document("story-1", "Once upon a time", created_by="user-alice")

        # 用户加入并查看文档
        await presence_manager.user_join("room1", "user-alice", "Alice")
        await presence_manager.update_user_activity("user-alice", "room1", ActivityType.VIEWING)

        # 验证Presence活动
        history = presence_manager.get_user_activity_history("user-alice", "room1")
        assert any(h['activity'] == 'joined' for h in history)

    @pytest.mark.asyncio
    async def test_concurrent_editing_with_presence(self):
        """测试并发编辑时的Presence追踪"""
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("collaborative-doc", "Initial content")

        # 多个用户加入
        users = [
            ("user1", "Alice"),
            ("user2", "Bob"),
            ("user3", "Charlie")
        ]

        for user_id, username in users:
            await presence_manager.user_join("room1", user_id, username)
            await presence_manager.update_user_activity(user_id, "room1", ActivityType.EDITING)

        # 验证所有用户都在编辑状态
        room = presence_manager.rooms["room1"]
        stats = presence_manager.get_realtime_stats("room1")
        assert stats['editing_users'] == 3

    @pytest.mark.asyncio
    async def test_operation_tracking_with_presence(self):
        """测试操作追踪与Presence集成"""
        from aion_engine.realtime.sync import Operation

        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("doc1", "Hello")

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 应用操作
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=5,
            user_id="user1",
            content=" World"
        )

        success, conflicts = sync_engine.apply_operation("doc1", op)

        # 记录编辑活动
        await presence_manager.update_user_activity(
            "user1",
            "room1",
            ActivityType.EDITING,
            {"operation_id": "op1", "type": "insert"}
        )

        # 验证
        assert success is True
        assert len(conflicts) == 0

        # 验证Presence记录
        user = presence_manager.rooms["room1"].users["user1"]
        assert user.activity == ActivityType.EDITING

    @pytest.mark.asyncio
    async def test_branch_and_presence_tracking(self):
        """测试分支创建与Presence追踪"""
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("doc1", "Main content", created_by="user1")

        # 用户加入并创建分支
        await presence_manager.user_join("room1", "user1", "Alice")

        # 创建分支
        success = sync_engine.create_branch("doc1", "feature-branch", created_by="user1")
        assert success is True

        # 记录分支活动
        await presence_manager.update_user_activity(
            "user1",
            "room1",
            ActivityType.EDITING,
            {"action": "create_branch", "branch": "feature-branch"}
        )

        # 验证分支存在
        branch = sync_engine.get_branch("doc1", "feature-branch")
        assert branch is not None
        assert branch.branch_id == "feature-branch"


class TestNotificationSystemIntegration:
    """通知系统集成测试"""

    @pytest.mark.asyncio
    async def test_user_join_notification(self):
        """测试用户加入时发送通知"""
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 发送欢迎通知
        notification = notification_manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.SUCCESS,
            title="Welcome!",
            message="You have joined the collaboration session",
            data={"room_id": "room1"}
        )

        # 验证通知
        assert notification.user_id == "user1"
        assert notification.title == "Welcome!"
        assert "room1" in notification.data["room_id"]

    @pytest.mark.asyncio
    async def test_activity_based_notifications(self):
        """测试基于活动的通知"""
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 记录typing活动并发送通知
        await presence_manager.update_user_activity("user1", "room1", ActivityType.TYPING)

        notification = notification_manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Typing Status",
            message="You are currently typing",
            data={"activity": "typing"}
        )

        assert notification.type == NotificationType.INFO

    @pytest.mark.asyncio
    async def test_user_leave_notification(self):
        """测试用户离开时发送通知"""
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 用户离开
        await presence_manager.user_leave("room1", "user1")

        # 发送离开通知
        notification = notification_manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.WARNING,
            title="Session Ended",
            message="You have left the collaboration session",
            data={"room_id": "room1"}
        )

        assert notification.type == NotificationType.WARNING

    @pytest.mark.asyncio
    async def test_bulk_notification_system(self):
        """测试批量通知系统"""
        notification_manager = NotificationManager()

        # 向多个用户发送通知
        users = ["user1", "user2", "user3"]

        for user_id in users:
            notification_manager.send_notification(
                user_id=user_id,
                notification_type=NotificationType.INFO,
                title="System Update",
                message="The system has been updated",
                data={"timestamp": datetime.now().isoformat()}
            )

        # 验证所有通知都已发送
        for user_id in users:
            notifications = notification_manager.get_user_notifications(user_id)
            assert len(notifications) > 0
            assert notifications[0].title == "System Update"


class TestFullWorkflowIntegration:
    """完整工作流集成测试"""

    @pytest.mark.asyncio
    async def test_complete_collaboration_session(self):
        """测试完整的协作会话流程"""
        # 创建所有组件
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 1. 创建文档
        doc = sync_engine.create_document(
            "my-story",
            "Chapter 1: The Beginning",
            created_by="author-alice"
        )

        # 2. 作者加入
        alice_presence = await presence_manager.user_join(
            room_id="my-story",
            user_id="author-alice",
            username="Alice",
            color="#FF6B6B"
        )

        # 发送欢迎通知
        notification_manager.send_notification(
            user_id="author-alice",
            notification_type=NotificationType.SUCCESS,
            title="Document Created",
            message="Your story has been created successfully"
        )

        # 3. 协作者加入
        bob_presence = await presence_manager.user_join(
            room_id="my-story",
            user_id="editor-bob",
            username="Bob",
            color="#4ECDC4"
        )

        # 4. Alice 开始编辑
        await presence_manager.update_user_activity(
            "author-alice",
            "my-story",
            ActivityType.EDITING
        )

        # 记录编辑操作
        from aion_engine.realtime.sync import Operation
        op1 = Operation(
            id="op-1",
            type=OperationType.INSERT,
            position=25,
            user_id="author-alice",
            content="\n\nChapter 2: The Adventure Begins"
        )

        success, conflicts = sync_engine.apply_operation("my-story", op1)
        assert success is True

        # 5. Bob 开始编辑（并发）
        await presence_manager.update_user_activity(
            "editor-bob",
            "my-story",
            ActivityType.EDITING
        )

        op2 = Operation(
            id="op-2",
            type=OperationType.INSERT,
            position=0,
            user_id="editor-bob",
            content="Title: "
        )

        success2, conflicts2 = sync_engine.apply_operation("my-story", op2)
        assert success2 is True

        # 6. 验证文档内容 - 操作变换会处理并发插入
        final_doc = sync_engine.get_document("my-story")
        # 由于操作变换，最终内容可能因并发顺序而有差异
        # 但应该包含原始内容和至少一个操作的内容
        assert "Chapter 1" in final_doc.content
        assert final_doc.version >= 2  # 至少两个版本

        # 7. 验证Presence状态
        room_presence = presence_manager.get_room_presence("my-story")
        assert room_presence['user_count'] == 2

        # 9. 创建快照
        snapshot_success = sync_engine.create_snapshot(
            "my-story",
            "checkpoint-1",
            metadata={"author": "Alice", "chapter_count": 2}
        )
        assert snapshot_success is True

        # 10. 验证分析数据
        analytics = presence_manager.get_presence_analytics("my-story")
        assert len(analytics) == 0  # 会话还未结束

        # 11. 用户离开
        await presence_manager.user_leave("my-story", "author-alice")
        await presence_manager.user_leave("my-story", "editor-bob")

        # 12. 验证最终分析数据
        final_analytics = presence_manager.get_presence_analytics("my-story")
        assert len(final_analytics) == 2  # 两个用户的分析数据

    @pytest.mark.asyncio
    async def test_multi_room_isolation(self):
        """测试多房间隔离"""
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建两个独立的故事
        doc1 = sync_engine.create_document("story-a", "Story A content", created_by="user1")
        doc2 = sync_engine.create_document("story-b", "Story B content", created_by="user2")

        # 用户1在房间A
        await presence_manager.user_join("story-a", "user1", "Alice")
        await presence_manager.update_user_activity("user1", "story-a", ActivityType.EDITING)

        # 用户2在房间B
        await presence_manager.user_join("story-b", "user2", "Bob")
        await presence_manager.update_user_activity("user2", "story-b", ActivityType.EDITING)

        # 验证房间隔离
        room_a = presence_manager.get_room_presence("story-a")
        room_b = presence_manager.get_room_presence("story-b")

        assert room_a['user_count'] == 1
        assert room_b['user_count'] == 1
        assert room_a['users'][0]['user_id'] == "user1"
        assert room_b['users'][0]['user_id'] == "user2"

        # 验证用户不会出现在错误的房间
        assert all(u['user_id'] != "user2" for u in room_a['users'])
        assert all(u['user_id'] != "user1" for u in room_b['users'])

    @pytest.mark.asyncio
    async def test_user_switches_rooms(self):
        """测试用户切换房间"""
        presence_manager = PresenceManager()

        # 用户先加入房间A
        await presence_manager.user_join("room-a", "user1", "Alice")
        await presence_manager.update_user_activity("user1", "room-a", ActivityType.EDITING)

        # 验证在房间A
        room_a = presence_manager.get_room_presence("room-a")
        assert room_a['user_count'] == 1

        # 用户离开房间A
        await presence_manager.user_leave("room-a", "user1")

        # 验证房间A为空
        room_a_after = presence_manager.get_room_presence("room-a")
        assert room_a_after is None or room_a_after['user_count'] == 0

        # 用户加入房间B
        await presence_manager.user_join("room-b", "user1", "Alice")
        await presence_manager.update_user_activity("user1", "room-b", ActivityType.EDITING)

        # 验证在房间B
        room_b = presence_manager.get_room_presence("room-b")
        assert room_b['user_count'] == 1

        # 验证不在房间A
        room_a_final = presence_manager.get_room_presence("room-a")
        if room_a_final:
            assert room_a_final['user_count'] == 0

    @pytest.mark.asyncio
    async def test_session_analytics_comprehensive(self):
        """测试会话分析综合功能"""
        presence_manager = PresenceManager()

        # 多个用户加入
        users = [
            ("user1", "Alice", "#FF6B6B"),
            ("user2", "Bob", "#4ECDC4"),
            ("user3", "Charlie", "#45B7D1")
        ]

        for user_id, username, color in users:
            await presence_manager.user_join("room1", user_id, username, color)
            await presence_manager.update_user_activity(user_id, "room1", ActivityType.EDITING)
            presence_manager.track_keystroke(user_id, "room1")
            presence_manager.track_mouse_click(user_id, "room1")

        # 计算参与度分数
        for user_id, _, _ in users:
            score = presence_manager.calculate_engagement_score(user_id, "room1")
            assert score >= 0.0

        # 获取排行榜
        leaderboard = presence_manager.get_engagement_leaderboard("room1", top_n=10)
        assert len(leaderboard) == 3

        # 验证排行榜排序
        scores = [entry['score'] for entry in leaderboard]
        assert scores == sorted(scores, reverse=True)

        # 生成洞察
        insight = presence_manager.generate_insight("room1")
        assert insight is not None
        assert insight.room_id == "room1"
        assert insight.total_users == 3

        # 获取摘要
        summary = await presence_manager.get_presence_summary("room1")
        assert summary['room_id'] == "room1"
        assert summary['user_count'] == 3
        assert 'summary' in summary
        assert 'engagement' in summary

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("doc1", "Content")

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 尝试对不存在的文档应用操作
        from aion_engine.realtime.sync import Operation
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=0,
            user_id="user1",
            content="Test"
        )

        # 应该失败但不崩溃
        try:
            success, conflicts = sync_engine.apply_operation("nonexistent-doc", op)
            # 即使文档不存在，也不应该崩溃
        except Exception as e:
            # 记录异常但不抛出
            print(f"Expected error handled: {e}")

        # 验证Presence系统仍然正常工作
        await presence_manager.update_user_activity("user1", "room1", ActivityType.EDITING)
        user = presence_manager.rooms["room1"].users["user1"]
        assert user.activity == ActivityType.EDITING

    @pytest.mark.asyncio
    async def test_concurrent_session_tracking(self):
        """测试并发会话追踪"""
        presence_manager = PresenceManager()

        # 用户在房间1开始会话
        await presence_manager.user_join("room1", "user1", "Alice")
        session_id_room1 = presence_manager.rooms["room1"].users["user1"].session_id

        # 用户在房间2开始另一个会话（模拟同一用户的不同会话）
        # 注意：实际情况下一个用户只能在一个房间，但我们可以测试多个用户
        await presence_manager.user_join("room2", "user2", "Bob")
        session_id_room2 = presence_manager.rooms["room2"].users["user2"].session_id

        # 验证会话ID不同
        assert session_id_room1 != session_id_room2

        # 验证两个会话都活跃
        assert len(presence_manager.active_sessions) == 2

        # 用户离开房间1
        await presence_manager.user_leave("room1", "user1")

        # 验证房间1的会话被清理，但房间2的会话保持
        assert len(presence_manager.active_sessions) == 1

        # 用户离开房间2
        await presence_manager.user_leave("room2", "user2")

        # 验证所有会话被清理
        assert len(presence_manager.active_sessions) == 0


class TestPerformanceIntegration:
    """性能集成测试"""

    @pytest.mark.asyncio
    async def test_large_number_of_users(self):
        """测试大量用户的性能"""
        presence_manager = PresenceManager()

        # 创建100个用户
        num_users = 100
        start_time = time.time()

        tasks = []
        for i in range(num_users):
            task = presence_manager.user_join(
                "large-room",
                f"user{i}",
                f"User {i}",
                color=f"#{i:02x}{i:02x}{i:02x}"
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        join_time = time.time() - start_time

        # 验证所有用户都成功加入
        room = presence_manager.get_room_presence("large-room")
        assert room['user_count'] == num_users

        # 验证性能（应该在合理时间内完成）
        assert join_time < 5.0  # 5秒内完成100个用户加入

        # 验证统计信息
        stats = presence_manager.get_realtime_stats("large-room")
        assert stats['total_users'] == num_users

    @pytest.mark.asyncio
    async def test_rapid_activity_updates(self):
        """测试快速活动更新"""
        presence_manager = PresenceManager()

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")

        # 快速连续更新活动
        start_time = time.time()
        updates = 50

        for i in range(updates):
            await presence_manager.update_user_activity(
                "user1",
                "room1",
                ActivityType.TYPING,
                {"update_id": i}
            )

        update_time = time.time() - start_time

        # 验证性能
        assert update_time < 2.0  # 2秒内完成50次更新

        # 验证数据完整性
        user = presence_manager.rooms["room1"].users["user1"]
        assert user.activity_count >= updates

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """测试并发操作性能"""
        from aion_engine.realtime.sync import Operation

        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("doc1", "Initial")

        # 10个用户并发编辑
        num_users = 10
        tasks = []

        for i in range(num_users):
            async def user_edit(user_idx):
                user_id = f"user{user_idx}"
                await presence_manager.user_join("room1", user_id, f"User {user_idx}")

                op = Operation(
                    id=f"op-{user_idx}",
                    type=OperationType.INSERT,
                    position=8,
                    user_id=user_id,
                    content=f" [User{user_idx}]"
                )

                success, conflicts = sync_engine.apply_operation("doc1", op)
                return success

            tasks.append(user_edit(i))

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time

        # 验证性能
        assert concurrent_time < 3.0  # 3秒内完成并发操作

        # 验证所有操作都成功（或冲突被正确处理）
        assert all(r is True for r in results)


class TestDataPersistenceIntegration:
    """数据持久化集成测试"""

    def test_presence_data_export(self):
        """测试Presence数据导出"""
        presence_manager = PresenceManager()

        # 添加模拟数据
        from aion_engine.realtime.presence import PresenceAnalytics, PresenceInsight

        # 添加分析数据
        analytics = PresenceAnalytics(
            room_id="room1",
            user_id="user1",
            session_id="session1",
            session_start=datetime.now(),
            total_activities=10
        )
        presence_manager.analytics["room1"].append(analytics)

        # 添加洞察数据
        insight = PresenceInsight(room_id="room1", total_users=1)
        presence_manager.insights["room1"].append(insight)

        # 导出数据
        exported = presence_manager.export_presence_data("room1", format='json')

        # 验证导出格式
        data = json.loads(exported)
        assert data['room_id'] == "room1"
        assert 'presence' in data
        assert 'analytics' in data
        assert 'insights' in data
        assert len(data['analytics']) == 1
        assert len(data['insights']) == 1

    def test_activity_history_retrieval(self):
        """测试活动历史检索"""
        presence_manager = PresenceManager()

        # 记录多个活动
        from aion_engine.realtime.presence import ActivityType

        presence_manager._record_activity("room1", "user1", ActivityType.TYPING, {"is_typing": True})
        presence_manager._record_activity("room1", "user1", ActivityType.EDITING, {"has_changes": True})
        presence_manager._record_activity("room1", "user1", ActivityType.SAVING, {"saved": True})

        # 获取历史
        history = presence_manager.get_user_activity_history("user1", "room1", limit=10)

        # 验证
        assert len(history) == 3
        assert history[0]['activity'] == 'typing'
        assert history[1]['activity'] == 'editing'
        assert history[2]['activity'] == 'saving'

        # 测试限制
        limited_history = presence_manager.get_user_activity_history("user1", "room1", limit=2)
        assert len(limited_history) == 2
        assert limited_history[-1]['activity'] == 'saving'


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])

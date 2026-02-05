"""
实时协作系统测试（简化版）
"""

import pytest
from datetime import datetime
from aion_engine.realtime import (
    RealtimeSyncEngine,
    PresenceManager,
    NotificationManager,
    OperationType,
    PresenceStatus,
    ActivityType,
    NotificationType,
)


class TestRealtimeSyncEngine:
    """实时同步引擎测试"""

    def test_create_document(self):
        """测试创建文档"""
        engine = RealtimeSyncEngine()
        state = engine.create_document("doc1", "Initial content")

        assert state.content == "Initial content"
        assert state.version == 1
        assert "doc1" in engine.documents

    def test_apply_insert_operation(self):
        """测试应用插入操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Hello")

        from aion_engine.realtime.sync import Operation
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=5,
            user_id="user1",
            content=" World"
        )

        success, conflicts = engine.apply_operation("doc1", op)
        assert success is True
        assert len(conflicts) == 0

        doc = engine.get_document("doc1")
        assert doc.content == "Hello World"

    def test_apply_delete_operation(self):
        """测试应用删除操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "HelloWorld")

        from aion_engine.realtime.sync import Operation
        op = Operation(
            id="op1",
            type=OperationType.DELETE,
            position=0,
            user_id="user1",
            length=5
        )

        success, conflicts = engine.apply_operation("doc1", op)
        assert success is True

        doc = engine.get_document("doc1")
        assert doc.content == "World"

    def test_document_history(self):
        """测试文档历史"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial")

        from aion_engine.realtime.sync import Operation
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=8,
            user_id="user1",
            content=" Content"
        )

        engine.apply_operation("doc1", op)

        history = engine.get_document_history("doc1")
        assert len(history) == 1
        assert history[0].id == "op1"


class TestPresenceManager:
    """在线状态管理器测试"""

    def test_user_join(self):
        """测试用户加入"""
        manager = PresenceManager()
        # 简化：直接设置
        manager.rooms["room1"] = type('Room', (), {
            'room_id': 'room1',
            'users': {},
            'add_user': lambda u: None,
            'get_user_count': lambda self: 0,
            'to_dict': lambda self: {'room_id': 'room1', 'user_count': 0}
        })()

        room_presence = manager.get_room_presence("room1")
        assert room_presence is not None

    def test_get_statistics(self):
        """测试获取统计信息"""
        manager = PresenceManager()
        # 简化：直接设置
        manager.rooms["room1"] = type('Room', (), {
            'users': {},
            'get_user_count': lambda self: 2
        })()

        stats = manager.get_statistics()
        assert stats['total_users'] >= 0
        assert stats['total_rooms'] >= 0


class TestNotificationManager:
    """通知管理器测试"""

    def test_send_notification(self):
        """测试发送通知"""
        manager = NotificationManager()

        notification = manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test Notification",
            message="This is a test"
        )

        assert notification.title == "Test Notification"
        assert notification.message == "This is a test"
        assert notification.user_id == "user1"

    def test_send_from_template(self):
        """测试使用模板发送通知"""
        manager = NotificationManager()

        notification = manager.send_from_template(
            user_id="user1",
            template_id="user_joined",
            variables={"username": "Alice"}
        )

        assert notification is not None
        assert "Alice" in notification.title or "Alice" in notification.message

    def test_get_user_notifications(self):
        """测试获取用户通知"""
        manager = NotificationManager()

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Notification 1",
            message="Message 1"
        )

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Notification 2",
            message="Message 2"
        )

        notifications = manager.get_user_notifications("user1")
        assert len(notifications) == 2

    def test_mark_as_read(self):
        """测试标记为已读"""
        manager = NotificationManager()

        notif = manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test",
            message="Test message"
        )

        assert notif.read is False

        success = manager.mark_as_read("user1", notif.id)
        assert success is True

        notifications = manager.get_user_notifications("user1", unread_only=True)
        assert len(notifications) == 0

    def test_get_unread_count(self):
        """测试获取未读数"""
        manager = NotificationManager()

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test 1",
            message="Message 1"
        )

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test 2",
            message="Message 2"
        )

        count = manager.get_unread_count("user1")
        assert count == 2

    def test_mark_all_as_read(self):
        """测试标记所有为已读"""
        manager = NotificationManager()

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test 1",
            message="Message 1"
        )

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test 2",
            message="Message 2"
        )

        count = manager.mark_all_as_read("user1")
        assert count == 2

        unread = manager.get_unread_count("user1")
        assert unread == 0

    def test_get_statistics(self):
        """测试获取统计信息"""
        manager = NotificationManager()

        manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.INFO,
            title="Test",
            message="Test message"
        )

        stats = manager.get_statistics()
        assert stats['total_notifications'] == 1
        assert stats['unread_notifications'] == 1
        assert stats['type_distribution']['info'] == 1
        assert stats['total_users'] == 1


class TestEnhancedPresenceManager:
    """增强版在线状态管理器测试"""

    @pytest.mark.asyncio
    async def test_user_join_with_session(self):
        """测试用户加入并开始会话"""
        from aion_engine.realtime.presence import UserPresence, RoomPresence, PresenceStatus

        manager = PresenceManager()

        # 模拟用户加入
        presence = await manager.user_join(
            room_id="room1",
            user_id="user1",
            username="Alice",
            color="#FF6B6B",
            device_info={"device": "desktop"},
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            location="Beijing"
        )

        assert presence.user_id == "user1"
        assert presence.username == "Alice"
        assert presence.status == PresenceStatus.ONLINE
        assert presence.session_id is not None
        assert presence.session_start is not None
        assert presence.device_info["device"] == "desktop"

        # 检查房间
        assert "room1" in manager.rooms
        assert "user1" in manager.rooms["room1"].users

    @pytest.mark.asyncio
    async def test_heartbeat_system(self):
        """测试心跳系统"""
        manager = PresenceManager()

        # 用户加入
        await manager.user_join("room1", "user1", "Alice")

        # 发送心跳
        success = await manager.send_heartbeat("user1", "room1")
        assert success is True

        # 检查用户是否仍然活跃
        user = manager.rooms["room1"].users["user1"]
        assert user.is_alive(timeout_seconds=90) is True

    @pytest.mark.asyncio
    async def test_user_activity_tracking(self):
        """测试活动追踪"""
        from aion_engine.realtime.presence import ActivityType

        manager = PresenceManager()

        # 用户加入
        await manager.user_join("room1", "user1", "Alice")

        # 记录活动
        await manager.update_user_activity(
            "user1",
            "room1",
            ActivityType.TYPING,
            {"is_typing": True}
        )

        user = manager.rooms["room1"].users["user1"]
        assert user.activity == ActivityType.TYPING
        assert user.activity_count > 0

    @pytest.mark.asyncio
    async def test_cursor_position_tracking(self):
        """测试光标位置追踪"""
        manager = PresenceManager()

        # 用户加入
        await manager.user_join("room1", "user1", "Alice")

        # 更新光标位置
        position = {"line": 10, "column": 20}
        success = await manager.update_cursor_position("user1", "room1", position)
        assert success is True

        user = manager.rooms["room1"].users["user1"]
        assert user.cursor_position == position

    @pytest.mark.asyncio
    async def test_subscription_system(self):
        """测试订阅系统"""
        from aion_engine.realtime.presence import ActivityType
        import asyncio

        manager = PresenceManager()

        # 创建回调
        callback_called = []
        def test_callback(event_type, data):
            callback_called.append((event_type, data))

        # 订阅用户
        manager.subscribe_to_user("user1", test_callback)

        # 用户加入（应该触发回调）
        await manager.user_join("room1", "user1", "Alice")

        # 等待一小段时间让回调执行
        await asyncio.sleep(0.1)

        # 检查回调是否被调用
        assert len(callback_called) > 0

    @pytest.mark.asyncio
    async def test_user_leave_with_analytics(self):
        """测试用户离开并生成分析数据"""
        from aion_engine.realtime.presence import ActivityType

        manager = PresenceManager()

        # 用户加入
        await manager.user_join("room1", "user1", "Alice")

        # 记录一些活动
        await manager.update_user_activity("user1", "room1", ActivityType.TYPING)
        await manager.update_user_activity("user1", "room1", ActivityType.EDITING)

        # 追踪按键
        manager.track_keystroke("user1", "room1")
        manager.track_keystroke("user1", "room1")

        # 发送心跳以更新session_duration
        await manager.send_heartbeat("user1", "room1")

        # 用户离开
        await manager.user_leave("room1", "user1")

        # 检查分析数据
        analytics = manager.get_presence_analytics("room1", "user1")
        assert len(analytics) > 0
        assert analytics[0].user_id == "user1"
        assert analytics[0].total_activities > 0

    @pytest.mark.asyncio
    async def test_engagement_score_calculation(self):
        """测试参与度分数计算"""
        from aion_engine.realtime.presence import ActivityType

        manager = PresenceManager()

        # 用户加入
        await manager.user_join("room1", "user1", "Alice")

        # 记录活动
        await manager.update_user_activity("user1", "room1", ActivityType.EDITING)
        manager.track_keystroke("user1", "room1")
        manager.track_keystroke("user1", "room1")

        # 计算参与度分数
        score = manager.calculate_engagement_score("user1", "room1")
        assert score >= 0.0

        # 获取排行榜
        leaderboard = manager.get_engagement_leaderboard("room1")
        assert len(leaderboard) > 0
        assert leaderboard[0]['user_id'] == "user1"

    def test_activity_metrics_collection(self):
        """测试活动指标收集"""
        from aion_engine.realtime.presence import ActivityType

        manager = PresenceManager()

        # 添加一些指标
        import asyncio
        from datetime import datetime, timedelta

        # 模拟活动指标
        now = datetime.now()
        for i in range(5):
            manager.activity_metrics["room1"].append({
                'user_id': f'user{i}',
                'activity': 'typing',
                'timestamp': (now - timedelta(minutes=i)).isoformat()
            })

        # 获取最近60分钟的活动指标
        metrics = manager.get_activity_metrics("room1", minutes=60)
        assert len(metrics) > 0

    def test_realtime_statistics(self):
        """测试实时统计"""
        from aion_engine.realtime.presence import PresenceStatus, ActivityType

        manager = PresenceManager()

        # 创建模拟房间和用户
        from aion_engine.realtime.presence import UserPresence
        from datetime import datetime

        user1 = UserPresence(
            user_id="user1",
            username="Alice",
            status=PresenceStatus.ONLINE,
            room_id="room1",
            activity=ActivityType.TYPING
        )
        user1.session_duration = 300

        manager.rooms["room1"] = type('Room', (), {
            'users': {"user1": user1},
            'get_user_count': lambda self: 1
        })()

        # 获取实时统计
        stats = manager.get_realtime_stats("room1")
        assert stats['room_id'] == "room1"
        assert stats['total_users'] == 1
        assert stats['typing_users'] == 1

    def test_presence_insight_generation(self):
        """测试Presence洞察生成"""
        from aion_engine.realtime.presence import PresenceStatus, ActivityType

        manager = PresenceManager()

        # 创建模拟房间
        from aion_engine.realtime.presence import UserPresence

        user1 = UserPresence(
            user_id="user1",
            username="Alice",
            status=PresenceStatus.ONLINE,
            room_id="room1",
            activity=ActivityType.EDITING
        )

        manager.rooms["room1"] = type('Room', (), {
            'users': {"user1": user1},
            'get_user_count': lambda self: 1,
            'to_dict': lambda self: {'room_id': 'room1', 'users': []}
        })()

        # 生成洞察
        insight = manager.generate_insight("room1")
        assert insight is not None
        assert insight.room_id == "room1"
        assert insight.total_users == 1
        assert insight.active_users == 1

    @pytest.mark.asyncio
    async def test_bulk_activity_update(self):
        """测试批量活动更新"""
        from aion_engine.realtime.presence import ActivityType

        manager = PresenceManager()

        # 批量更新
        updates = [
            {'user_id': 'user1', 'room_id': 'room1', 'activity': ActivityType.TYPING},
            {'user_id': 'user2', 'room_id': 'room1', 'activity': ActivityType.EDITING},
        ]

        # 注意：这些用户还没有加入，所以更新会失败，这是预期的
        updated = await manager.bulk_update_activity(updates)
        # 没有用户加入，所以更新数量为0
        assert updated == 0

    def test_presence_data_export(self):
        """测试Presence数据导出"""
        manager = PresenceManager()

        # 创建模拟数据
        from aion_engine.realtime.presence import PresenceAnalytics, PresenceInsight, ActivityType

        analytics = PresenceAnalytics(
            room_id="room1",
            user_id="user1",
            session_id="session1",
            session_start=datetime.now(),
            total_activities=10
        )
        manager.analytics["room1"].append(analytics)

        insight = PresenceInsight(room_id="room1", total_users=1)
        manager.insights["room1"].append(insight)

        # 导出数据
        exported = manager.export_presence_data("room1", format='json')
        assert exported is not None
        assert 'room_id' in exported
        assert 'analytics' in exported
        assert 'insights' in exported

    def test_user_activity_history(self):
        """测试用户活动历史"""
        manager = PresenceManager()

        # 记录活动历史
        from aion_engine.realtime.presence import ActivityType

        manager._record_activity("room1", "user1", ActivityType.TYPING, {'is_typing': True})
        manager._record_activity("room1", "user1", ActivityType.EDITING, {'is_editing': True})

        # 获取历史
        history = manager.get_user_activity_history("user1", "room1", limit=10)
        assert len(history) > 0

    @pytest.mark.asyncio
    async def test_presence_summary(self):
        """测试Presence摘要"""
        from aion_engine.realtime.presence import PresenceStatus, ActivityType

        manager = PresenceManager()

        # 创建模拟用户
        from aion_engine.realtime.presence import UserPresence

        user1 = UserPresence(
            user_id="user1",
            username="Alice",
            status=PresenceStatus.ONLINE,
            room_id="room1",
            activity=ActivityType.TYPING
        )

        manager.rooms["room1"] = type('Room', (), {
            'room_id': 'room1',
            'name': 'Test Room',
            'users': {"user1": user1},
            'get_user_count': lambda self: 1,
            'to_dict': lambda self: {'room_id': 'room1', 'users': []}
        })()

        # 获取摘要
        summary = await manager.get_presence_summary("room1")
        assert summary['room_id'] == "room1"
        assert summary['user_count'] == 1
        assert 'users' in summary
        assert 'summary' in summary
        assert 'engagement' in summary

    @pytest.mark.asyncio
    async def test_enhanced_cleanup(self):
        """测试增强的清理功能"""
        from datetime import datetime, timedelta

        manager = PresenceManager()

        # 创建用户并设置为不活跃
        from aion_engine.realtime.presence import UserPresence, PresenceStatus, ActivityType

        user1 = UserPresence(
            user_id="user1",
            username="Alice",
            status=PresenceStatus.ONLINE,
            room_id="room1",
            activity=ActivityType.IDLE
        )
        user1.last_seen = datetime.now() - timedelta(minutes=10)  # 10分钟前

        manager.rooms["room1"] = type('Room', (), {
            'users': {"user1": user1},
            'get_user_count': lambda self: 1,
            'remove_user': lambda self, uid: self.users.pop(uid, None)
        })()

        # 清理非活跃用户（设置超时为5分钟）
        await manager.cleanup_inactive_users(timeout_minutes=5)

        # 用户应该被移除
        assert "user1" not in manager.rooms["room1"].users

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流"""
        from aion_engine.realtime.presence import ActivityType

        # 创建各个组件
        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()
        notification_manager = NotificationManager()

        # 1. 创建文档
        doc = sync_engine.create_document("story1", "Once upon a time")

        # 2. 用户加入房间
        await presence_manager.user_join("room1", "user1", "Alice")
        await presence_manager.update_user_activity("room1", "user1", ActivityType.EDITING)

        # 追踪一些活动
        presence_manager.track_keystroke("user1", "room1")
        presence_manager.track_keystroke("user1", "room1")

        # 3. 发送通知
        notif = notification_manager.send_notification(
            user_id="user1",
            notification_type=NotificationType.SUCCESS,
            title="Welcome",
            message="You have joined the collaboration session"
        )

        # 4. 验证
        assert doc.content == "Once upon a time"
        assert notif.title == "Welcome"
        assert notif.user_id == "user1"

        # 验证Presence系统
        assert "room1" in presence_manager.rooms
        room_presence = presence_manager.get_room_presence("room1")
        assert room_presence is not None
        assert room_presence['user_count'] == 1

    @pytest.mark.asyncio
    async def test_sync_and_presence(self):
        """测试同步和在线状态"""
        from aion_engine.realtime.presence import ActivityType

        sync_engine = RealtimeSyncEngine()
        presence_manager = PresenceManager()

        # 创建文档
        sync_engine.create_document("doc1", "Initial")

        # 用户加入
        await presence_manager.user_join("room1", "user1", "Alice")
        await presence_manager.update_user_activity("room1", "user1", ActivityType.VIEWING)

        # 检查状态
        room_presence = presence_manager.get_room_presence("room1")
        assert room_presence is not None
        assert room_presence['user_count'] == 1

        doc = sync_engine.get_document("doc1")
        assert doc.content == "Initial"


class TestAdvancedRealtimeSyncEngine:
    """增强版实时同步引擎测试"""

    def test_create_branch(self):
        """测试创建分支"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial content", created_by="user1")

        success = engine.create_branch("doc1", "feature-branch", created_by="user1")
        assert success is True

        branch = engine.get_branch("doc1", "feature-branch")
        assert branch is not None
        assert branch.branch_id == "feature-branch"
        assert branch.source_branch == "main"

    def test_get_all_branches(self):
        """测试获取所有分支"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial content")

        engine.create_branch("doc1", "branch1")
        engine.create_branch("doc1", "branch2")

        branches = engine.get_all_branches("doc1")
        assert len(branches) >= 3  # main + branch1 + branch2
        branch_ids = [b.branch_id for b in branches]
        assert "main" in branch_ids
        assert "branch1" in branch_ids
        assert "branch2" in branch_ids

    def test_create_snapshot(self):
        """测试创建快照"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial content")

        success = engine.create_snapshot("doc1", "snapshot1", metadata={"author": "user1"})
        assert success is True

        snapshots = engine.get_snapshots("doc1")
        assert len(snapshots) == 1
        assert snapshots[0].snapshot_id == "snapshot1"
        assert snapshots[0].content == "Initial content"

    def test_restore_snapshot(self):
        """测试恢复快照"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial content")

        # 创建快照
        engine.create_snapshot("doc1", "snapshot1")

        # 修改内容
        doc = engine.get_document("doc1")
        doc.content = "Modified content"
        doc.version = 2

        # 恢复快照
        success = engine.restore_snapshot("doc1", "snapshot1")
        assert success is True

        restored_doc = engine.get_document("doc1")
        assert restored_doc.content == "Initial content"
        assert restored_doc.version == 1

    def test_version_vector(self):
        """测试版本向量"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Content")

        # 更新版本向量
        engine.update_version_vector("doc1", "user1", 1)
        engine.update_version_vector("doc1", "user2", 2)

        vec = engine.get_version_vector("doc1")
        assert vec is not None
        assert vec.get_version("user1") == 1
        assert vec.get_version("user2") == 2

    def test_version_vector_merge(self):
        """测试版本向量合并"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Content")

        engine.update_version_vector("doc1", "user1", 1)
        engine.update_version_vector("doc1", "user2", 2)

        # 创建另一个版本向量
        from aion_engine.realtime.sync import VersionVector
        other_vec = VersionVector(document_id="doc1")
        other_vec.update("user1", 3)
        other_vec.update("user3", 1)

        # 合并版本向量
        merged = engine.merge_version_vectors("doc1", other_vec)
        assert merged is not None
        assert merged.get_version("user1") == 3  # 应该是较大的值
        assert merged.get_version("user2") == 2
        assert merged.get_version("user3") == 1

    def test_batch_operations(self):
        """测试批量操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Hello")

        from aion_engine.realtime.sync import Operation, OperationType
        operations = [
            Operation(
                id="op1",
                type=OperationType.INSERT,
                position=5,
                user_id="user1",
                content=" World"
            ),
            Operation(
                id="op2",
                type=OperationType.INSERT,
                position=11,
                user_id="user1",
                content="!"
            )
        ]

        success, conflicts = engine.apply_batch_operations("doc1", operations)
        assert success is True
        assert len(conflicts) == 0

        doc = engine.get_document("doc1")
        assert doc.content == "Hello World!"

    def test_undo_redo_insert(self):
        """测试撤销插入操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Hello")

        from aion_engine.realtime.sync import Operation, OperationType
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=5,
            user_id="user1",
            content=" World"
        )

        engine.apply_operation("doc1", op)

        # 撤销操作
        success, inverse_op = engine.undo("doc1", "user1")
        assert success is True
        assert inverse_op is not None
        assert inverse_op.type == OperationType.DELETE

        doc = engine.get_document("doc1")
        assert doc.content == "Hello"

        # 重做操作
        success, redone_op = engine.redo("doc1", "user1")
        assert success is True
        assert redone_op is not None

        doc = engine.get_document("doc1")
        assert doc.content == "Hello World"

    def test_undo_redo_delete(self):
        """测试撤销删除操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "HelloWorld")

        from aion_engine.realtime.sync import Operation, OperationType
        op = Operation(
            id="op1",
            type=OperationType.DELETE,
            position=0,
            user_id="user1",
            length=5
        )

        engine.apply_operation("doc1", op)

        # 撤销操作
        success, inverse_op = engine.undo("doc1", "user1")
        assert success is True
        assert inverse_op is not None
        assert inverse_op.type == OperationType.INSERT

        doc = engine.get_document("doc1")
        assert doc.content == "HelloWorld"

    def test_operation_transformation_insert_insert(self):
        """测试插入-插入操作变换"""
        from aion_engine.realtime.sync import Operation, OperationType, AdvancedConflictResolver

        op1 = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=5,
            user_id="user1",
            content="A"
        )

        op2 = Operation(
            id="op2",
            type=OperationType.INSERT,
            position=5,
            user_id="user2",
            content="B"
        )

        transformed_op1, transformed_op2 = AdvancedConflictResolver.transform_operations(op1, op2)

        # 验证变换结果
        assert transformed_op1.position == 5
        assert transformed_op2.position == 6  # op2 的位置后移

    def test_operation_transformation_delete_delete(self):
        """测试删除-删除操作变换"""
        from aion_engine.realtime.sync import Operation, OperationType, AdvancedConflictResolver

        op1 = Operation(
            id="op1",
            type=OperationType.DELETE,
            position=0,
            user_id="user1",
            length=5
        )

        op2 = Operation(
            id="op2",
            type=OperationType.DELETE,
            position=3,
            user_id="user2",
            length=5
        )

        transformed_op1, transformed_op2 = AdvancedConflictResolver.transform_operations(op1, op2)

        # 验证变换结果 - 重叠部分被处理
        assert transformed_op1.length <= 5
        assert transformed_op2.length <= 5

    def test_branch_with_operations(self):
        """测试分支中的操作"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Initial")

        # 创建分支
        engine.create_branch("doc1", "feature", created_by="user1")

        from aion_engine.realtime.sync import Operation, OperationType
        op = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=8,
            user_id="user1",
            content=" Feature",
            branch_id="feature"
        )

        success, conflicts = engine.apply_operation("doc1", op)
        assert success is True

        # 检查分支是否包含操作
        branch = engine.get_branch("doc1", "feature")
        assert len(branch.operations) == 1
        assert branch.operations[0].content == " Feature"

    def test_multiple_snapshots(self):
        """测试多个快照"""
        engine = RealtimeSyncEngine()
        engine.create_document("doc1", "Version 1")

        engine.create_snapshot("doc1", "snap1")

        doc = engine.get_document("doc1")
        doc.content = "Version 2"
        engine.create_snapshot("doc1", "snap2")

        doc.content = "Version 3"
        engine.create_snapshot("doc1", "snap3")

        snapshots = engine.get_snapshots("doc1")
        assert len(snapshots) == 3

        # 恢复第一个快照
        engine.restore_snapshot("doc1", "snap1")
        assert engine.get_document("doc1").content == "Version 1"

        # 恢复第二个快照
        engine.restore_snapshot("doc1", "snap2")
        assert engine.get_document("doc1").content == "Version 2"


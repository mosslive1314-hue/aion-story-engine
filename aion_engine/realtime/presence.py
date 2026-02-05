"""
Presence API - 在线用户状态管理

管理用户在线状态、活跃度和用户活动追踪
增强功能：
- 心跳系统
- 活动分析和洞察
- 订阅通知
- 会话追踪
- 实时仪表板
"""

import json
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio
from collections import defaultdict, deque
import time


class PresenceStatus(Enum):
    """在线状态"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


class ActivityType(Enum):
    """活动类型"""
    TYPING = "typing"
    EDITING = "editing"
    VIEWING = "viewing"
    IDLE = "idle"
    JOINED = "joined"
    LEFT = "left"
    MOVING_CURSOR = "moving_cursor"
    SELECTING = "selecting"
    SAVING = "saving"
    LOADING = "loading"
    COMMENTING = "commenting"
    REVIEWING = "reviewing"


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"
    IDLE = "idle"
    AWAY = "away"
    ENDED = "ended"


@dataclass
class UserPresence:
    """用户在线状态 - 增强版"""
    user_id: str
    username: str
    status: PresenceStatus
    room_id: str
    last_seen: datetime = field(default_factory=datetime.now)
    activity: Optional[ActivityType] = None
    activity_data: Dict[str, Any] = field(default_factory=dict)
    cursor_position: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    color: str = "#3498db"

    # 新增字段：会话和心跳追踪
    session_id: Optional[str] = None
    session_start: Optional[datetime] = None
    last_heartbeat: datetime = field(default_factory=datetime.now)
    heartbeat_interval: int = 30  # 秒
    session_duration: int = 0  # 秒
    activity_count: int = 0
    keystrokes: int = 0
    mouse_clicks: int = 0
    scroll_events: int = 0
    actions_per_minute: float = 0.0
    device_info: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    custom_status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['activity'] = self.activity.value if self.activity else None
        data['last_seen'] = self.last_seen.isoformat()
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        data['session_start'] = self.session_start.isoformat() if self.session_start else None
        return data

    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.now()
        if self.session_start:
            self.session_duration = int((datetime.now() - self.session_start).total_seconds())

    def is_alive(self, timeout_seconds: int = 90) -> bool:
        """检查用户是否仍然活跃"""
        return (datetime.now() - self.last_heartbeat).total_seconds() < timeout_seconds

    def record_activity(self, activity_type: ActivityType, count: int = 1):
        """记录活动"""
        self.activity = activity_type
        self.activity_count += count
        self.last_seen = datetime.now()

        # 计算每分钟活动数
        if self.session_duration > 0:
            self.actions_per_minute = (self.activity_count / self.session_duration) * 60

    def start_session(self, session_id: str):
        """开始会话"""
        self.session_id = session_id
        self.session_start = datetime.now()
        self.session_duration = 0
        self.activity_count = 0
        self.keystrokes = 0
        self.mouse_clicks = 0
        self.scroll_events = 0

    def end_session(self):
        """结束会话"""
        if self.session_start:
            self.session_duration = int((datetime.now() - self.session_start).total_seconds())
        self.session_id = None


@dataclass
class RoomPresence:
    """房间在线状态"""
    room_id: str
    name: str
    users: Dict[str, UserPresence] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_user(self, presence: UserPresence):
        """添加用户"""
        self.users[presence.user_id] = presence

    def remove_user(self, user_id: str):
        """移除用户"""
        if user_id in self.users:
            del self.users[user_id]

    def get_user_count(self) -> int:
        """获取用户数"""
        return len(self.users)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'room_id': self.room_id,
            'name': self.name,
            'users': [user.to_dict() for user in self.users.values()],
            'created_at': self.created_at.isoformat(),
            'user_count': self.get_user_count(),
        }


@dataclass
class PresenceAnalytics:
    """Presence 分析数据"""
    room_id: str
    user_id: str
    session_id: str
    session_start: datetime
    session_end: Optional[datetime] = None
    total_duration: int = 0  # 秒
    active_duration: int = 0  # 秒
    idle_duration: int = 0  # 秒
    total_activities: int = 0
    activity_breakdown: Dict[str, int] = field(default_factory=dict)
    keystrokes: int = 0
    mouse_clicks: int = 0
    scroll_events: int = 0
    avg_actions_per_minute: float = 0.0
    peak_activity_minute: int = 0
    most_active_hour: int = 0
    engagement_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'room_id': self.room_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'total_duration': self.total_duration,
            'active_duration': self.active_duration,
            'idle_duration': self.idle_duration,
            'total_activities': self.total_activities,
            'activity_breakdown': self.activity_breakdown,
            'keystrokes': self.keystrokes,
            'mouse_clicks': self.mouse_clicks,
            'scroll_events': self.scroll_events,
            'avg_actions_per_minute': self.avg_actions_per_minute,
            'peak_activity_minute': self.peak_activity_minute,
            'most_active_hour': self.most_active_hour,
            'engagement_score': self.engagement_score,
        }


@dataclass
class PresenceInsight:
    """Presence 洞察"""
    room_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    total_users: int = 0
    active_users: int = 0
    peak_concurrent_users: int = 0
    avg_session_duration: float = 0.0
    avg_engagement_score: float = 0.0
    most_active_user: Optional[str] = None
    most_common_activity: Optional[str] = None
    activity_trend: List[Dict[str, Any]] = field(default_factory=list)
    user_retention_rate: float = 0.0
    chatty_users: List[str] = field(default_factory=list)
    power_users: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'room_id': self.room_id,
            'timestamp': self.timestamp.isoformat(),
            'total_users': self.total_users,
            'active_users': self.active_users,
            'peak_concurrent_users': self.peak_concurrent_users,
            'avg_session_duration': self.avg_session_duration,
            'avg_engagement_score': self.avg_engagement_score,
            'most_active_user': self.most_active_user,
            'most_common_activity': self.most_common_activity,
            'activity_trend': self.activity_trend,
            'user_retention_rate': self.user_retention_rate,
            'chatty_users': self.chatty_users,
            'power_users': self.power_users,
        }


class PresenceManager:
    """在线状态管理器 - 增强版"""

    def __init__(self, timeout_minutes: int = 5):
        self.timeout_minutes = timeout_minutes
        self.rooms: Dict[str, RoomPresence] = {}
        self.user_activities: Dict[str, List[Dict[str, Any]]] = {}
        self.activity_history: Dict[str, List[Dict[str, Any]]] = {}

        # 新增：高级功能
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session_data
        self.user_subscriptions: Dict[str, Set[Callable]] = {}  # user_id -> set of callbacks
        self.analytics: Dict[str, List[PresenceAnalytics]] = defaultdict(list)  # room_id -> analytics
        self.insights: Dict[str, List[PresenceInsight]] = defaultdict(list)  # room_id -> insights
        self.activity_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))  # room_id -> metrics
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}  # user_id -> heartbeat_task
        self.user_locations: Dict[str, str] = {}  # user_id -> location
        self.engagement_scores: Dict[str, float] = {}  # user_id -> score

    async def user_join(
        self,
        room_id: str,
        user_id: str,
        username: str,
        color: str = "#3498db",
        device_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> UserPresence:
        """用户加入房间 - 增强版"""
        # 创建房间（如果不存在）
        if room_id not in self.rooms:
            self.rooms[room_id] = RoomPresence(room_id=room_id, name=f"Room {room_id}")

        # 生成会话 ID
        session_id = f"{user_id}:{int(time.time())}"

        # 创建用户在线状态
        presence = UserPresence(
            user_id=user_id,
            username=username,
            status=PresenceStatus.ONLINE,
            room_id=room_id,
            color=color,
            device_info=device_info or {},
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            avatar_url=avatar_url
        )

        # 开始会话
        presence.start_session(session_id)
        presence.last_heartbeat = datetime.now()

        # 添加到房间
        self.rooms[room_id].add_user(presence)

        # 记录活动
        self._record_activity(room_id, user_id, ActivityType.JOINED, {'username': username})

        # 记录会话
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'room_id': room_id,
            'username': username,
            'start_time': presence.session_start,
            'last_activity': presence.last_seen,
            'activities': [],
            'engagement_score': 0.0
        }

        # 启动心跳任务
        if user_id not in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id] = asyncio.create_task(
                self._heartbeat_monitor(user_id, room_id)
            )

        # 触发订阅回调
        await self._notify_subscribers(user_id, 'join', presence.to_dict())

        return presence

    async def user_leave(self, room_id: str, user_id: str):
        """用户离开房间 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]

            # 结束会话 - 保存session_id用于后续操作
            session_id = user.session_id
            if session_id:
                user.end_session()

                # 创建分析数据
                if session_id in self.active_sessions:
                    session_data = self.active_sessions[session_id]
                    analytics = PresenceAnalytics(
                        room_id=room_id,
                        user_id=user_id,
                        session_id=session_id,
                        session_start=user.session_start,
                        session_end=datetime.now(),
                        total_duration=user.session_duration,
                        total_activities=user.activity_count,
                        keystrokes=user.keystrokes,
                        mouse_clicks=user.mouse_clicks,
                        scroll_events=user.scroll_events,
                        avg_actions_per_minute=user.actions_per_minute
                    )
                    self.analytics[room_id].append(analytics)

                    # 删除会话
                    del self.active_sessions[session_id]

            # 记录活动
            self._record_activity(room_id, user_id, ActivityType.LEFT, {})

            # 从房间移除
            self.rooms[room_id].remove_user(user_id)

            # 取消心跳任务
            if user_id in self.heartbeat_tasks:
                self.heartbeat_tasks[user_id].cancel()
                del self.heartbeat_tasks[user_id]

            # 触发订阅回调
            await self._notify_subscribers(user_id, 'leave', {'user_id': user_id})

            # 如果房间为空，可以选择删除
            if self.rooms[room_id].get_user_count() == 0:
                del self.rooms[room_id]

    async def update_user_status(
        self,
        user_id: str,
        status: PresenceStatus,
        room_id: str,
        custom_status: Optional[str] = None
    ) -> bool:
        """更新用户状态 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.status = status
            user.last_seen = datetime.now()
            user.custom_status = custom_status

            # 触发订阅回调
            await self._notify_subscribers(user_id, 'status_change', user.to_dict())

            return True
        return False

    async def update_user_activity(
        self,
        user_id: str,
        room_id: str,
        activity: ActivityType,
        activity_data: Optional[Dict[str, Any]] = None,
        count: int = 1
    ) -> bool:
        """更新用户活动 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]

            # 更新活动统计
            user.record_activity(activity, count)

            # 记录详细活动
            activity_info = {
                'type': activity.value,
                'data': activity_data or {},
                'timestamp': datetime.now().isoformat()
            }

            # 更新会话数据
            if user.session_id and user.session_id in self.active_sessions:
                self.active_sessions[user.session_id]['last_activity'] = user.last_seen
                self.active_sessions[user.session_id]['activities'].append(activity_info)

            # 更新活动历史
            self._record_activity(room_id, user_id, activity, activity_data or {})

            # 更新活跃度指标
            self.activity_metrics[room_id].append({
                'user_id': user_id,
                'activity': activity.value,
                'timestamp': datetime.now().isoformat()
            })

            # 触发订阅回调
            await self._notify_subscribers(user_id, 'activity_change', {
                'activity': activity.value,
                'data': activity_data
            })

            return True
        return False

    async def send_heartbeat(self, user_id: str, room_id: str) -> bool:
        """接收用户心跳"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.update_heartbeat()
            return True
        return False

    async def _heartbeat_monitor(self, user_id: str, room_id: str):
        """心跳监控任务"""
        try:
            while True:
                await asyncio.sleep(30)  # 每30秒检查一次

                if room_id in self.rooms and user_id in self.rooms[room_id].users:
                    user = self.rooms[room_id].users[user_id]

                    # 检查是否超时
                    if not user.is_alive():
                        print(f"User {user_id} heartbeat timeout, marking as away")
                        user.status = PresenceStatus.AWAY

                        # 5分钟后标记为离线
                        await asyncio.sleep(300)
                        if not user.is_alive():
                            print(f"User {user_id} offline, removing from room")
                            await self.user_leave(room_id, user_id)
                            break
                else:
                    # 用户已离开
                    break

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Heartbeat monitor error for user {user_id}: {e}")

    def subscribe_to_user(self, user_id: str, callback: Callable):
        """订阅用户状态变更"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(callback)

    def unsubscribe_from_user(self, user_id: str, callback: Callable):
        """取消订阅"""
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(callback)

    async def _notify_subscribers(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """通知订阅者"""
        if user_id in self.user_subscriptions:
            for callback in self.user_subscriptions[user_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_type, data)
                    else:
                        callback(event_type, data)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")

    def get_presence_analytics(self, room_id: str, user_id: Optional[str] = None) -> List[PresenceAnalytics]:
        """获取 Presence 分析数据"""
        if user_id:
            return [a for a in self.analytics[room_id] if a.user_id == user_id]
        return self.analytics[room_id]

    def get_presence_insights(self, room_id: str, limit: int = 10) -> List[PresenceInsight]:
        """获取 Presence 洞察"""
        return self.insights[room_id][-limit:]

    def generate_insight(self, room_id: str) -> PresenceInsight:
        """生成 Presence 洞察"""
        if room_id not in self.rooms:
            return None

        room = self.rooms[room_id]
        now = datetime.now()

        # 计算指标
        total_users = room.get_user_count()
        active_users = sum(1 for user in room.users.values() if user.status == PresenceStatus.ONLINE)

        # 简化计算
        avg_session_duration = 0.0
        if self.analytics[room_id]:
            avg_session_duration = sum(a.total_duration for a in self.analytics[room_id]) / len(self.analytics[room_id])

        # 创建洞察
        insight = PresenceInsight(
            room_id=room_id,
            timestamp=now,
            total_users=total_users,
            active_users=active_users,
            peak_concurrent_users=total_users,
            avg_session_duration=avg_session_duration,
            avg_engagement_score=0.0
        )

        self.insights[room_id].append(insight)
        return insight

    def track_keystroke(self, user_id: str, room_id: str):
        """追踪按键"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.keystrokes += 1
            return True
        return False

    def track_mouse_click(self, user_id: str, room_id: str):
        """追踪鼠标点击"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.mouse_clicks += 1
            return True
        return False

    def track_scroll(self, user_id: str, room_id: str):
        """追踪滚动"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.scroll_events += 1
            return True
        return False

    def get_activity_metrics(self, room_id: str, minutes: int = 60) -> List[Dict[str, Any]]:
        """获取活动指标"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            metric for metric in self.activity_metrics[room_id]
            if datetime.fromisoformat(metric['timestamp']) > cutoff
        ]

    def calculate_engagement_score(self, user_id: str, room_id: str) -> float:
        """计算用户参与度分数"""
        if room_id not in self.rooms or user_id not in self.rooms[room_id].users:
            return 0.0

        user = self.rooms[room_id].users[user_id]

        # 简单的参与度计算
        score = 0.0

        # 活动数量权重
        score += min(user.activity_count * 0.1, 50.0)

        # 会话时长权重
        score += min(user.session_duration / 60, 30.0)

        # 互动权重
        score += min(user.keystrokes * 0.01, 20.0)

        self.engagement_scores[f"{room_id}:{user_id}"] = score
        return score

    def get_engagement_leaderboard(self, room_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """获取参与度排行榜"""
        leaderboard = []

        if room_id in self.rooms:
            for user_id, user in self.rooms[room_id].users.items():
                score = self.engagement_scores.get(f"{room_id}:{user_id}", 0.0)
                leaderboard.append({
                    'user_id': user_id,
                    'username': user.username,
                    'score': score,
                    'session_duration': user.session_duration,
                    'activities': user.activity_count
                })

        # 按分数排序
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return leaderboard[:top_n]

    async def update_cursor_position(
        self,
        user_id: str,
        room_id: str,
        position: Dict[str, Any]
    ) -> bool:
        """更新光标位置 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.cursor_position = position
            user.last_seen = datetime.now()

            # 追踪活动
            self.track_keystroke(user_id, room_id)
            await self.update_user_activity(
                user_id, room_id, ActivityType.MOVING_CURSOR, {'position': position}
            )

            # 触发订阅回调
            await self._notify_subscribers(user_id, 'cursor_change', position)

            return True
        return False

    async def update_selection(
        self,
        user_id: str,
        room_id: str,
        selection: Dict[str, Any]
    ) -> bool:
        """更新选择区域 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            user.selection = selection
            user.last_seen = datetime.now()

            # 追踪活动
            self.track_mouse_click(user_id, room_id)
            await self.update_user_activity(
                user_id, room_id, ActivityType.SELECTING, {'selection': selection}
            )

            # 触发订阅回调
            await self._notify_subscribers(user_id, 'selection_change', selection)

            return True
        return False

    async def mark_user_typing(self, user_id: str, room_id: str, is_typing: bool):
        """标记用户正在输入 - 增强版"""
        if is_typing:
            await self.update_user_activity(
                user_id, room_id, ActivityType.TYPING, {'is_typing': True}
            )
        else:
            await self.update_user_activity(
                user_id, room_id, ActivityType.EDITING, {'is_typing': False}
            )

    async def mark_user_idle(self, user_id: str, room_id: str):
        """标记用户空闲 - 增强版"""
        return await self.update_user_activity(
            user_id, room_id, ActivityType.IDLE, {}
        )

    def get_room_presence(self, room_id: str, include_analytics: bool = False) -> Optional[Dict[str, Any]]:
        """获取房间在线状态 - 增强版"""
        if room_id in self.rooms:
            data = self.rooms[room_id].to_dict()

            if include_analytics:
                data['analytics'] = {
                    'insights': [insight.to_dict() for insight in self.get_presence_insights(room_id, 1)],
                    'leaderboard': self.get_engagement_leaderboard(room_id),
                    'activity_metrics': self.get_activity_metrics(room_id)
                }

            return data
        return None

    def get_user_presence(self, room_id: str, user_id: str, include_session: bool = False) -> Optional[Dict[str, Any]]:
        """获取特定用户在线状态 - 增强版"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            user = self.rooms[room_id].users[user_id]
            data = user.to_dict()

            if include_session and user.session_id:
                data['session'] = self.active_sessions.get(user.session_id, {})

            return data
        return None

    def get_all_rooms(self, include_analytics: bool = False) -> List[Dict[str, Any]]:
        """获取所有房间在线状态 - 增强版"""
        rooms = []
        for room_id, room in self.rooms.items():
            room_data = room.to_dict()

            if include_analytics:
                room_data['analytics'] = {
                    'insights': [insight.to_dict() for insight in self.get_presence_insights(room_id, 1)],
                    'leaderboard': self.get_engagement_leaderboard(room_id)
                }

            rooms.append(room_data)

        return rooms

    def get_room_users(self, room_id: str, include_engagement: bool = False) -> List[Dict[str, Any]]:
        """获取房间内所有用户状态 - 增强版"""
        if room_id in self.rooms:
            users = []
            for user in self.rooms[room_id].users.values():
                user_data = user.to_dict()

                if include_engagement:
                    user_data['engagement_score'] = self.calculate_engagement_score(user.user_id, room_id)

                users.append(user_data)

            return users
        return []

    async def cleanup_inactive_users(self, timeout_minutes: Optional[int] = None):
        """清理非活跃用户 - 增强版"""
        timeout = timedelta(minutes=timeout_minutes or self.timeout_minutes)
        now = datetime.now()

        rooms_to_remove = []

        for room_id, room in self.rooms.items():
            users_to_remove = []

            for user_id, user in room.users.items():
                inactive_duration = now - user.last_seen

                if inactive_duration > timeout:
                    users_to_remove.append(user_id)

            for user_id in users_to_remove:
                await self.user_leave(room_id, user_id)

            if room.get_user_count() == 0:
                rooms_to_remove.append(room_id)

        for room_id in rooms_to_remove:
            if room_id in self.rooms:
                del self.rooms[room_id]

    async def bulk_update_activity(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新活动"""
        updated = 0
        for update in updates:
            user_id = update.get('user_id')
            room_id = update.get('room_id')
            activity = update.get('activity')
            activity_data = update.get('data')

            if activity and isinstance(activity, ActivityType):
                if await self.update_user_activity(user_id, room_id, activity, activity_data):
                    updated += 1

        return updated

    def get_realtime_stats(self, room_id: Optional[str] = None) -> Dict[str, Any]:
        """获取实时统计"""
        if room_id:
            room = self.rooms.get(room_id)
            if not room:
                return {}

            return {
                'room_id': room_id,
                'total_users': room.get_user_count(),
                'active_users': sum(1 for u in room.users.values() if u.status == PresenceStatus.ONLINE),
                'typing_users': sum(1 for u in room.users.values() if u.activity == ActivityType.TYPING),
                'editing_users': sum(1 for u in room.users.values() if u.activity == ActivityType.EDITING),
                'idle_users': sum(1 for u in room.users.values() if u.activity == ActivityType.IDLE),
                'sessions': len([u for u in room.users.values() if u.session_id]),
                'avg_session_duration': sum(u.session_duration for u in room.users.values()) / max(room.get_user_count(), 1),
                'total_activities': sum(u.activity_count for u in room.users.values()),
                'leaderboard': self.get_engagement_leaderboard(room_id, 5)
            }

        # 全局统计
        return {
            'total_rooms': len(self.rooms),
            'total_users': sum(r.get_user_count() for r in self.rooms.values()),
            'active_sessions': len(self.active_sessions),
            'total_analytics_records': sum(len(a) for a in self.analytics.values())
        }

    def export_presence_data(self, room_id: str, format: str = 'json') -> str:
        """导出 Presence 数据"""
        data = {
            'room_id': room_id,
            'exported_at': datetime.now().isoformat(),
            'presence': self.get_room_presence(room_id, include_analytics=True),
            'analytics': [a.to_dict() for a in self.analytics[room_id]],
            'insights': [i.to_dict() for i in self.insights[room_id]],
            'activity_history': self.activity_history.get(room_id, [])
        }

        if format == 'json':
            return json.dumps(data, indent=2)

        return str(data)

    def get_user_activity_history(
        self,
        user_id: str,
        room_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取用户活动历史 - 增强版"""
        key = f"{room_id}:{user_id}"
        if key in self.activity_history:
            history = self.activity_history[key][-limit:]

            # 转换为增强格式
            return [
                {
                    'activity': item['activity'],
                    'data': item['data'],
                    'timestamp': item['timestamp'],
                    'session_id': self._get_session_id(user_id, room_id)
                }
                for item in history
            ]
        return []

    def _get_session_id(self, user_id: str, room_id: str) -> Optional[str]:
        """获取用户的会话 ID"""
        if room_id in self.rooms and user_id in self.rooms[room_id].users:
            return self.rooms[room_id].users[user_id].session_id
        return None

    def _record_activity(
        self,
        room_id: str,
        user_id: str,
        activity: ActivityType,
        data: Dict[str, Any]
    ):
        """记录用户活动 - 增强版"""
        key = f"{room_id}:{user_id}"
        if key not in self.activity_history:
            self.activity_history[key] = []

        activity_record = {
            'activity': activity.value,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        self.activity_history[key].append(activity_record)

        # 限制历史记录数量
        if len(self.activity_history[key]) > 1000:
            self.activity_history[key] = self.activity_history[key][-1000:]

        # 更新会话数据
        session_id = self._get_session_id(user_id, room_id)
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id]['activities'].append(activity_record)

    def get_statistics(self) -> Dict[str, Any]:
        """获取在线状态统计 - 增强版"""
        total_users = sum(room.get_user_count() for room in self.rooms.values())
        total_rooms = len(self.rooms)

        status_counts = {
            'online': 0,
            'away': 0,
            'busy': 0,
            'offline': 0
        }

        activity_counts = defaultdict(int)

        for room in self.rooms.values():
            for user in room.users.values():
                status_counts[user.status.value] += 1
                if user.activity:
                    activity_counts[user.activity.value] += 1

        # 计算高级统计
        total_sessions = len(self.active_sessions)
        total_activities = sum(user.activity_count for room in self.rooms.values() for user in room.users.values())
        total_keystrokes = sum(user.keystrokes for room in self.rooms.values() for user in room.users.values())

        avg_session_duration = 0.0
        if self.active_sessions:
            now = datetime.now()
            durations = []
            for session in self.active_sessions.values():
                start = session.get('start_time', now)
                durations.append((now - start).total_seconds())
            avg_session_duration = sum(durations) / len(durations)

        return {
            'total_users': total_users,
            'total_rooms': total_rooms,
            'status_distribution': dict(status_counts),
            'activity_distribution': dict(activity_counts),
            'average_users_per_room': total_users / total_rooms if total_rooms > 0 else 0,
            'active_sessions': total_sessions,
            'total_activities': total_activities,
            'total_keystrokes': total_keystrokes,
            'average_session_duration': avg_session_duration,
            'total_analytics_records': sum(len(a) for a in self.analytics.values()),
            'total_insights': sum(len(i) for i in self.insights.values())
        }

    async def broadcast_presence_update(
        self,
        room_id: str,
        user_id: str,
        presence_data: Dict[str, Any]
    ):
        """广播在线状态更新 - 增强版"""
        # 与 WebSocket 系统集成
        # 这里可以发布到消息队列或直接发送到 WebSocket 连接
        print(f"Broadcasting presence update: {room_id} - {user_id} - {presence_data}")

        # 触发订阅回调
        await self._notify_subscribers(user_id, 'presence_update', presence_data)

    async def get_presence_summary(self, room_id: str) -> Dict[str, Any]:
        """获取房间在线状态摘要 - 增强版"""
        room = self.rooms.get(room_id)
        if not room:
            return {}

        users = []
        for user in room.users.values():
            user_info = {
                'user_id': user.user_id,
                'username': user.username,
                'status': user.status.value,
                'activity': user.activity.value if user.activity else None,
                'last_seen': user.last_seen.isoformat(),
                'color': user.color,
                'session_duration': user.session_duration,
                'engagement_score': self.engagement_scores.get(f"{room_id}:{user.user_id}", 0.0)
            }
            users.append(user_info)

        # 计算摘要统计
        typing_users = sum(1 for u in users if u['activity'] == 'typing')
        editing_users = sum(1 for u in users if u['activity'] == 'editing')
        idle_users = sum(1 for u in users if u['activity'] == 'idle')
        online_users = sum(1 for u in users if u['status'] == 'online')

        # 生成洞察
        insight = self.generate_insight(room_id)

        return {
            'room_id': room_id,
            'name': room.name,
            'user_count': room.get_user_count(),
            'users': users,
            'summary': {
                'online': online_users,
                'away': sum(1 for u in users if u['status'] == 'away'),
                'busy': sum(1 for u in users if u['status'] == 'busy'),
                'typing': typing_users,
                'editing': editing_users,
                'idle': idle_users,
                'active_sessions': sum(1 for u in users if u.get('session_duration', 0) > 0)
            },
            'engagement': {
                'average_score': sum(u['engagement_score'] for u in users) / max(len(users), 1),
                'total_activities': sum(u.get('session_duration', 0) for u in users),
                'leaderboard': self.get_engagement_leaderboard(room_id, 5)
            },
            'insight': insight.to_dict() if insight else None,
            'generated_at': datetime.now().isoformat()
        }


# 全局 Presence Manager 实例
presence_manager = PresenceManager(timeout_minutes=5)


# 定期清理任务
async def periodic_cleanup():
    """定期清理非活跃用户"""
    while True:
        await asyncio.sleep(60)  # 每分钟执行一次
        await presence_manager.cleanup_inactive_users()
        print("Cleaned up inactive users")

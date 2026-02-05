"""
实时通知系统

支持多种通知类型：浏览器通知、邮件通知、应用内通知
"""

import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio


class NotificationType(Enum):
    """通知类型"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    MENTION = "mention"
    INVITATION = "invitation"
    UPDATE = "update"
    SYSTEM = "system"


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """通知"""
    id: str
    type: NotificationType
    title: str
    message: str
    user_id: str
    room_id: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """从字典创建通知"""
        data = data.copy()
        data['type'] = NotificationType(data['type'])
        data['priority'] = NotificationPriority(data['priority'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


@dataclass
class NotificationTemplate:
    """通知模板"""
    template_id: str
    type: NotificationType
    title_template: str
    message_template: str
    default_priority: NotificationPriority = NotificationPriority.NORMAL
    variables: List[str] = field(default_factory=list)

    def render(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """渲染模板"""
        title = self.title_template
        message = self.message_template

        for var, value in variables.items():
            placeholder = f"{{{var}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))

        return {
            'title': title,
            'message': message
        }


class NotificationChannel:
    """通知渠道基类"""

    def send(self, notification: Notification) -> bool:
        """发送通知"""
        raise NotImplementedError

    def send_batch(self, notifications: List[Notification]) -> bool:
        """批量发送通知"""
        results = []
        for notif in notifications:
            try:
                result = self.send(notif)
                results.append(result)
            except Exception as e:
                print(f"Failed to send notification: {e}")
                results.append(False)
        return all(results)


class BrowserNotificationChannel(NotificationChannel):
    """浏览器通知渠道"""

    def send(self, notification: Notification) -> bool:
        """发送浏览器通知"""
        # 这里应该与前端 WebSocket 集成
        # 简化实现，返回成功
        print(f"[Browser Notification] {notification.title}: {notification.message}")
        return True

    def send_batch(self, notifications: List[Notification]) -> bool:
        """批量发送浏览器通知"""
        results = []
        for notif in notifications:
            result = self.send(notif)
            results.append(result)
        return all(results)


class EmailNotificationChannel(NotificationChannel):
    """邮件通知渠道"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send(self, notification: Notification) -> bool:
        """发送邮件通知"""
        # 简化实现，返回成功
        print(f"[Email Notification] To: {notification.user_id}")
        print(f"Subject: {notification.title}")
        print(f"Body: {notification.message}")
        return True


class InAppNotificationChannel(NotificationChannel):
    """应用内通知渠道"""

    def send(self, notification: Notification) -> bool:
        """发送应用内通知"""
        # 这里应该存储到数据库并通过 WebSocket 推送
        print(f"[In-App Notification] User: {notification.user_id}")
        print(f"Title: {notification.title}")
        print(f"Message: {notification.message}")
        return True


class NotificationManager:
    """通知管理器"""

    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}  # user_id -> notifications
        self.templates: Dict[str, NotificationTemplate] = {}
        self.channels: List[NotificationChannel] = []
        self.subscribers: Dict[str, Callable] = {}  # user_id -> callback

        # 添加默认渠道
        self.channels.append(BrowserNotificationChannel())
        self.channels.append(InAppNotificationChannel())

        # 加载默认模板
        self._load_default_templates()

    def _load_default_templates(self):
        """加载默认通知模板"""
        templates = [
            NotificationTemplate(
                template_id="user_joined",
                type=NotificationType.INFO,
                title_template="用户加入",
                message_template="{username} 加入了房间",
                variables=["username"]
            ),
            NotificationTemplate(
                template_id="user_left",
                type=NotificationType.INFO,
                title_template="用户离开",
                message_template="{username} 离开了房间",
                variables=["username"]
            ),
            NotificationTemplate(
                template_id="mention",
                type=NotificationType.MENTION,
                title_template="有人提到了你",
                message_template="{username} 在 {room_name} 中提到了你",
                variables=["username", "room_name"]
            ),
            NotificationTemplate(
                template_id="invitation",
                type=NotificationType.INVITATION,
                title_template="邀请通知",
                message_template="{username} 邀请你加入 {room_name}",
                variables=["username", "room_name"]
            ),
            NotificationTemplate(
                template_id="update",
                type=NotificationType.UPDATE,
                title_template="内容更新",
                message_template="房间 {room_name} 有新更新",
                variables=["room_name"]
            ),
        ]

        for template in templates:
            self.templates[template.template_id] = template

    def register_channel(self, channel: NotificationChannel):
        """注册通知渠道"""
        self.channels.append(channel)

    def subscribe(self, user_id: str, callback: Callable[[Notification], None]):
        """订阅用户通知"""
        self.subscribers[user_id] = callback

    def unsubscribe(self, user_id: str):
        """取消订阅"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]

    def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        room_id: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None
    ) -> Notification:
        """发送通知"""
        notification = Notification(
            id=f"notif_{datetime.now().timestamp()}",
            type=notification_type,
            title=title,
            message=message,
            user_id=user_id,
            room_id=room_id,
            priority=priority,
            data=data or {},
            expires_at=datetime.now() + timedelta(seconds=expires_in) if expires_in else None
        )

        # 添加到用户通知列表
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        self.notifications[user_id].append(notification)

        # 发送到各个渠道
        self._send_to_channels(notification)

        # 触发订阅回调
        if user_id in self.subscribers:
            try:
                self.subscribers[user_id](notification)
            except Exception as e:
                print(f"Error in notification callback: {e}")

        return notification

    def send_from_template(
        self,
        user_id: str,
        template_id: str,
        variables: Dict[str, Any],
        room_id: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> Optional[Notification]:
        """使用模板发送通知"""
        if template_id not in self.templates:
            print(f"Template not found: {template_id}")
            return None

        template = self.templates[template_id]
        rendered = template.render(variables)

        return self.send_notification(
            user_id=user_id,
            notification_type=template.type,
            title=rendered['title'],
            message=rendered['message'],
            room_id=room_id,
            priority=template.default_priority
        )

    def _send_to_channels(self, notification: Notification):
        """发送到所有注册的渠道"""
        for channel in self.channels:
            try:
                channel.send(notification)
            except Exception as e:
                print(f"Failed to send notification via {channel.__class__.__name__}: {e}")

    def send_batch(
        self,
        notifications: List[Notification]
    ) -> bool:
        """批量发送通知"""
        for channel in self.channels:
            try:
                channel.send_batch(notifications)
            except Exception as e:
                print(f"Failed to send batch notifications: {e}")
                return False
        return True

    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """获取用户通知"""
        notifications = self.notifications.get(user_id, [])

        if unread_only:
            notifications = [n for n in notifications if not n.read]

        # 按时间倒序排列
        notifications.sort(key=lambda n: n.created_at, reverse=True)

        return notifications[:limit]

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """标记通知为已读"""
        notifications = self.notifications.get(user_id, [])
        for notif in notifications:
            if notif.id == notification_id:
                notif.read = True
                return True
        return False

    def mark_all_as_read(self, user_id: str) -> int:
        """标记所有通知为已读"""
        notifications = self.notifications.get(user_id, [])
        count = 0
        for notif in notifications:
            if not notif.read:
                notif.read = True
                count += 1
        return count

    def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """删除通知"""
        notifications = self.notifications.get(user_id, [])
        for i, notif in enumerate(notifications):
            if notif.id == notification_id:
                notifications.pop(i)
                return True
        return False

    def clear_notifications(self, user_id: str):
        """清除所有通知"""
        self.notifications[user_id] = []

    def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数"""
        notifications = self.notifications.get(user_id, [])
        return sum(1 for n in notifications if not n.read)

    def cleanup_expired(self):
        """清理过期通知"""
        now = datetime.now()
        for user_id, notifications in self.notifications.items():
            self.notifications[user_id] = [
                n for n in notifications
                if n.expires_at is None or n.expires_at > now
            ]

    def get_statistics(self) -> Dict[str, Any]:
        """获取通知统计"""
        total_notifications = sum(len(notifs) for notifs in self.notifications.values())
        unread_notifications = sum(
            sum(1 for n in notifs if not n.read)
            for notifs in self.notifications.values()
        )

        type_counts = {
            'info': 0,
            'success': 0,
            'warning': 0,
            'error': 0,
            'mention': 0,
            'invitation': 0,
            'update': 0,
            'system': 0
        }

        for notifs in self.notifications.values():
            for notif in notifs:
                type_counts[notif.type.value] += 1

        return {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'type_distribution': type_counts,
            'total_users': len(self.notifications),
            'total_channels': len(self.channels),
        }


# 全局通知管理器实例
notification_manager = NotificationManager()


# 定期清理任务
async def periodic_notification_cleanup():
    """定期清理过期通知"""
    while True:
        await asyncio.sleep(300)  # 每5分钟执行一次
        await notification_manager.cleanup_expired()
        print("Cleaned up expired notifications")

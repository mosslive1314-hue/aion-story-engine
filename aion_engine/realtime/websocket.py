"""
WebSocket 实时通信系统

实现实时双向通信，支持多用户协作编辑
"""

import json
import asyncio
from typing import Dict, Set, Optional, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型枚举"""
    JOIN = "join"
    LEAVE = "leave"
    UPDATE = "update"
    CURSOR = "cursor"
    SELECTION = "selection"
    CHANGE = "change"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    PRESENCE = "presence"
    SYNC = "sync"


@dataclass
class User:
    """用户信息"""
    user_id: str
    username: str
    color: str
    cursor_position: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    last_seen: datetime = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        return data


@dataclass
class Room:
    """房间/会话信息"""
    room_id: str
    name: str
    users: Dict[str, User] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.users is None:
            self.users = {}
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_user(self, user: User):
        """添加用户"""
        self.users[user.user_id] = user

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
            'users': {uid: user.to_dict() for uid, user in self.users.items()},
            'created_at': self.created_at.isoformat(),
            'user_count': self.get_user_count(),
        }


@dataclass
class Message:
    """WebSocket 消息"""
    type: MessageType
    room_id: str
    user_id: str
    data: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        data = {
            'type': self.type.value,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """从 JSON 创建消息"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data['type']),
            room_id=data['room_id'],
            user_id=data['user_id'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
        )


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 连接存储: room_id -> {user_id -> websocket}
        self.connections: Dict[str, Dict[str, WebSocketServerProtocol]] = {}

        # 房间存储
        self.rooms: Dict[str, Room] = {}

        # 用户信息存储: websocket -> user_id
        self.user_connections: Dict[WebSocketServerProtocol, str] = {}

        # 用户房间映射: user_id -> room_id
        self.user_rooms: Dict[str, str] = {}

    async def connect(self, websocket: WebSocketServerProtocol, room_id: str, user: User):
        """处理新连接"""
        logger.info(f"用户 {user.username} 加入房间 {room_id}")

        # 添加到连接池
        if room_id not in self.connections:
            self.connections[room_id] = {}

        self.connections[room_id][user.user_id] = websocket
        self.user_connections[websocket] = user.user_id
        self.user_rooms[user.user_id] = room_id

        # 创建或获取房间
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id=room_id, name=f"Room {room_id}")

        # 添加用户到房间
        self.rooms[room_id].add_user(user)

        # 发送欢迎消息给新用户
        await self.send_to_user(
            websocket,
            Message(
                type=MessageType.JOIN,
                room_id=room_id,
                user_id=user.user_id,
                data={
                    'message': f'欢迎 {user.username}!',
                    'room': self.rooms[room_id].to_dict(),
                    'users': [u.to_dict() for u in self.rooms[room_id].users.values()]
                }
            )
        )

        # 通知其他用户有新用户加入
        await self.broadcast_to_room(
            room_id,
            Message(
                type=MessageType.PRESENCE,
                room_id=room_id,
                user_id=user.user_id,
                data={
                    'action': 'user_joined',
                    'user': user.to_dict()
                }
            ),
            exclude_user=user.user_id
        )

    async def disconnect(self, websocket: WebSocketServerProtocol):
        """处理断开连接"""
        if websocket not in self.user_connections:
            return

        user_id = self.user_connections[websocket]
        room_id = self.user_rooms.get(user_id)

        if room_id and room_id in self.rooms:
            # 从房间移除用户
            user = self.rooms[room_id].users.get(user_id)
            self.rooms[room_id].remove_user(user_id)

            # 从连接池移除
            if room_id in self.connections and user_id in self.connections[room_id]:
                del self.connections[room_id][user_id]

            # 清理映射
            del self.user_connections[websocket]
            del self.user_rooms[user_id]

            logger.info(f"用户 {user_id} 离开房间 {room_id}")

            # 通知其他用户
            await self.broadcast_to_room(
                room_id,
                Message(
                    type=MessageType.PRESENCE,
                    room_id=room_id,
                    user_id=user_id,
                    data={
                        'action': 'user_left',
                        'user_id': user_id,
                        'user': user.to_dict() if user else None
                    }
                )
            )

            # 如果房间为空，可以选择删除房间
            if self.rooms[room_id].get_user_count() == 0:
                logger.info(f"房间 {room_id} 为空，删除房间")
                del self.rooms[room_id]
                if room_id in self.connections:
                    del self.connections[room_id]

    async def send_to_user(self, websocket: WebSocketServerProtocol, message: Message):
        """发送消息给特定用户"""
        try:
            await websocket.send(message.to_json())
        except websockets.exceptions.ConnectionClosed:
            logger.error(f"连接已关闭，无法发送消息")
        except Exception as e:
            logger.error(f"发送消息失败: {e}")

    async def send_to_room(self, room_id: str, message: Message):
        """发送消息给房间内所有用户"""
        if room_id not in self.connections:
            return

        for user_id, websocket in list(self.connections[room_id].items()):
            await self.send_to_user(websocket, message)

    async def broadcast_to_room(
        self,
        room_id: str,
        message: Message,
        exclude_user: Optional[str] = None
    ):
        """广播消息给房间内所有用户（除指定用户外）"""
        if room_id not in self.connections:
            return

        for user_id, websocket in list(self.connections[room_id].items()):
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_to_user(websocket, message)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: Message):
        """处理接收到的消息"""
        logger.info(f"处理消息: {message.type.value} 从用户 {message.user_id}")

        if message.type == MessageType.UPDATE:
            # 广播更新给房间内其他用户
            await self.broadcast_to_room(
                message.room_id,
                message,
                exclude_user=message.user_id
            )

        elif message.type == MessageType.CURSOR:
            # 更新用户光标位置
            if message.room_id in self.rooms:
                user = self.rooms[message.room_id].users.get(message.user_id)
                if user:
                    user.cursor_position = message.data

            # 广播光标位置给其他用户
            await self.broadcast_to_room(
                message.room_id,
                message,
                exclude_user=message.user_id
            )

        elif message.type == MessageType.SELECTION:
            # 更新用户选择
            if message.room_id in self.rooms:
                user = self.rooms[message.room_id].users.get(message.user_id)
                if user:
                    user.selection = message.data

            # 广播选择给其他用户
            await self.broadcast_to_room(
                message.room_id,
                message,
                exclude_user=message.user_id
            )

        elif message.type == MessageType.CHANGE:
            # 广播内容变更
            await self.broadcast_to_room(
                message.room_id,
                message,
                exclude_user=message.user_id
            )

        elif message.type == MessageType.SYNC:
            # 处理同步请求
            await self.send_to_user(
                websocket,
                Message(
                    type=MessageType.SYNC,
                    room_id=message.room_id,
                    user_id=message.user_id,
                    data={
                        'room': self.rooms[message.room_id].to_dict() if message.room_id in self.rooms else None,
                        'users': [u.to_dict() for u in self.rooms[message.room_id].users.values()] if message.room_id in self.rooms else []
                    }
                )
            )

        elif message.type == MessageType.PING:
            # 响应 ping
            await self.send_to_user(
                websocket,
                Message(
                    type=MessageType.PONG,
                    room_id=message.room_id,
                    user_id=message.user_id,
                    data={'timestamp': datetime.now().isoformat()}
                )
            )

    async def get_room_info(self, room_id: str) -> Optional[Dict[str, Any]]:
        """获取房间信息"""
        if room_id in self.rooms:
            return self.rooms[room_id].to_dict()
        return None

    async def get_room_users(self, room_id: str) -> List[Dict[str, Any]]:
        """获取房间内用户列表"""
        if room_id in self.rooms:
            return [user.to_dict() for user in self.rooms[room_id].users.values()]
        return []

    def get_active_rooms(self) -> List[str]:
        """获取活跃房间列表"""
        return list(self.rooms.keys())

    def get_room_count(self) -> int:
        """获取房间数"""
        return len(self.rooms)

    def get_total_connections(self) -> int:
        """获取总连接数"""
        return sum(len(conns) for conns in self.connections.values())


# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()


async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """WebSocket 连接处理函数"""
    logger.info(f"新连接: {websocket.remote_address}")

    try:
        async for message_str in websocket:
            try:
                # 解析消息
                message = Message.from_json(message_str)

                # 根据消息类型处理
                if message.type == MessageType.JOIN:
                    # 解析用户信息
                    user_data = message.data.get('user', {})
                    user = User(
                        user_id=user_data.get('user_id'),
                        username=user_data.get('username', 'Anonymous'),
                        color=user_data.get('color', '#3498db'),
                    )
                    await websocket_manager.connect(websocket, message.room_id, user)

                else:
                    # 处理其他类型消息
                    await websocket_manager.handle_message(websocket, message)

            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {message_str}")
                error_msg = Message(
                    type=MessageType.ERROR,
                    room_id='',
                    user_id='',
                    data={'error': 'Invalid JSON'}
                )
                await websocket_manager.send_to_user(websocket, error_msg)

            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                error_msg = Message(
                    type=MessageType.ERROR,
                    room_id='',
                    user_id='',
                    data={'error': str(e)}
                )
                await websocket_manager.send_to_user(websocket, error_msg)

    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"连接正常关闭: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"连接异常: {websocket.remote_address}, 错误: {e}")
    finally:
        # 处理断开连接
        await websocket_manager.disconnect(websocket)


async def start_websocket_server(host: str = "0.0.0.0", port: int = 8765):
    """启动 WebSocket 服务器"""
    logger.info(f"启动 WebSocket 服务器: ws://{host}:{port}")

    async with websockets.serve(websocket_handler, host, port):
        logger.info("WebSocket 服务器已启动，等待连接...")
        await asyncio.Future()  # 永远等待

"""
Ecosystem Orchestrator - 生态系统编排器
整合所有Phase的功能，提供统一的生态系统接口
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid
from asyncio import Queue, Event


class EventType(Enum):
    """事件类型"""
    WORLD_CREATED = "world_created"
    WORLD_UPDATED = "world_updated"
    WORLD_DELETED = "world_deleted"

    PORTAL_CREATED = "portal_created"
    PORTAL_USED = "portal_used"
    PORTAL_DELETED = "portal_deleted"

    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_VOTED = "proposal_voted"
    PROPOSAL_EXECUTED = "proposal_executed"

    ASSET_PUBLISHED = "asset_published"
    ASSET_PURCHASED = "asset_purchased"

    TOKEN_STAKED = "token_staked"
    TOKEN_UNSTAKED = "token_unstaked"

    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"

    CUSTOM = "custom"


@dataclass
class Event:
    """事件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM
    source: str = ""  # 事件源（模块名）
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed,
            "metadata": self.metadata
        }


@dataclass
class EventHandler:
    """事件处理器"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    event_types: List[EventType] = field(default_factory=list)
    callback: Callable = None
    enabled: bool = True
    priority: int = 0  # 优先级（数字越大优先级越高）
    filter_criteria: Dict[str, Any] = field(default_factory=dict)  # 过滤条件

    async def handle(self, event: Event) -> bool:
        """处理事件"""
        if not self.enabled:
            return False

        # 检查事件类型
        if event.event_type not in self.event_types:
            return False

        # 检查过滤条件
        for key, value in self.filter_criteria.items():
            if event.data.get(key) != value:
                return False

        # 调用回调
        try:
            if self.callback:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(event)
                else:
                    self.callback(event)
                return True
        except Exception as e:
            print(f"Error in event handler {self.name}: {e}")

        return False


class EventBus:
    """事件总线"""

    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.event_queue: Queue = Queue()
        self.event_history: List[Event] = []
        self.running = False
        self.max_history = 10000  # 最大历史记录数

    def subscribe(self, handler: EventHandler):
        """订阅事件"""
        for event_type in handler.event_types:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

            # 按优先级排序
            self.handlers[event_type].sort(key=lambda h: h.priority, reverse=True)

    def unsubscribe(self, handler_id: str):
        """取消订阅"""
        for event_type, handlers in self.handlers.items():
            self.handlers[event_type] = [
                h for h in handlers if h.id != handler_id
            ]

    async def publish(self, event: Event):
        """发布事件"""
        # 添加到队列
        await self.event_queue.put(event)

        # 添加到历史
        self.event_history.append(event)

        # 限制历史大小
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

    async def process_events(self):
        """处理事件"""
        self.running = True

        while self.running:
            try:
                # 从队列获取事件
                event = await self.event_queue.get()

                # 查找处理器
                handlers = self.handlers.get(event.event_type, [])

                # 执行处理器
                for handler in handlers:
                    try:
                        await handler.handle(event)
                    except Exception as e:
                        print(f"Error processing event {event.id} with handler {handler.name}: {e}")

                event.processed = True

            except Exception as e:
                print(f"Error in event processing loop: {e}")

    def stop(self):
        """停止事件处理"""
        self.running = False

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """获取事件"""
        events = self.event_history

        # 过滤
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if source:
            events = [e for e in events if e.source == source]

        if since:
            events = [e for e in events if e.timestamp >= since]

        # 按时间倒序
        events.sort(key=lambda e: e.timestamp, reverse=True)

        return events[:limit]


class Plugin:
    """插件"""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.version = version
        self.enabled = True
        self.loaded = False
        self.config: Dict[str, Any] = {}
        self.dependencies: List[str] = []  # 依赖的插件

    def load(self):
        """加载插件"""
        self.loaded = True

    def unload(self):
        """卸载插件"""
        self.loaded = False

    def configure(self, config: Dict[str, Any]):
        """配置插件"""
        self.config.update(config)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "loaded": self.loaded,
            "config": self.config,
            "dependencies": self.dependencies
        }


class EcosystemOrchestrator:
    """生态系统编排器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/ecosystem.json"

        # 事件总线
        self.event_bus = EventBus()

        # 插件系统
        self.plugins: Dict[str, Plugin] = {}

        # 模块引用
        self.multiverse_manager = None
        self.portal_manager = None
        self.dao_manager = None
        self.advanced_economy = None
        self.collaboration_manager = None
        self.marketplace = None

        # 统计
        self.statistics: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "events_processed": 0,
            "active_plugins": 0
        }

        # 加载数据
        self._load_data()

    def register_module(self, module_name: str, module_instance: Any):
        """注册模块"""
        setattr(self, module_name, module_instance)

    def init_plugins(self):
        """初始化插件"""
        # 这里可以加载并初始化所有插件
        pass

    def register_plugin(self, plugin: Plugin) -> bool:
        """注册插件"""
        # 检查依赖
        for dep in plugin.dependencies:
            if dep not in self.plugins:
                return False

        self.plugins[plugin.id] = plugin

        if plugin.enabled:
            plugin.load()
            self.statistics["active_plugins"] += 1

        self._save_data()
        return True

    def unregister_plugin(self, plugin_id: str) -> bool:
        """注销插件"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False

        # 检查是否有其他插件依赖此插件
        for other_plugin in self.plugins.values():
            if plugin_id in other_plugin.dependencies:
                return False

        plugin.unload()
        del self.plugins[plugin_id]

        self.statistics["active_plugins"] = sum(1 for p in self.plugins.values() if p.enabled and p.loaded)

        self._save_data()
        return True

    def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False

        plugin.enabled = True
        if not plugin.loaded:
            plugin.load()
            self.statistics["active_plugins"] += 1

        self._save_data()
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """禁用插件"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False

        plugin.enabled = False
        if plugin.loaded:
            plugin.unload()
            self.statistics["active_plugins"] -= 1

        self._save_data()
        return True

    async def emit_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ):
        """发送事件"""
        event = Event(
            event_type=event_type,
            source=source,
            data=data,
            metadata=metadata or {}
        )

        await self.event_bus.publish(event)
        self.statistics["events_processed"] += 1

    def subscribe_to_events(self, handler: EventHandler):
        """订阅事件"""
        self.event_bus.subscribe(handler)

    def unsubscribe_from_events(self, handler_id: str):
        """取消订阅事件"""
        self.event_bus.unsubscribe(handler_id)

    def get_ecosystem_status(self) -> Dict[str, Any]:
        """获取生态系统状态"""
        # 模块状态
        module_status = {}
        for module_name in ["multiverse_manager", "portal_manager", "dao_manager", "advanced_economy"]:
            module = getattr(self, module_name, None)
            module_status[module_name] = {
                "loaded": module is not None,
                "type": type(module).__name__ if module else None
            }

        # 插件状态
        plugins_status = {
            "total": len(self.plugins),
            "active": self.statistics["active_plugins"],
            "loaded": len([p for p in self.plugins.values() if p.loaded])
        }

        # 事件统计
        recent_events = len(self.event_bus.event_history)

        return {
            "modules": module_status,
            "plugins": plugins_status,
            "events": {
                "recent_events": recent_events,
                "total_processed": self.statistics["events_processed"]
            },
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.statistics["start_time"])).total_seconds()
        }

    def get_analytics(self) -> Dict[str, Any]:
        """获取分析数据"""
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_status": self.get_ecosystem_status()
        }

        # 添加各模块的统计
        if self.multiverse_manager:
            analytics["multiverse"] = self.multiverse_manager.get_statistics()

        if self.portal_manager:
            analytics["portals"] = self.portal_manager.get_statistics()

        if self.advanced_economy:
            analytics["economy"] = self.advanced_economy.get_statistics()

        return analytics

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载插件
            for plugin_data in data.get("plugins", []):
                plugin = Plugin(
                    name=plugin_data["name"],
                    version=plugin_data.get("version", "1.0.0")
                )
                plugin.id = plugin_data["id"]
                plugin.enabled = plugin_data.get("enabled", True)
                plugin.loaded = plugin_data.get("loaded", False)
                plugin.config = plugin_data.get("config", {})
                plugin.dependencies = plugin_data.get("dependencies", [])

                self.plugins[plugin.id] = plugin

            # 加载统计
            self.statistics.update(data.get("statistics", {}))

        except Exception as e:
            print(f"Error loading ecosystem data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "plugins": [plugin.to_dict() for plugin in self.plugins.values()],
                "statistics": self.statistics,
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving ecosystem data: {e}")


# 全局生态系统编排器实例
_ecosystem_orchestrator: Optional[EcosystemOrchestrator] = None


def get_ecosystem_orchestrator(storage_path: Optional[str] = None) -> EcosystemOrchestrator:
    """获取生态系统编排器单例"""
    global _ecosystem_orchestrator
    if _ecosystem_orchestrator is None:
        _ecosystem_orchestrator = EcosystemOrchestrator(storage_path)
    return _ecosystem_orchestrator


# 修复asyncio导入
import asyncio

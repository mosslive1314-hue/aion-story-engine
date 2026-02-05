"""
Portal System - 传送门系统
管理世界间的传送门和连接
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid


class PortalType(Enum):
    """传送门类型"""
    PERMANENT = "permanent"  # 永久传送门
    TEMPORARY = "temporary"  # 临时传送门
    ONE_WAY = "one_way"  # 单向传送门
    TWO_WAY = "two_way"  # 双向传送门
    CONDITIONAL = "conditional"  # 条件传送门
    RANDOM = "random"  # 随机传送门
    DIMENSIONAL = "dimensional"  # 维度传送门


class PortalStatus(Enum):
    """传送门状态"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 不活跃
    LOCKED = "locked"  # 锁定
    BROKEN = "broken"  # 损坏
    CHARGING = "charging"  # 充能中


@dataclass
class PortalRule:
    """传送门规则"""
    require_item: Optional[str] = None  # 需要的物品
    require_quest: Optional[str] = None  # 需要的任务
    min_level: int = 0  # 最低等级
    cost_amount: float = 0.0  # 传送费用
    cost_currency: str = "gold"  # 费用货币类型
    cooldown_seconds: int = 0  # 冷却时间
    max_uses: int = -1  # 最大使用次数（-1为无限）
    required_faction: Optional[str] = None  # 需要的派系
    time_of_day: Optional[str] = None  # 特定时间（day, night, any）
    weather_condition: Optional[str] = None  # 天气条件

    def can_use(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """检查是否可以使用"""
        # 检查等级
        if user_data.get("level", 0) < self.min_level:
            return False, f"Requires level {self.min_level}"

        # 检查物品
        if self.require_item and self.require_item not in user_data.get("items", []):
            return False, f"Requires item: {self.require_item}"

        # 检查派系
        if self.required_faction and user_data.get("faction") != self.required_faction:
            return False, f"Requires faction: {self.required_faction}"

        return True, "OK"


@dataclass
class TransportEvent:
    """传送事件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    portal_id: str = ""
    entity_id: str = ""
    source_world_id: str = ""
    target_world_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "portal_id": self.portal_id,
            "entity_id": self.entity_id,
            "source_world_id": self.source_world_id,
            "target_world_id": self.target_world_id,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class Location:
    """位置"""
    world_id: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    region: Optional[str] = None
    instance_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "world_id": self.world_id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "region": self.region,
            "instance_id": self.instance_id
        }


class Portal:
    """传送门"""

    def __init__(
        self,
        name: str,
        source_location: Location,
        target_location: Location,
        portal_type: PortalType = PortalType.TWO_WAY
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.source_location = source_location
        self.target_location = target_location
        self.portal_type = portal_type

        # 状态
        self.status = PortalStatus.ACTIVE
        self.created_at = datetime.now()
        self.created_by = ""

        # 规则
        self.rules = PortalRule()

        # 使用统计
        self.total_uses = 0
        self.last_used: Optional[datetime] = None

        # 双向传送门的反向传送门
        self.reverse_portal_id: Optional[str] = None

        # 元数据
        self.description = ""
        self.visual_effect: str = "swirl"  # 视觉效果
        self.sound_effect: str = "portal_sound"  # 音效
        self.custom_attributes: Dict[str, Any] = {}

    def can_use(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """检查是否可以使用"""
        if self.status != PortalStatus.ACTIVE:
            return False, f"Portal is {self.status.value}"

        # 检查规则
        return self.rules.can_use(user_data)

    def use(self, entity_id: str, user_data: Dict[str, Any] = None) -> TransportEvent:
        """使用传送门"""
        event = TransportEvent(
            portal_id=self.id,
            entity_id=entity_id,
            source_world_id=self.source_location.world_id,
            target_world_id=self.target_location.world_id
        )

        # 检查是否可以使用
        if user_data:
            can_use, reason = self.can_use(user_data)
            if not can_use:
                event.success = False
                event.error_message = reason
                return event

        # 检查最大使用次数
        if self.rules.max_uses > 0 and self.total_uses >= self.rules.max_uses:
            event.success = False
            event.error_message = "Portal has reached maximum uses"
            return event

        # 成功传送
        self.total_uses += 1
        self.last_used = datetime.now()

        event.success = True
        return event

    def get_reverse_portal(self) -> Optional['Portal']:
        """获取反向传送门"""
        # 这个方法需要PortalManager支持
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "source_location": self.source_location.to_dict(),
            "target_location": self.target_location.to_dict(),
            "portal_type": self.portal_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "rules": {
                "require_item": self.rules.require_item,
                "require_quest": self.rules.require_quest,
                "min_level": self.rules.min_level,
                "cost_amount": self.rules.cost_amount,
                "cost_currency": self.rules.cost_currency,
                "cooldown_seconds": self.rules.cooldown_seconds,
                "max_uses": self.rules.max_uses,
                "required_faction": self.rules.required_faction,
                "time_of_day": self.rules.time_of_day,
                "weather_condition": self.rules.weather_condition
            },
            "total_uses": self.total_uses,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "reverse_portal_id": self.reverse_portal_id,
            "description": self.description,
            "visual_effect": self.visual_effect,
            "sound_effect": self.sound_effect
        }


class PortalManager:
    """传送门管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/portals.json"
        self.portals: Dict[str, Portal] = {}
        self.transport_events: List[TransportEvent] = []

        # 加载数据
        self._load_data()

    def create_portal(
        self,
        name: str,
        source_world_id: str,
        target_world_id: str,
        source_x: float = 0.0,
        source_y: float = 0.0,
        source_z: float = 0.0,
        target_x: float = 0.0,
        target_y: float = 0.0,
        target_z: float = 0.0,
        portal_type: PortalType = PortalType.TWO_WAY,
        created_by: str = "",
        description: str = ""
    ) -> Portal:
        """创建传送门"""
        source_location = Location(
            world_id=source_world_id,
            x=source_x,
            y=source_y,
            z=source_z
        )

        target_location = Location(
            world_id=target_world_id,
            x=target_x,
            y=target_y,
            z=target_z
        )

        portal = Portal(
            name=name,
            source_location=source_location,
            target_location=target_location,
            portal_type=portal_type
        )

        portal.description = description
        portal.created_by = created_by

        # 如果是双向传送门，自动创建反向传送门
        if portal_type == PortalType.TWO_WAY:
            reverse_portal = Portal(
                name=f"{name} (Reverse)",
                source_location=target_location,
                target_location=source_location,
                portal_type=PortalType.TWO_WAY
            )
            reverse_portal.created_by = created_by

            self.portals[reverse_portal.id] = reverse_portal
            portal.reverse_portal_id = reverse_portal.id
            reverse_portal.reverse_portal_id = portal.id

        # 添加到管理器
        self.portals[portal.id] = portal

        # 保存
        self._save_data()

        return portal

    def get_portal(self, portal_id: str) -> Optional[Portal]:
        """获取传送门"""
        return self.portals.get(portal_id)

    def update_portal(self, portal_id: str, **kwargs) -> bool:
        """更新传送门"""
        portal = self.get_portal(portal_id)
        if not portal:
            return False

        for key, value in kwargs.items():
            if hasattr(portal, key):
                setattr(portal, key, value)

        self._save_data()
        return True

    def delete_portal(self, portal_id: str) -> bool:
        """删除传送门"""
        if portal_id not in self.portals:
            return False

        portal = self.portals[portal_id]

        # 如果有反向传送门，也删除
        if portal.reverse_portal_id and portal.reverse_portal_id in self.portals:
            reverse = self.portals[portal.reverse_portal_id]
            del self.portals[portal.reverse_portal_id]
            reverse.reverse_portal_id = None

        # 删除传送门
        del self.portals[portal_id]

        self._save_data()
        return True

    def get_portals_from_world(self, world_id: str) -> List[Portal]:
        """获取从某世界出发的所有传送门"""
        return [
            portal for portal in self.portals.values()
            if portal.source_location.world_id == world_id
        ]

    def get_portals_to_world(self, world_id: str) -> List[Portal]:
        """获取到达某世界的所有传送门"""
        return [
            portal for portal in self.portals.values()
            if portal.target_location.world_id == world_id
        ]

    def get_portals_between_worlds(self, world_a: str, world_b: str) -> List[Portal]:
        """获取两个世界之间的所有传送门"""
        portals = []

        for portal in self.portals.values():
            if (portal.source_location.world_id == world_a and
                portal.target_location.world_id == world_b):
                portals.append(portal)
            elif (portal.source_location.world_id == world_b and
                  portal.target_location.world_id == world_a):
                portals.append(portal)

        return portals

    def transport(
        self,
        portal_id: str,
        entity_id: str,
        user_data: Dict[str, Any] = None
    ) -> TransportEvent:
        """通过传送门传送实体"""
        portal = self.get_portal(portal_id)
        if not portal:
            event = TransportEvent(
                portal_id=portal_id,
                entity_id=entity_id,
                source_world_id="",
                target_world_id=""
            )
            event.success = False
            event.error_message = "Portal not found"
            return event

        # 使用传送门
        event = portal.use(entity_id, user_data)

        # 记录事件
        self.transport_events.append(event)

        # 保存
        self._save_data()

        return event

    def get_transport_history(
        self,
        entity_id: Optional[str] = None,
        portal_id: Optional[str] = None,
        limit: int = 100
    ) -> List[TransportEvent]:
        """获取传送历史"""
        events = self.transport_events

        # 过滤
        if entity_id:
            events = [e for e in events if e.entity_id == entity_id]

        if portal_id:
            events = [e for e in events if e.portal_id == portal_id]

        # 按时间倒序
        events.sort(key=lambda e: e.timestamp, reverse=True)

        return events[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_portals = len(self.portals)

        portals_by_type = {}
        portals_by_status = {}

        for portal in self.portals.values():
            ptype = portal.portal_type.value
            portals_by_type[ptype] = portals_by_type.get(ptype, 0) + 1

            status = portal.status.value
            portals_by_status[status] = portals_by_status.get(status, 0) + 1

        total_transports = len(self.transport_events)
        successful_transports = sum(1 for e in self.transport_events if e.success)

        return {
            "total_portals": total_portals,
            "portals_by_type": portals_by_type,
            "portals_by_status": portals_by_status,
            "total_transports": total_transports,
            "successful_transports": successful_transports,
            "success_rate": successful_transports / total_transports if total_transports > 0 else 0.0
        }

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for portal_data in data.get("portals", []):
                source_loc_data = portal_data["source_location"]
                source_location = Location(
                    world_id=source_loc_data["world_id"],
                    x=source_loc_data["x"],
                    y=source_loc_data["y"],
                    z=source_loc_data["z"],
                    region=source_loc_data.get("region"),
                    instance_id=source_loc_data.get("instance_id")
                )

                target_loc_data = portal_data["target_location"]
                target_location = Location(
                    world_id=target_loc_data["world_id"],
                    x=target_loc_data["x"],
                    y=target_loc_data["y"],
                    z=target_loc_data["z"],
                    region=target_loc_data.get("region"),
                    instance_id=target_loc_data.get("instance_id")
                )

                portal = Portal(
                    name=portal_data["name"],
                    source_location=source_location,
                    target_location=target_location,
                    portal_type=PortalType(portal_data["portal_type"])
                )

                portal.id = portal_data["id"]
                portal.status = PortalStatus(portal_data.get("status", "active"))
                portal.created_at = datetime.fromisoformat(portal_data["created_at"])
                portal.created_by = portal_data.get("created_by", "")
                portal.description = portal_data.get("description", "")
                portal.total_uses = portal_data.get("total_uses", 0)
                portal.last_used = datetime.fromisoformat(portal_data["last_used"]) if portal_data.get("last_used") else None
                portal.reverse_portal_id = portal_data.get("reverse_portal_id")
                portal.visual_effect = portal_data.get("visual_effect", "swirl")
                portal.sound_effect = portal_data.get("sound_effect", "portal_sound")

                # 加载规则
                rules_data = portal_data.get("rules", {})
                portal.rules = PortalRule(
                    require_item=rules_data.get("require_item"),
                    require_quest=rules_data.get("require_quest"),
                    min_level=rules_data.get("min_level", 0),
                    cost_amount=rules_data.get("cost_amount", 0.0),
                    cost_currency=rules_data.get("cost_currency", "gold"),
                    cooldown_seconds=rules_data.get("cooldown_seconds", 0),
                    max_uses=rules_data.get("max_uses", -1),
                    required_faction=rules_data.get("required_faction"),
                    time_of_day=rules_data.get("time_of_day"),
                    weather_condition=rules_data.get("weather_condition")
                )

                self.portals[portal.id] = portal

            # 加载传送事件
            for event_data in data.get("transport_events", []):
                event = TransportEvent(
                    id=event_data["id"],
                    portal_id=event_data["portal_id"],
                    entity_id=event_data["entity_id"],
                    source_world_id=event_data["source_world_id"],
                    target_world_id=event_data["target_world_id"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    success=event_data["success"],
                    error_message=event_data.get("error_message"),
                    metadata=event_data.get("metadata", {})
                )
                self.transport_events.append(event)

        except Exception as e:
            print(f"Error loading portal data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "portals": [portal.to_dict() for portal in self.portals.values()],
                "transport_events": [event.to_dict() for event in self.transport_events[-1000:]],  # 只保留最近1000条
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving portal data: {e}")


# 全局传送门管理器实例
_portal_manager: Optional[PortalManager] = None


def get_portal_manager(storage_path: Optional[str] = None) -> PortalManager:
    """获取传送门管理器单例"""
    global _portal_manager
    if _portal_manager is None:
        _portal_manager = PortalManager(storage_path)
    return _portal_manager

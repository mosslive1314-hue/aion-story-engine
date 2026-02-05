"""
Multi-World Architecture - 多世界架构
管理多个宇宙、世界和区域的层级结构
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid


class WorldScale(Enum):
    """世界规模"""
    MULTIVERSE = "multiverse"  # 多元宇宙
    UNIVERSE = "universe"  # 宇宙
    GALAXY = "galaxy"  # 星系
    SOLAR_SYSTEM = "solar_system"  # 恒星系
    WORLD = "world"  # 世界（行星）
    REGION = "region"  # 区域
    LOCALITY = "locality"  # 地点
    INSTANCE = "instance"  # 实例


class WorldType(Enum):
    """世界类型"""
    FANTASY = "fantasy"  # 奇幻
    SCIFI = "scifi"  # 科幻
    MODERN = "modern"  # 现代
    HISTORICAL = "historical"  # 历史
    POST_APOCALYPTIC = "post_apocalyptic"  # 末世
    STEAMPUNK = "steampunk"  # 蒸汽朋克
    CYBERPUNK = "cyberpunk"  # 赛博朋克
    ABSTRACT = "abstract"  # 抽象
    CUSTOM = "custom"  # 自定义


class WorldStatus(Enum):
    """世界状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 活跃
    PAUSED = "paused"  # 暂停
    ARCHIVED = "archived"  # 归档
    DELETED = "deleted"  # 已删除


@dataclass
class PhysicsRules:
    """物理规则"""
    magic_enabled: bool = False
    magic_strength: float = 0.0  # 0-1
    technology_level: float = 0.5  # 0-1 (原始→超先进)
    physics_realism: float = 1.0  # 0-1 (完全真实→完全幻想)
    time_dilation: float = 1.0  # 时间流逝倍率
    gravity: float = 1.0  # 重力倍率
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "magic_enabled": self.magic_enabled,
            "magic_strength": self.magic_strength,
            "technology_level": self.technology_level,
            "physics_realism": self.physics_realism,
            "time_dilation": self.time_dilation,
            "gravity": self.gravity,
            "custom_rules": self.custom_rules
        }


@dataclass
class EconomicRules:
    """经济规则"""
    currency_system: str = "gold"  # 货币系统
    inflation_rate: float = 0.01  # 通胀率
    taxation_rate: float = 0.1  # 税率
    trade_enabled: bool = True
    market_type: str = "free"  # free, controlled, mixed
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "currency_system": self.currency_system,
            "inflation_rate": self.inflation_rate,
            "taxation_rate": self.taxation_rate,
            "trade_enabled": self.trade_enabled,
            "market_type": self.market_type,
            "custom_rules": self.custom_rules
        }


@dataclass
class SocialRules:
    """社会规则"""
    government_type: str = "monarchy"  # 政体类型
    law_level: float = 0.5  # 法律严格度
    social_hierarchy: bool = True  # 社会等级
    freedom_level: float = 0.5  # 自由度
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "government_type": self.government_type,
            "law_level": self.law_level,
            "social_hierarchy": self.social_hierarchy,
            "freedom_level": self.freedom_level,
            "custom_rules": self.custom_rules
        }


@dataclass
class WorldStatistics:
    """世界统计"""
    total_nodes: int = 0
    total_characters: int = 0
    total_stories: int = 0
    total_events: int = 0
    active_users: int = 0
    total_playtime_hours: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class World:
    """世界"""

    def __init__(
        self,
        name: str,
        world_type: WorldType,
        scale: WorldScale = WorldScale.WORLD,
        parent_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.world_type = world_type
        self.scale = scale
        self.parent_id = parent_id
        self.children: List[str] = []  # 子世界ID列表

        # 世界规则
        self.physics_rules = PhysicsRules()
        self.economic_rules = EconomicRules()
        self.social_rules = SocialRules()

        # 元数据
        self.description = ""
        self.tags: List[str] = []
        self.status = WorldStatus.DRAFT
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.created_by = ""

        # 统计信息
        self.statistics = WorldStatistics()

        # 设置
        self.settings: Dict[str, Any] = {}

    def add_child(self, world_id: str):
        """添加子世界"""
        if world_id not in self.children:
            self.children.append(world_id)

    def remove_child(self, world_id: str):
        """移除子世界"""
        if world_id in self.children:
            self.children.remove(world_id)

    def get_path(self) -> List[str]:
        """获取世界路径"""
        # 这个方法需要MultiverseManager支持来获取完整路径
        return [self.id]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "world_type": self.world_type.value,
            "scale": self.scale.value,
            "parent_id": self.parent_id,
            "children": self.children,
            "physics_rules": self.physics_rules.to_dict(),
            "economic_rules": self.economic_rules.to_dict(),
            "social_rules": self.social_rules.to_dict(),
            "description": self.description,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "statistics": {
                "total_nodes": self.statistics.total_nodes,
                "total_characters": self.statistics.total_characters,
                "total_stories": self.statistics.total_stories,
                "total_events": self.statistics.total_events,
                "active_users": self.statistics.active_users,
                "total_playtime_hours": self.statistics.total_playtime_hours
            },
            "settings": self.settings
        }


class MultiverseManager:
    """多元宇宙管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/multiverse.json"
        self.worlds: Dict[str, World] = {}

        # 加载数据
        self._load_data()

    def create_world(
        self,
        name: str,
        world_type: WorldType,
        scale: WorldScale = WorldScale.WORLD,
        parent_id: Optional[str] = None,
        created_by: str = "",
        description: str = ""
    ) -> World:
        """创建世界"""
        world = World(
            name=name,
            world_type=world_type,
            scale=scale,
            parent_id=parent_id
        )

        world.description = description
        world.created_by = created_by

        # 添加到管理器
        self.worlds[world.id] = world

        # 如果有父世界，添加到父世界的子列表
        if parent_id and parent_id in self.worlds:
            self.worlds[parent_id].add_child(world.id)

        # 保存
        self._save_data()

        return world

    def get_world(self, world_id: str) -> Optional[World]:
        """获取世界"""
        return self.worlds.get(world_id)

    def update_world(self, world_id: str, **kwargs) -> bool:
        """更新世界"""
        world = self.get_world(world_id)
        if not world:
            return False

        for key, value in kwargs.items():
            if hasattr(world, key):
                setattr(world, key, value)

        world.updated_at = datetime.now()
        self._save_data()
        return True

    def delete_world(self, world_id: str) -> bool:
        """删除世界"""
        if world_id not in self.worlds:
            return False

        world = self.worlds[world_id]

        # 递归删除所有子世界
        for child_id in world.children.copy():
            self.delete_world(child_id)

        # 从父世界的子列表中移除
        if world.parent_id and world.parent_id in self.worlds:
            self.worlds[world.parent_id].remove_child(world_id)

        # 删除世界
        del self.worlds[world_id]

        self._save_data()
        return True

    def get_children(self, world_id: str) -> List[World]:
        """获取子世界"""
        world = self.get_world(world_id)
        if not world:
            return []

        return [
            self.get_world(child_id)
            for child_id in world.children
            if child_id in self.worlds
        ]

    def get_path(self, world_id: str) -> List[World]:
        """获取从根到世界的路径"""
        path = []
        current = self.get_world(world_id)

        while current:
            path.insert(0, current)
            if current.parent_id:
                current = self.get_world(current.parent_id)
            else:
                break

        return path

    def get_tree(self, root_id: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """获取世界树"""
        if root_id:
            root = self.get_world(root_id)
        else:
            # 找到所有根世界（没有父世界的）
            roots = [w for w in self.worlds.values() if w.parent_id is None]
            root = roots[0] if roots else None

        if not root:
            return {}

        return self._build_tree(root, max_depth)

    def _build_tree(self, world: World, max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        """构建世界树"""
        node = {
            "id": world.id,
            "name": world.name,
            "type": world.world_type.value,
            "scale": world.scale.value,
            "status": world.status.value,
            "children": []
        }

        if current_depth < max_depth:
            for child_id in world.children:
                child = self.get_world(child_id)
                if child:
                    node["children"].append(self._build_tree(child, max_depth, current_depth + 1))

        return node

    def search_worlds(
        self,
        query: str = "",
        world_type: Optional[WorldType] = None,
        scale: Optional[WorldScale] = None,
        status: Optional[WorldStatus] = None,
        tags: List[str] = None,
        limit: int = 20
    ) -> List[World]:
        """搜索世界"""
        results = []

        for world in self.worlds.values():
            # 文本搜索
            if query:
                query_lower = query.lower()
                if (query_lower not in world.name.lower() and
                    query_lower not in world.description.lower()):
                    continue

            # 类型过滤
            if world_type and world.world_type != world_type:
                continue

            # 规模过滤
            if scale and world.scale != scale:
                continue

            # 状态过滤
            if status and world.status != status:
                continue

            # 标签过滤
            if tags and not any(tag in world.tags for tag in tags):
                continue

            results.append(world)

        return results[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_worlds = len(self.worlds)
        worlds_by_type = {}
        worlds_by_scale = {}
        worlds_by_status = {}

        for world in self.worlds.values():
            # 按类型统计
            wtype = world.world_type.value
            worlds_by_type[wtype] = worlds_by_type.get(wtype, 0) + 1

            # 按规模统计
            scale = world.scale.value
            worlds_by_scale[scale] = worlds_by_scale.get(scale, 0) + 1

            # 按状态统计
            status = world.status.value
            worlds_by_status[status] = worlds_by_status.get(status, 0) + 1

        # 计算总统计
        total_nodes = sum(w.statistics.total_nodes for w in self.worlds.values())
        total_characters = sum(w.statistics.total_characters for w in self.worlds.values())
        total_stories = sum(w.statistics.total_stories for w in self.worlds.values())

        return {
            "total_worlds": total_worlds,
            "worlds_by_type": worlds_by_type,
            "worlds_by_scale": worlds_by_scale,
            "worlds_by_status": worlds_by_status,
            "total_nodes": total_nodes,
            "total_characters": total_characters,
            "total_stories": total_stories
        }

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for world_data in data.get("worlds", []):
                world = World(
                    name=world_data["name"],
                    world_type=WorldType(world_data["world_type"]),
                    scale=WorldScale(world_data["scale"]),
                    parent_id=world_data.get("parent_id")
                )

                world.id = world_data["id"]
                world.description = world_data.get("description", "")
                world.tags = world_data.get("tags", [])
                world.status = WorldStatus(world_data.get("status", "draft"))
                world.created_at = datetime.fromisoformat(world_data["created_at"])
                world.updated_at = datetime.fromisoformat(world_data["updated_at"])
                world.created_by = world_data.get("created_by", "")
                world.children = world_data.get("children", [])

                # 加载规则
                physics_data = world_data.get("physics_rules", {})
                world.physics_rules = PhysicsRules(
                    magic_enabled=physics_data.get("magic_enabled", False),
                    magic_strength=physics_data.get("magic_strength", 0.0),
                    technology_level=physics_data.get("technology_level", 0.5),
                    physics_realism=physics_data.get("physics_realism", 1.0),
                    time_dilation=physics_data.get("time_dilation", 1.0),
                    gravity=physics_data.get("gravity", 1.0),
                    custom_rules=physics_data.get("custom_rules", {})
                )

                economic_data = world_data.get("economic_rules", {})
                world.economic_rules = EconomicRules(
                    currency_system=economic_data.get("currency_system", "gold"),
                    inflation_rate=economic_data.get("inflation_rate", 0.01),
                    taxation_rate=economic_data.get("taxation_rate", 0.1),
                    trade_enabled=economic_data.get("trade_enabled", True),
                    market_type=economic_data.get("market_type", "free"),
                    custom_rules=economic_data.get("custom_rules", {})
                )

                social_data = world_data.get("social_rules", {})
                world.social_rules = SocialRules(
                    government_type=social_data.get("government_type", "monarchy"),
                    law_level=social_data.get("law_level", 0.5),
                    social_hierarchy=social_data.get("social_hierarchy", True),
                    freedom_level=social_data.get("freedom_level", 0.5),
                    custom_rules=social_data.get("custom_rules", {})
                )

                # 加载统计
                stats_data = world_data.get("statistics", {})
                world.statistics = WorldStatistics(
                    total_nodes=stats_data.get("total_nodes", 0),
                    total_characters=stats_data.get("total_characters", 0),
                    total_stories=stats_data.get("total_stories", 0),
                    total_events=stats_data.get("total_events", 0),
                    active_users=stats_data.get("active_users", 0),
                    total_playtime_hours=stats_data.get("total_playtime_hours", 0.0)
                )

                world.settings = world_data.get("settings", {})

                self.worlds[world.id] = world

        except Exception as e:
            print(f"Error loading multiverse data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "worlds": [world.to_dict() for world in self.worlds.values()],
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving multiverse data: {e}")


# 全局多元宇宙管理器实例
_multiverse_manager: Optional[MultiverseManager] = None


def get_multiverse_manager(storage_path: Optional[str] = None) -> MultiverseManager:
    """获取多元宇宙管理器单例"""
    global _multiverse_manager
    if _multiverse_manager is None:
        _multiverse_manager = MultiverseManager(storage_path)
    return _multiverse_manager

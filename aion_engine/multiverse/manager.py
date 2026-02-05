from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Universe:
    """多元宇宙中的单个宇宙"""
    universe_id: str
    name: str
    creator_id: str
    description: str
    physics_rules: Dict[str, Any]
    theme: str
    tags: List[str] = field(default_factory=list)
    connected_universes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_public: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_connection(self, target_universe_id: str):
        """添加宇宙连接"""
        if target_universe_id not in self.connected_universes:
            self.connected_universes.append(target_universe_id)
            self.updated_at = datetime.now()

    def remove_connection(self, target_universe_id: str):
        """移除宇宙连接"""
        if target_universe_id in self.connected_universes:
            self.connected_universes.remove(target_universe_id)
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'universe_id': self.universe_id,
            'name': self.name,
            'creator_id': self.creator_id,
            'description': self.description,
            'physics_rules': self.physics_rules,
            'theme': self.theme,
            'tags': self.tags,
            'connected_universes': self.connected_universes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_public': self.is_public,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Universe':
        """从字典创建实例"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class World:
    """宇宙中的世界"""
    world_id: str
    universe_id: str
    name: str
    description: str
    regions: List[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'world_id': self.world_id,
            'universe_id': self.universe_id,
            'name': self.name,
            'description': self.description,
            'regions': self.regions,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """从字典创建实例"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class UniverseConnection:
    """宇宙间的连接"""
    connection_id: str
    source_universe_id: str
    target_universe_id: str
    connection_type: str  # 'portal', 'wormhole', 'reference'
    creator_id: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'connection_id': self.connection_id,
            'source_universe_id': self.source_universe_id,
            'target_universe_id': self.target_universe_id,
            'connection_type': self.connection_type,
            'creator_id': self.creator_id,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniverseConnection':
        """从字典创建实例"""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class MultiverseManager:
    """多元宇宙管理器"""

    def __init__(self):
        self.universes: Dict[str, Universe] = {}
        self.worlds: Dict[str, World] = {}
        self.connections: Dict[str, UniverseConnection] = {}

    def create_universe(
        self,
        name: str,
        creator_id: str,
        description: str,
        physics_rules: Dict[str, Any],
        theme: str,
        is_public: bool = True,
        tags: Optional[List[str]] = None,
    ) -> Universe:
        """创建新宇宙"""
        universe_id = str(uuid.uuid4())
        universe = Universe(
            universe_id=universe_id,
            name=name,
            creator_id=creator_id,
            description=description,
            physics_rules=physics_rules,
            theme=theme,
            tags=tags or [],
            is_public=is_public,
        )
        self.universes[universe_id] = universe
        return universe

    def create_world(
        self,
        universe_id: str,
        name: str,
        created_by: str,
        description: str,
        regions: Optional[List[str]] = None,
    ) -> Optional[World]:
        """在宇宙中创建世界"""
        if universe_id not in self.universes:
            return None

        world_id = str(uuid.uuid4())
        world = World(
            world_id=world_id,
            universe_id=universe_id,
            name=name,
            description=description,
            regions=regions or [],
            created_by=created_by,
        )
        self.worlds[world_id] = world
        return world

    def create_connection(
        self,
        source_universe_id: str,
        target_universe_id: str,
        creator_id: str,
        connection_type: str,
        description: str,
    ) -> Optional[UniverseConnection]:
        """创建宇宙连接"""
        if source_universe_id not in self.universes or target_universe_id not in self.universes:
            return None

        connection_id = str(uuid.uuid4())
        connection = UniverseConnection(
            connection_id=connection_id,
            source_universe_id=source_universe_id,
            target_universe_id=target_universe_id,
            connection_type=connection_type,
            creator_id=creator_id,
            description=description,
        )
        self.connections[connection_id] = connection

        # 双向连接
        self.universes[source_universe_id].add_connection(target_universe_id)
        self.universes[target_universe_id].add_connection(source_universe_id)

        return connection

    def get_universe(self, universe_id: str) -> Optional[Universe]:
        """获取宇宙"""
        return self.universes.get(universe_id)

    def get_universe_worlds(self, universe_id: str) -> List[World]:
        """获取宇宙中的所有世界"""
        return [w for w in self.worlds.values() if w.universe_id == universe_id]

    def get_universe_connections(self, universe_id: str) -> List[UniverseConnection]:
        """获取宇宙的连接"""
        return [
            c for c in self.connections.values()
            if c.source_universe_id == universe_id or c.target_universe_id == universe_id
        ]

    def search_universes(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        creator_id: Optional[str] = None,
    ) -> List[Universe]:
        """搜索宇宙"""
        results = list(self.universes.values())

        if query:
            query = query.lower()
            results = [
                u for u in results
                if query in u.name.lower() or query in u.description.lower()
            ]

        if tags:
            results = [u for u in results if any(tag in u.tags for tag in tags)]

        if creator_id:
            results = [u for u in results if u.creator_id == creator_id]

        return results

    def get_recommended_universes(self, universe_id: str, limit: int = 5) -> List[Universe]:
        """获取推荐宇宙"""
        if universe_id not in self.universes:
            return []

        universe = self.universes[universe_id]
        candidates = [
            u for u in self.universes.values()
            if u.universe_id != universe_id and u.is_public
        ]

        # 基于标签和主题的推荐
        scored = []
        for candidate in candidates:
            score = 0

            # 相同标签
            score += len(set(universe.tags) & set(candidate.tags)) * 2

            # 相同主题
            if universe.theme == candidate.theme:
                score += 3

            # 已连接宇宙的推荐
            if candidate.universe_id in universe.connected_universes:
                score += 5

            scored.append((candidate, score))

        # 按分数排序
        scored.sort(key=lambda x: x[1], reverse=True)

        return [u for u, _ in scored[:limit]]

    def delete_universe(self, universe_id: str) -> bool:
        """删除宇宙及其所有世界和连接"""
        if universe_id not in self.universes:
            return False

        # 删除世界
        worlds_to_delete = [w.world_id for w in self.get_universe_worlds(universe_id)]
        for world_id in worlds_to_delete:
            del self.worlds[world_id]

        # 删除连接
        connections_to_delete = [
            c.connection_id for c in self.get_universe_connections(universe_id)
        ]
        for connection_id in connections_to_delete:
            del self.connections[connection_id]

        # 删除宇宙
        del self.universes[universe_id]

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """获取多元宇宙统计信息"""
        return {
            'total_universes': len(self.universes),
            'total_worlds': len(self.worlds),
            'total_connections': len(self.connections),
            'public_universes': sum(1 for u in self.universes.values() if u.is_public),
            'private_universes': sum(1 for u in self.universes.values() if not u.is_public),
            'themes': list(set(u.theme for u in self.universes.values())),
            'top_tags': self._get_top_tags(10),
        }

    def _get_top_tags(self, limit: int) -> List[str]:
        """获取热门标签"""
        tag_counts = {}
        for universe in self.universes.values():
            for tag in universe.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:limit]]

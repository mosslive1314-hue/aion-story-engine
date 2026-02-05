from datetime import datetime
import pytest
from aion_engine.multiverse import MultiverseManager, Universe, World, UniverseConnection


@pytest.fixture
def multiverse():
    """创建测试用的多元宇宙管理器"""
    return MultiverseManager()


def test_create_universe(multiverse):
    """测试创建宇宙"""
    universe = multiverse.create_universe(
        name="Test Universe",
        creator_id="alice",
        description="A test universe",
        physics_rules={"gravity": 9.8, "thermodynamics": True},
        theme="cyberpunk",
    )

    assert universe.universe_id is not None
    assert universe.name == "Test Universe"
    assert universe.creator_id == "alice"
    assert universe.physics_rules["gravity"] == 9.8
    assert universe.theme == "cyberpunk"
    assert universe.is_public is True


def test_create_world(multiverse):
    """测试创建世界"""
    universe = multiverse.create_universe(
        name="Test Universe",
        creator_id="alice",
        description="A test universe",
        physics_rules={},
        theme="fantasy",
    )

    world = multiverse.create_world(
        universe_id=universe.universe_id,
        name="Middle Earth",
        created_by="alice",
        description="A fantasy world",
        regions=["Shire", "Mordor", "Gondor"],
    )

    assert world.world_id is not None
    assert world.universe_id == universe.universe_id
    assert world.name == "Middle Earth"
    assert "Shire" in world.regions


def test_create_connection(multiverse):
    """测试创建宇宙连接"""
    universe1 = multiverse.create_universe(
        name="Universe 1",
        creator_id="alice",
        description="First universe",
        physics_rules={},
        theme="fantasy",
    )

    universe2 = multiverse.create_universe(
        name="Universe 2",
        creator_id="bob",
        description="Second universe",
        physics_rules={},
        theme="sci-fi",
    )

    connection = multiverse.create_connection(
        source_universe_id=universe1.universe_id,
        target_universe_id=universe2.universe_id,
        creator_id="alice",
        connection_type="portal",
        description="A magical portal connects these universes",
    )

    assert connection.connection_id is not None
    assert connection.source_universe_id == universe1.universe_id
    assert connection.target_universe_id == universe2.universe_id
    assert connection.connection_type == "portal"

    # 验证双向连接
    universe1_updated = multiverse.get_universe(universe1.universe_id)
    assert universe2.universe_id in universe1_updated.connected_universes


def test_get_universe_worlds(multiverse):
    """测试获取宇宙中的世界"""
    universe = multiverse.create_universe(
        name="Test Universe",
        creator_id="alice",
        description="A test universe",
        physics_rules={},
        theme="fantasy",
    )

    # 创建多个世界
    world1 = multiverse.create_world(
        universe_id=universe.universe_id,
        name="World 1",
        created_by="alice",
        description="First world",
    )

    world2 = multiverse.create_world(
        universe_id=universe.universe_id,
        name="World 2",
        created_by="bob",
        description="Second world",
    )

    worlds = multiverse.get_universe_worlds(universe.universe_id)

    assert len(worlds) == 2
    assert any(w.name == "World 1" for w in worlds)
    assert any(w.name == "World 2" for w in worlds)


def test_search_universes(multiverse):
    """测试搜索宇宙"""
    # 创建不同类型的宇宙
    multiverse.create_universe(
        name="Cyberpunk City",
        creator_id="alice",
        description="A futuristic cyberpunk setting",
        physics_rules={},
        theme="cyberpunk",
        tags=["cyber", "future"],
    )

    multiverse.create_universe(
        name="Medieval Kingdom",
        creator_id="bob",
        description="A medieval fantasy kingdom",
        physics_rules={},
        theme="fantasy",
        tags=["fantasy", "medieval"],
    )

    # 搜索
    results = multiverse.search_universes(query="cyber")
    assert len(results) == 1
    assert results[0].name == "Cyberpunk City"

    # 按主题搜索
    results = multiverse.search_universes(tags=["fantasy"])
    assert len(results) == 1
    assert results[0].name == "Medieval Kingdom"

    # 按创建者搜索
    results = multiverse.search_universes(creator_id="alice")
    assert len(results) == 1
    assert results[0].name == "Cyberpunk City"


def test_get_recommended_universes(multiverse):
    """测试获取推荐宇宙"""
    universe1 = multiverse.create_universe(
        name="Fantasy World 1",
        creator_id="alice",
        description="A fantasy universe",
        physics_rules={},
        theme="fantasy",
        tags=["magic", "dragons"],
    )

    universe2 = multiverse.create_universe(
        name="Fantasy World 2",
        creator_id="bob",
        description="Another fantasy universe",
        physics_rules={},
        theme="fantasy",
        tags=["magic", "elves"],
    )

    universe3 = multiverse.create_universe(
        name="Sci-Fi World",
        creator_id="charlie",
        description="A science fiction universe",
        physics_rules={},
        theme="sci-fi",
        tags=["spaceships", "robots"],
    )

    # 连接宇宙1和宇宙2
    multiverse.create_connection(
        source_universe_id=universe1.universe_id,
        target_universe_id=universe2.universe_id,
        creator_id="alice",
        connection_type="portal",
        description="Connected worlds",
    )

    # 获取推荐
    recommendations = multiverse.get_recommended_universes(universe1.universe_id, limit=10)

    # 宇宙2应该有更高的推荐分数（相同主题 + 已连接）
    assert len(recommendations) >= 1
    assert universe2.universe_id in [u.universe_id for u in recommendations]


def test_delete_universe(multiverse):
    """测试删除宇宙"""
    universe = multiverse.create_universe(
        name="Test Universe",
        creator_id="alice",
        description="A test universe",
        physics_rules={},
        theme="fantasy",
    )

    world = multiverse.create_world(
        universe_id=universe.universe_id,
        name="Test World",
        created_by="alice",
        description="A test world",
    )

    universe2 = multiverse.create_universe(
        name="Another Universe",
        creator_id="bob",
        description="Another universe",
        physics_rules={},
        theme="sci-fi",
    )

    multiverse.create_connection(
        source_universe_id=universe.universe_id,
        target_universe_id=universe2.universe_id,
        creator_id="alice",
        connection_type="portal",
        description="Connection",
    )

    # 验证存在
    assert universe.universe_id in multiverse.universes
    assert world.world_id in multiverse.worlds

    # 删除宇宙
    success = multiverse.delete_universe(universe.universe_id)
    assert success is True

    # 验证删除
    assert universe.universe_id not in multiverse.universes
    assert world.world_id not in multiverse.worlds
    assert universe2.universe_id in multiverse.universes  # 其他宇宙未受影响


def test_get_statistics(multiverse):
    """测试获取统计信息"""
    # 创建多个宇宙
    multiverse.create_universe(
        name="Fantasy World",
        creator_id="alice",
        description="A fantasy universe",
        physics_rules={},
        theme="fantasy",
        tags=["magic", "dragons"],
    )

    multiverse.create_universe(
        name="Sci-Fi World",
        creator_id="bob",
        description="A sci-fi universe",
        physics_rules={},
        theme="sci-fi",
        tags=["spaceships"],
    )

    multiverse.create_universe(
        name="Private World",
        creator_id="charlie",
        description="A private universe",
        physics_rules={},
        theme="horror",
        is_public=False,
    )

    stats = multiverse.get_statistics()

    assert stats['total_universes'] == 3
    assert stats['total_worlds'] == 0
    assert stats['total_connections'] == 0
    assert stats['public_universes'] == 2
    assert stats['private_universes'] == 1
    assert 'fantasy' in stats['themes']
    assert 'sci-fi' in stats['themes']
    assert 'horror' in stats['themes']
    assert 'magic' in stats['top_tags']


def test_universe_to_dict(multiverse):
    """测试宇宙转换为字典"""
    universe = multiverse.create_universe(
        name="Test Universe",
        creator_id="alice",
        description="A test universe",
        physics_rules={"gravity": 9.8},
        theme="cyberpunk",
        tags=["future", "neon"],
    )

    data = universe.to_dict()

    assert data['name'] == "Test Universe"
    assert data['creator_id'] == "alice"
    assert data['physics_rules']['gravity'] == 9.8
    assert 'created_at' in data
    assert 'updated_at' in data
    assert isinstance(data['created_at'], str)


def test_universe_from_dict(multiverse):
    """测试从字典创建宇宙"""
    data = {
        'universe_id': 'test-id',
        'name': 'Test Universe',
        'creator_id': 'alice',
        'description': 'A test universe',
        'physics_rules': {"gravity": 9.8},
        'theme': 'cyberpunk',
        'tags': ['future'],
        'connected_universes': [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'is_public': True,
        'metadata': {},
    }

    universe = Universe.from_dict(data)

    assert universe.universe_id == 'test-id'
    assert universe.name == 'Test Universe'
    assert isinstance(universe.created_at, datetime)

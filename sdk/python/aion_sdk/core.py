"""
AION Story Engine Python SDK

一个用于与 AION Story Engine API 交互的 Python SDK
"""

import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class Session:
    """故事会话数据类"""
    session_id: str
    name: str
    status: str
    message: Optional[str] = None


@dataclass
class Asset:
    """创作资产数据类"""
    id: str
    name: str
    type: str
    price: float
    creator: Optional[str] = None
    rating: Optional[float] = None
    downloads: Optional[int] = None


@dataclass
class Universe:
    """多元宇宙数据类"""
    universe_id: str
    name: str
    creator_id: str
    description: str
    physics_rules: Dict[str, Any]
    theme: str
    tags: List[str]
    created_at: str
    is_public: bool


@dataclass
class Proposal:
    """治理提案数据类"""
    proposal_id: str
    title: str
    description: str
    proposal_type: str
    proposer_id: str
    created_at: str
    voting_period_days: int
    status: str
    votes_for: int
    votes_against: int
    votes_abstain: int


class AionClient:
    """AION Story Engine API 客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: int = 30
    ):
        """
        初始化客户端

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点

        Returns:
            响应 JSON 数据

        Raises:
            requests.exceptions.RequestException: 请求失败时抛出
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            timeout=self.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    # ========== 会话管理 ==========

    def create_session(self, name: str, owner_id: Optional[str] = None) -> Session:
        """
        创建新的故事会话

        Args:
            name: 会话名称
            owner_id: 所有者 ID

        Returns:
            Session 对象
        """
        data = {"name": name}
        if owner_id:
            data["owner_id"] = owner_id

        response = self._request("POST", "/sessions", json=data)
        return Session(**response)

    def get_session(self, session_id: str) -> Session:
        """
        获取指定的故事会话

        Args:
            session_id: 会话 ID

        Returns:
            Session 对象
        """
        response = self._request("GET", f"/sessions/{session_id}")
        return Session(**response)

    def list_sessions(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """
        列示所有故事会话

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            Session 对象列表
        """
        params = {"skip": skip, "limit": limit}
        response = self._request("GET", "/sessions", params=params)
        return [Session(**item) for item in response.get("sessions", [])]

    # ========== 资产管理 ==========

    def list_assets(
        self,
        skip: int = 0,
        limit: int = 100,
        asset_type: Optional[str] = None
    ) -> List[Asset]:
        """
        列示所有创作资产

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            asset_type: 资产类型过滤

        Returns:
            Asset 对象列表
        """
        params = {"skip": skip, "limit": limit}
        if asset_type:
            params["asset_type"] = asset_type

        response = self._request("GET", "/assets", params=params)
        return [Asset(**item) for item in response.get("assets", [])]

    # ========== 市场 ==========

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """
        获取创作者市场统计数据

        Returns:
            统计数据字典
        """
        return self._request("GET", "/marketplace/stats")

    def list_marketplace_assets(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        列示市场中的所有资产

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            Asset 对象列表
        """
        params = {"skip": skip, "limit": limit}
        response = self._request("GET", "/marketplace/assets", params=params)
        return [Asset(**item) for item in response.get("assets", [])]

    # ========== 多元宇宙 ==========

    def create_universe(
        self,
        name: str,
        creator_id: str,
        description: str,
        physics_rules: Dict[str, Any],
        theme: str,
        tags: Optional[List[str]] = None,
        is_public: bool = True
    ) -> Universe:
        """
        创建新的多元宇宙

        Args:
            name: 宇宙名称
            creator_id: 创建者 ID
            description: 宇宙描述
            physics_rules: 物理规则
            theme: 主题
            tags: 标签列表
            is_public: 是否公开

        Returns:
            Universe 对象
        """
        data = {
            "name": name,
            "creator_id": creator_id,
            "description": description,
            "physics_rules": physics_rules,
            "theme": theme,
            "is_public": is_public
        }
        if tags:
            data["tags"] = tags

        response = self._request("POST", "/universes", json=data)
        return Universe(**response)

    def list_universes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Universe]:
        """
        列示所有多元宇宙

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            Universe 对象列表
        """
        params = {"skip": skip, "limit": limit}
        response = self._request("GET", "/universes", params=params)
        return [Universe(**item) for item in response]

    # ========== 治理 ==========

    def list_proposals(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Proposal]:
        """
        列示所有治理提案

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            status: 状态过滤

        Returns:
            Proposal 对象列表
        """
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status

        response = self._request("GET", "/governance/proposals", params=params)
        return [Proposal(**item) for item in response]

    # ========== 辅助方法 ==========

    def health_check(self) -> Dict[str, Any]:
        """
        执行健康检查

        Returns:
            健康状态信息
        """
        url = f"{self.base_url.replace('/api/v1', '')}/health"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()


# 便捷函数
def create_client(api_key: str, **kwargs) -> AionClient:
    """
    创建 AION 客户端实例的便捷函数

    Args:
        api_key: API 密钥
        **kwargs: 其他传递给 AionClient 的参数

    Returns:
        AionClient 实例
    """
    return AionClient(api_key=api_key, **kwargs)


# 示例用法
if __name__ == "__main__":
    import os

    # 从环境变量获取 API Key（推荐）
    API_KEY = os.getenv("AION_API_KEY", "test_api_key")
    BASE_URL = os.getenv("AION_API_URL", "http://localhost:8000/api/v1")

    # 创建客户端
    client = AionClient(api_key=API_KEY, base_url=BASE_URL)

    print("🌌 AION Story Engine Python SDK 示例")
    print("=" * 60)

    # 健康检查
    try:
        health = client.health_check()
        print(f"✅ 健康检查: {health['status']}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        print("请确保 API 服务器正在运行：python start_api.py")

    # 示例 1: 创建故事会话
    print("\n📝 示例 1: 创建故事会话")
    try:
        session = client.create_session(name="我的第一个故事", owner_id="user123")
        print(f"✅ 会话创建成功: {session.session_id}")
        print(f"   名称: {session.name}")
        print(f"   状态: {session.status}")
    except Exception as e:
        print(f"❌ 创建会话失败: {e}")

    # 示例 2: 列示会话
    print("\n📋 示例 2: 列示故事会话")
    try:
        sessions = client.list_sessions(limit=5)
        print(f"✅ 找到 {len(sessions)} 个会话")
        for s in sessions:
            print(f"   - {s.name} ({s.status})")
    except Exception as e:
        print(f"❌ 列示会话失败: {e}")

    # 示例 3: 列示资产
    print("\n🎨 示例 3: 列示创作资产")
    try:
        assets = client.list_assets(limit=5)
        print(f"✅ 找到 {len(assets)} 个资产")
        for asset in assets:
            price = "免费" if asset.price == 0 else f"${asset.price:.2f}"
            print(f"   - {asset.name} - {price}")
    except Exception as e:
        print(f"❌ 列示资产失败: {e}")

    # 示例 4: 列示宇宙
    print("\n🌍 示例 4: 列示多元宇宙")
    try:
        universes = client.list_universes(limit=5)
        print(f"✅ 找到 {len(universes)} 个宇宙")
        for u in universes:
            print(f"   - {u.name} ({u.theme})")
    except Exception as e:
        print(f"❌ 列示宇宙失败: {e}")

    # 示例 5: 创建宇宙
    print("\n✨ 示例 5: 创建新宇宙")
    try:
        universe = client.create_universe(
            name="科幻世界",
            creator_id="user123",
            description="一个充满星际冒险的科幻宇宙",
            physics_rules={
                "gravity": 9.8,
                "faster_than_light": True,
                "energy_conservation": "quantum"
            },
            theme="sci-fi",
            tags=["space", "adventure", "future"]
        )
        print(f"✅ 宇宙创建成功: {universe.universe_id}")
        print(f"   名称: {universe.name}")
        print(f"   主题: {universe.theme}")
    except Exception as e:
        print(f"❌ 创建宇宙失败: {e}")

    # 示例 6: 列示治理提案
    print("\n🗳️ 示例 6: 列示治理提案")
    try:
        proposals = client.list_proposals(limit=5)
        print(f"✅ 找到 {len(proposals)} 个提案")
        for p in proposals:
            print(f"   - {p.title} ({p.status})")
    except Exception as e:
        print(f"❌ 列示提案失败: {e}")

    print("\n" + "=" * 60)
    print("🎉 示例运行完成！")
    print("=" * 60)

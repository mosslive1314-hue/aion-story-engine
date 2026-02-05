"""
Creator Economy - 创作者经济系统
实现资产市场、交易、评分和收益分配
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid


class AssetStatus(Enum):
    """资产状态"""
    DRAFT = "draft"  # 草稿
    REVIEW = "review"  # 审核中
    APPROVED = "approved"  # 已批准
    PUBLISHED = "published"  # 已发布
    REMOVED = "removed"  # 已移除


class TransactionType(Enum):
    """交易类型"""
    PURCHASE = "purchase"  # 购买
    SALE = "sale"  # 销售
    ROYALTY = "royalty"  # 版税
    REFUND = "refund"  # 退款
    TIP = "tip"  # 打赏


class LicenseType(Enum):
    """许可类型"""
    PERSONAL = "personal"  # 个人使用
    COMMERCIAL = "commercial"  # 商业使用
    EXCLUSIVE = "exclusive"  # 独家许可
    ROYALTY_FREE = "royalty_free"  # 免版税
    CREATIVE_COMMONS = "creative_commons"  # 知识共享


@dataclass
class CreatorProfile:
    """创作者档案"""
    id: str
    user_id: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    social_links: Dict[str, str] = field(default_factory=dict)
    total_sales: float = 0.0
    total_revenue: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    follower_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    verified: bool = False


@dataclass
class MarketplaceAsset:
    """市场资产"""
    id: str
    creator_id: str
    asset_type: str
    name: str
    description: str
    price: float
    status: AssetStatus = AssetStatus.DRAFT
    license_type: LicenseType = LicenseType.PERSONAL
    tags: List[str] = field(default_factory=list)
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    view_count: int = 0
    purchase_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Review:
    """评价"""
    id: str
    asset_id: str
    user_id: str
    rating: int  # 1-5
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    helpful_count: int = 0
    verified_purchase: bool = False


@dataclass
class Transaction:
    """交易"""
    id: str
    transaction_type: TransactionType
    asset_id: str
    buyer_id: str
    seller_id: str
    amount: float
    platform_fee: float = 0.0
    royalty_amount: float = 0.0
    status: str = "pending"  # pending, completed, cancelled, refunded
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueShare:
    """收益分配"""
    id: str
    transaction_id: str
    recipient_id: str
    share_type: str  # creator, platform, referrer
    share_percentage: float
    amount: float
    status: str = "pending"  # pending, paid
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None


class Marketplace:
    """市场主类"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/marketplace.json"
        self.assets: Dict[str, MarketplaceAsset] = {}
        self.reviews: Dict[str, Review] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}

        # 平台费用配置
        self.platform_fee_rate = 0.15  # 15% 平台费用
        self.royalty_rate = 0.10  # 10% 版税

        self._load_data()

    def create_creator_profile(self, user_id: str, display_name: str, bio: str = "") -> CreatorProfile:
        """创建创作者档案"""
        profile = CreatorProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            display_name=display_name,
            bio=bio
        )

        self.creator_profiles[profile.id] = profile
        self._save_data()
        return profile

    def get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """获取创作者档案"""
        return self.creator_profiles.get(creator_id)

    def update_creator_stats(self, creator_id: str, sale_amount: float):
        """更新创作者统计"""
        profile = self.creator_profiles.get(creator_id)
        if profile:
            profile.total_sales += 1
            profile.total_revenue += sale_amount

            # 更新评分
            asset_reviews = [r for r in self.reviews.values()
                           if any(a.creator_id == creator_id for a in self.assets.values() if a.id == r.asset_id)]

            if asset_reviews:
                profile.rating = sum(r.rating for r in asset_reviews) / len(asset_reviews)
                profile.review_count = len(asset_reviews)

            self._save_data()

    def publish_asset(
        self,
        creator_id: str,
        asset_type: str,
        name: str,
        description: str,
        price: float,
        license_type: LicenseType = LicenseType.PERSONAL,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[MarketplaceAsset]:
        """发布资产"""
        creator = self.creator_profiles.get(creator_id)
        if not creator:
            return None

        asset = MarketplaceAsset(
            id=str(uuid.uuid4()),
            creator_id=creator_id,
            asset_type=asset_type,
            name=name,
            description=description,
            price=price,
            license_type=license_type,
            tags=tags or [],
            status=AssetStatus.REVIEW,
            metadata=metadata or {}
        )

        self.assets[asset.id] = asset
        self._save_data()
        return asset

    def approve_asset(self, asset_id: str) -> bool:
        """批准资产"""
        asset = self.assets.get(asset_id)
        if not asset:
            return False

        asset.status = AssetStatus.PUBLISHED
        self._save_data()
        return True

    def search_assets(
        self,
        query: str = "",
        asset_type: str = "",
        tags: List[str] = None,
        min_price: float = 0,
        max_price: float = float('inf'),
        min_rating: float = 0,
        sort_by: str = "relevance",  # relevance, price_asc, price_desc, rating, newest
        limit: int = 20
    ) -> List[MarketplaceAsset]:
        """搜索资产"""
        results = []

        for asset in self.assets.values():
            if asset.status != AssetStatus.PUBLISHED:
                continue

            # 文本搜索
            if query:
                query_lower = query.lower()
                if (query_lower not in asset.name.lower() and
                    query_lower not in asset.description.lower()):
                    continue

            # 类型过滤
            if asset_type and asset.asset_type != asset_type:
                continue

            # 标签过滤
            if tags and not any(tag in asset.tags for tag in tags):
                continue

            # 价格过滤
            if not (min_price <= asset.price <= max_price):
                continue

            # 评分过滤
            if asset.rating < min_rating:
                continue

            results.append(asset)

        # 排序
        if sort_by == "price_asc":
            results.sort(key=lambda a: a.price)
        elif sort_by == "price_desc":
            results.sort(key=lambda a: a.price, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda a: a.rating, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda a: a.created_at, reverse=True)
        else:  # relevance
            # 简单相关性：匹配度 = 评分 + 购买数权重
            results.sort(key=lambda a: a.rating * 2 + a.purchase_count, reverse=True)

        return results[:limit]

    def get_trending_assets(self, limit: int = 10) -> List[MarketplaceAsset]:
        """获取热门资产"""
        published = [a for a in self.assets.values() if a.status == AssetStatus.PUBLISHED]

        # 按购买量和评分排序
        published.sort(key=lambda a: a.purchase_count * 10 + a.rating * 5, reverse=True)
        return published[:limit]

    def purchase_asset(self, asset_id: str, buyer_id: str) -> Optional[Transaction]:
        """购买资产"""
        asset = self.assets.get(asset_id)
        if not asset or asset.status != AssetStatus.PUBLISHED:
            return None

        # 创建交易
        transaction = Transaction(
            id=str(uuid.uuid4()),
            transaction_type=TransactionType.PURCHASE,
            asset_id=asset_id,
            buyer_id=buyer_id,
            seller_id=asset.creator_id,
            amount=asset.price,
            platform_fee=asset.price * self.platform_fee_rate,
            royalty_amount=asset.price * self.royalty_rate
        )

        self.transactions[transaction.id] = transaction

        # 更新资产统计
        asset.purchase_count += 1

        # 更新创作者统计
        self.update_creator_stats(asset.creator_id, asset.price)

        self._save_data()
        return transaction

    def complete_transaction(self, transaction_id: str) -> bool:
        """完成交易"""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return False

        transaction.status = "completed"
        transaction.completed_at = datetime.now()

        self._save_data()
        return True

    def add_review(
        self,
        asset_id: str,
        user_id: str,
        rating: int,
        title: str,
        content: str,
        verified_purchase: bool = False
    ) -> Optional[Review]:
        """添加评价"""
        asset = self.assets.get(asset_id)
        if not asset:
            return None

        review = Review(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            user_id=user_id,
            rating=max(1, min(5, rating)),
            title=title,
            content=content,
            verified_purchase=verified_purchase
        )

        self.reviews[review.id] = review

        # 更新资产评分
        asset_reviews = [r for r in self.reviews.values() if r.asset_id == asset_id]
        asset.rating = sum(r.rating for r in asset_reviews) / len(asset_reviews)
        asset.review_count = len(asset_reviews)

        # 更新创作者评分
        self.update_creator_stats(asset.creator_id, 0)

        self._save_data()
        return review

    def get_asset_reviews(self, asset_id: str, limit: int = 10) -> List[Review]:
        """获取资产评价"""
        reviews = [r for r in self.reviews.values() if r.asset_id == asset_id]
        reviews.sort(key=lambda r: r.helpful_count, reverse=True)
        return reviews[:limit]

    def get_creator_assets(self, creator_id: str) -> List[MarketplaceAsset]:
        """获取创作者的资产"""
        return [a for a in self.assets.values() if a.creator_id == creator_id]

    def get_user_purchases(self, user_id: str) -> List[Transaction]:
        """获取用户购买记录"""
        return [t for t in self.transactions.values()
                if t.buyer_id == user_id and t.status == "completed"]

    def get_creator_sales(self, creator_id: str) -> List[Transaction]:
        """获取创作者销售记录"""
        return [t for t in self.transactions.values()
                if t.seller_id == creator_id and t.status == "completed"]

    def calculate_revenue(self, creator_id: str, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """计算创作者收益"""
        sales = self.get_creator_sales(creator_id)

        total_revenue = 0.0
        net_revenue = 0.0

        for sale in sales:
            if start_date <= sale.created_at <= end_date:
                total_revenue += sale.amount
                net_revenue += sale.amount - sale.platform_fee

        return {
            "total_revenue": total_revenue,
            "net_revenue": net_revenue,
            "platform_fees": total_revenue - net_revenue,
            "transaction_count": len(sales)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取市场统计"""
        total_assets = len(self.assets)
        published_assets = len([a for a in self.assets.values() if a.status == AssetStatus.PUBLISHED])
        total_transactions = len(self.transactions)
        completed_transactions = len([t for t in self.transactions.values() if t.status == "completed"])
        total_revenue = sum(t.amount for t in self.transactions.values() if t.status == "completed")

        return {
            "total_assets": total_assets,
            "published_assets": published_assets,
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "total_revenue": total_revenue,
            "total_creators": len(self.creator_profiles),
            "total_reviews": len(self.reviews)
        }

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载资产
            for asset_data in data.get("assets", []):
                asset = MarketplaceAsset(
                    id=asset_data["id"],
                    creator_id=asset_data["creator_id"],
                    asset_type=asset_data["asset_type"],
                    name=asset_data["name"],
                    description=asset_data["description"],
                    price=asset_data["price"],
                    status=AssetStatus(asset_data.get("status", "draft")),
                    license_type=LicenseType(asset_data.get("license_type", "personal")),
                    tags=asset_data.get("tags", []),
                    preview_url=asset_data.get("preview_url"),
                    download_url=asset_data.get("download_url"),
                    view_count=asset_data.get("view_count", 0),
                    purchase_count=asset_data.get("purchase_count", 0),
                    rating=asset_data.get("rating", 0.0),
                    review_count=asset_data.get("review_count", 0),
                    created_at=datetime.fromisoformat(asset_data["created_at"]),
                    updated_at=datetime.fromisoformat(asset_data["updated_at"]),
                    metadata=asset_data.get("metadata", {})
                )
                self.assets[asset.id] = asset

            # 加载评价
            for review_data in data.get("reviews", []):
                review = Review(
                    id=review_data["id"],
                    asset_id=review_data["asset_id"],
                    user_id=review_data["user_id"],
                    rating=review_data["rating"],
                    title=review_data["title"],
                    content=review_data["content"],
                    created_at=datetime.fromisoformat(review_data["created_at"]),
                    updated_at=datetime.fromisoformat(review_data["updated_at"]) if review_data.get("updated_at") else None,
                    helpful_count=review_data.get("helpful_count", 0),
                    verified_purchase=review_data.get("verified_purchase", False)
                )
                self.reviews[review.id] = review

            # 加载交易
            for trans_data in data.get("transactions", []):
                transaction = Transaction(
                    id=trans_data["id"],
                    transaction_type=TransactionType(trans_data["transaction_type"]),
                    asset_id=trans_data["asset_id"],
                    buyer_id=trans_data["buyer_id"],
                    seller_id=trans_data["seller_id"],
                    amount=trans_data["amount"],
                    platform_fee=trans_data.get("platform_fee", 0.0),
                    royalty_amount=trans_data.get("royalty_amount", 0.0),
                    status=trans_data.get("status", "pending"),
                    created_at=datetime.fromisoformat(trans_data["created_at"]),
                    completed_at=datetime.fromisoformat(trans_data["completed_at"]) if trans_data.get("completed_at") else None,
                    metadata=trans_data.get("metadata", {})
                )
                self.transactions[transaction.id] = transaction

            # 加载创作者档案
            for profile_data in data.get("creator_profiles", []):
                profile = CreatorProfile(
                    id=profile_data["id"],
                    user_id=profile_data["user_id"],
                    display_name=profile_data["display_name"],
                    bio=profile_data.get("bio", ""),
                    avatar_url=profile_data.get("avatar_url"),
                    portfolio_url=profile_data.get("portfolio_url"),
                    social_links=profile_data.get("social_links", {}),
                    total_sales=profile_data.get("total_sales", 0),
                    total_revenue=profile_data.get("total_revenue", 0.0),
                    rating=profile_data.get("rating", 0.0),
                    review_count=profile_data.get("review_count", 0),
                    follower_count=profile_data.get("follower_count", 0),
                    created_at=datetime.fromisoformat(profile_data["created_at"]),
                    verified=profile_data.get("verified", False)
                )
                self.creator_profiles[profile.id] = profile

        except Exception as e:
            print(f"Error loading marketplace data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "assets": [
                    {
                        "id": asset.id,
                        "creator_id": asset.creator_id,
                        "asset_type": asset.asset_type,
                        "name": asset.name,
                        "description": asset.description,
                        "price": asset.price,
                        "status": asset.status.value,
                        "license_type": asset.license_type.value,
                        "tags": asset.tags,
                        "preview_url": asset.preview_url,
                        "download_url": asset.download_url,
                        "view_count": asset.view_count,
                        "purchase_count": asset.purchase_count,
                        "rating": asset.rating,
                        "review_count": asset.review_count,
                        "created_at": asset.created_at.isoformat(),
                        "updated_at": asset.updated_at.isoformat(),
                        "metadata": asset.metadata
                    }
                    for asset in self.assets.values()
                ],
                "reviews": [
                    {
                        "id": review.id,
                        "asset_id": review.asset_id,
                        "user_id": review.user_id,
                        "rating": review.rating,
                        "title": review.title,
                        "content": review.content,
                        "created_at": review.created_at.isoformat(),
                        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
                        "helpful_count": review.helpful_count,
                        "verified_purchase": review.verified_purchase
                    }
                    for review in self.reviews.values()
                ],
                "transactions": [
                    {
                        "id": trans.id,
                        "transaction_type": trans.transaction_type.value,
                        "asset_id": trans.asset_id,
                        "buyer_id": trans.buyer_id,
                        "seller_id": trans.seller_id,
                        "amount": trans.amount,
                        "platform_fee": trans.platform_fee,
                        "royalty_amount": trans.royalty_amount,
                        "status": trans.status,
                        "created_at": trans.created_at.isoformat(),
                        "completed_at": trans.completed_at.isoformat() if trans.completed_at else None,
                        "metadata": trans.metadata
                    }
                    for trans in self.transactions.values()
                ],
                "creator_profiles": [
                    {
                        "id": profile.id,
                        "user_id": profile.user_id,
                        "display_name": profile.display_name,
                        "bio": profile.bio,
                        "avatar_url": profile.avatar_url,
                        "portfolio_url": profile.portfolio_url,
                        "social_links": profile.social_links,
                        "total_sales": profile.total_sales,
                        "total_revenue": profile.total_revenue,
                        "rating": profile.rating,
                        "review_count": profile.review_count,
                        "follower_count": profile.follower_count,
                        "created_at": profile.created_at.isoformat(),
                        "verified": profile.verified
                    }
                    for profile in self.creator_profiles.values()
                ]
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving marketplace data: {e}")


# 全局市场实例
_marketplace: Optional[Marketplace] = None


def get_marketplace(storage_path: Optional[str] = None) -> Marketplace:
    """获取市场单例"""
    global _marketplace
    if _marketplace is None:
        _marketplace = Marketplace(storage_path)
    return _marketplace

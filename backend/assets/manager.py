"""
Asset Manager - 资产管理器
资产浏览、存储、搜索和推荐
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

from .asset_types import (
    Asset, AssetType, AssetStatus, AssetCategory,
    PatternAsset, NPCTemplateAsset, UsageStats
)
from .abstraction import Pattern, get_abstraction_engine


@dataclass
class AssetSearchParams:
    """资产搜索参数"""
    asset_type: Optional[AssetType] = None
    category: Optional[AssetCategory] = None
    status: AssetStatus = AssetStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    text_query: Optional[str] = None
    min_rating: float = 0.0
    min_usage: int = 0
    author: Optional[str] = None
    limit: int = 50


@dataclass
class AssetRecommendation:
    """资产推荐"""
    asset: Asset
    score: float
    reason: str


class AssetBrowser:
    """资产浏览器"""

    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.abstraction_engine = get_abstraction_engine()

    def add_asset(self, asset: Asset) -> bool:
        """添加资产"""
        try:
            # 验证资产
            if not asset.name:
                raise ValueError("Asset name is required")

            # 检查 ID 唯一性
            if asset.id in self.assets:
                raise ValueError(f"Asset ID already exists: {asset.id}")

            self.assets[asset.id] = asset

            # 如果是模式资产，添加到抽象引擎
            if isinstance(asset, PatternAsset):
                pattern = Pattern(
                    id=asset.id,
                    name=asset.name,
                    pattern_type=asset.pattern_type,
                    features=asset.content,
                    examples=[{
                        "description": asset.description,
                        "content": asset.content
                    }]
                )
                self.abstraction_engine.knowledge_base.store_pattern(pattern)

            return True
        except Exception as e:
            print(f"Error adding asset: {e}")
            return False

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """获取资产"""
        return self.assets.get(asset_id)

    def search(self, params: AssetSearchParams) -> List[Asset]:
        """搜索资产"""
        results = []

        for asset in self.assets.values():
            # 状态筛选
            if asset.status != params.status:
                continue

            # 类型筛选
            if params.asset_type and asset.asset_type != params.asset_type:
                continue

            # 分类筛选
            if params.category and asset.metadata.category != params.category:
                continue

            # 作者筛选
            if params.author and asset.metadata.author != params.author:
                continue

            # 标签筛选
            if params.tags:
                if not any(tag in asset.metadata.tags for tag in params.tags):
                    continue

            # 评分筛选
            if asset.usage_stats.average_rating < params.min_rating:
                continue

            # 使用次数筛选
            if asset.usage_stats.usage_count < params.min_usage:
                continue

            # 文本搜索
            if params.text_query:
                query = params.text_query.lower()
                searchable_text = f"{asset.name} {asset.description} {' '.join(asset.metadata.tags)}".lower()
                if query not in searchable_text:
                    continue

            results.append(asset)

            # 限制结果数量
            if len(results) >= params.limit:
                break

        return results

    def get_popular_assets(self, limit: int = 10) -> List[Asset]:
        """获取热门资产"""
        return sorted(
            self.assets.values(),
            key=lambda a: (a.usage_stats.usage_count, a.usage_stats.average_rating),
            reverse=True
        )[:limit]

    def get_recent_assets(self, limit: int = 10) -> List[Asset]:
        """获取最近资产"""
        return sorted(
            self.assets.values(),
            key=lambda a: a.metadata.updated_at,
            reverse=True
        )[:limit]

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """按类型获取资产"""
        return [
            asset for asset in self.assets.values()
            if asset.asset_type == asset_type
        ]

    def get_assets_by_tag(self, tag: str) -> List[Asset]:
        """按标签获取资产"""
        return [
            asset for asset in self.assets.values()
            if tag in asset.metadata.tags
        ]


class AssetRecommender:
    """资产推荐引擎"""

    def __init__(self, browser: AssetBrowser):
        self.browser = browser
        self.abstraction_engine = get_abstraction_engine()

    def recommend(
        self,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[AssetRecommendation]:
        """基于上下文推荐资产"""
        recommendations = []

        # 从抽象引擎获取相关模式
        patterns = self.abstraction_engine.suggest_patterns(context, limit=limit * 2)

        # 为每个模式查找对应的资产
        for pattern in patterns:
            # 查找与模式相关的资产
            related_assets = self._find_assets_by_pattern(pattern)

            for asset in related_assets:
                # 计算推荐分数
                score = self._calculate_recommendation_score(asset, context, pattern)

                if score > 0.5:  # 推荐阈值
                    recommendations.append(AssetRecommendation(
                        asset=asset,
                        score=score,
                        reason=self._generate_recommendation_reason(asset, pattern)
                    ))

        # 按分数排序
        recommendations.sort(key=lambda r: r.score, reverse=True)

        return recommendations[:limit]

    def _find_assets_by_pattern(self, pattern: Pattern) -> List[Asset]:
        """查找与模式相关的资产"""
        # 简化实现：查找相同类型的资产
        asset_type_map = {
            "character_arc": AssetType.NPC_TEMPLATE,
            "plot_structure": AssetType.PATTERN,
            "dialogue_pattern": AssetType.DIALOGUE,
        }

        asset_type = asset_type_map.get(pattern.pattern_type)
        if asset_type:
            return self.browser.get_assets_by_type(asset_type)

        return []

    def _calculate_recommendation_score(
        self,
        asset: Asset,
        context: Dict[str, Any],
        pattern: Pattern
    ) -> float:
        """计算推荐分数"""
        score = 0.0

        # 基于使用统计
        if asset.usage_stats.usage_count > 0:
            score += min(0.3, asset.usage_stats.success_rate * 0.3)

        # 基于评分
        if asset.usage_stats.rating_count > 0:
            score += min(0.3, asset.usage_stats.average_rating / 5.0 * 0.3)

        # 基于模式匹配度
        similarity = self.abstraction_engine.knowledge_base._calculate_similarity(
            context,
            pattern.features
        )
        score += similarity * 0.4

        return min(1.0, score)

    def _generate_recommendation_reason(self, asset: Asset, pattern: Pattern) -> str:
        """生成推荐理由"""
        reasons = []

        if asset.usage_stats.usage_count > 10:
            reasons.append(f"热门资产（已使用 {asset.usage_stats.usage_count} 次）")

        if asset.usage_stats.average_rating > 4.0:
            reasons.append(f"高评分（{asset.usage_stats.average_rating:.1f} 分）")

        if pattern.pattern_type in ["character_arc", "plot_structure"]:
            reasons.append(f"匹配 {pattern.pattern_type} 模式")

        if not reasons:
            reasons.append("与当前上下文相关")

        return " | ".join(reasons)


class AssetManager:
    """资产管理器：主管理类"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/assets.json"
        self.browser = AssetBrowser()
        self.recommender = AssetRecommender(self.browser)

        # 创建数据目录
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # 加载已保存的资产
        self._load_assets()

    def _load_assets(self):
        """加载资产"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for asset_data in data.get("assets", []):
                try:
                    asset = Asset.from_dict(asset_data)
                    self.browser.assets[asset.id] = asset
                except Exception as e:
                    print(f"Error loading asset {asset_data.get('id')}: {e}")

        except Exception as e:
            print(f"Error loading assets: {e}")

    def _save_assets(self):
        """保存资产"""
        try:
            data = {
                "assets": [
                    asset.to_dict()
                    for asset in self.browser.assets.values()
                ],
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving assets: {e}")

    # ========== 公共 API ==========

    def create_asset(
        self,
        asset_type: AssetType,
        name: str,
        content: Dict[str, Any],
        description: str = "",
        tags: List[str] = None,
        author: str = "user"
    ) -> Optional[Asset]:
        """创建资产"""
        from .asset_types import AssetFactory

        asset = AssetFactory.create_asset(
            asset_type=asset_type,
            name=name,
            description=description,
            content=content,
            metadata={
                "author": author,
                "tags": tags or [],
            }
        )

        if self.browser.add_asset(asset):
            self._save_assets()
            return asset

        return None

    def update_asset(self, asset_id: str, **updates) -> bool:
        """更新资产"""
        asset = self.browser.get_asset(asset_id)
        if not asset:
            return False

        # 更新字段
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
            elif hasattr(asset.metadata, key):
                setattr(asset.metadata, key, value)

        asset.metadata.updated_at = datetime.now()

        self._save_assets()
        return True

    def delete_asset(self, asset_id: str) -> bool:
        """删除资产"""
        if asset_id not in self.browser.assets:
            return False

        del self.browser.assets[asset_id]
        self._save_assets()
        return True

    def rate_asset(self, asset_id: str, rating: float) -> bool:
        """为资产评分"""
        asset = self.browser.get_asset(asset_id)
        if not asset:
            return False

        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5")

        asset.usage_stats.rating_sum += rating
        asset.usage_stats.rating_count += 1
        asset.metadata.updated_at = datetime.now()

        self._save_assets()
        return True

    def use_asset(self, asset_id: str, success: bool = True) -> bool:
        """使用资产"""
        asset = self.browser.get_asset(asset_id)
        if not asset:
            return False

        asset.update_usage(success=success)
        self._save_assets()
        return True

    def search_assets(self, **params) -> List[Asset]:
        """搜索资产"""
        search_params = AssetSearchParams(**params)
        return self.browser.search(search_params)

    def get_recommendations(self, context: Dict[str, Any], limit: int = 5) -> List[AssetRecommendation]:
        """获取推荐"""
        return self.recommender.recommend(context, limit)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        all_assets = list(self.browser.assets.values())

        type_counts = {}
        for asset in all_assets:
            atype = asset.asset_type.value
            type_counts[atype] = type_counts.get(atype, 0) + 1

        total_usage = sum(a.usage_stats.usage_count for a in all_assets)
        total_ratings = sum(a.usage_stats.rating_count for a in all_assets)
        avg_rating = (
            sum(a.usage_stats.average_rating for a in all_assets if a.usage_stats.rating_count > 0) /
            len([a for a in all_assets if a.usage_stats.rating_count > 0])
            if total_ratings > 0 else 0
        )

        return {
            "total_assets": len(all_assets),
            "type_counts": type_counts,
            "total_usage": total_usage,
            "total_ratings": total_ratings,
            "average_rating": round(avg_rating, 2),
            "last_updated": datetime.now().isoformat()
        }


# 全局资产管理器实例
_asset_manager: Optional[AssetManager] = None


def get_asset_manager(storage_path: Optional[str] = None) -> AssetManager:
    """获取资产管理器单例"""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager(storage_path)
    return _asset_manager

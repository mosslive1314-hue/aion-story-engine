"""
Asset System - 资产系统核心类型
定义资产类型、数据结构和生命周期
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class AssetType(Enum):
    """资产类型"""
    PATTERN = "pattern"  # 故事模式
    NPC_TEMPLATE = "npc_template"  # NPC 模板
    WORLD_RULE = "world_rule"  # 世界规则
    DIALOGUE = "dialogue"  # 对话模板
    NARRATIVE = "narrative"  # 叙事框架
    ASSET_PACK = "asset_pack"  # 资产包
    SCENE_TEMPLATE = "scene_template"  # 场景模板
    PLOT_TWIST = "plot_twist"  # 情节转折


class AssetStatus(Enum):
    """资产状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 活跃
    ARCHIVED = "archived"  # 归档
    DEPRECATED = "deprecated"  # 弃用


class AssetCategory(Enum):
    """资产分类"""
    CHARACTER = "character"  # 角色
    PLOT = "plot"  # 情节
    SETTING = "setting"  # 设定
    DIALOGUE = "dialogue"  # 对话
    THEME = "theme"  # 主题
    MECHANIC = "mechanic"  # 机制


@dataclass
class AssetMetadata:
    """资产元数据"""
    author: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    category: Optional[AssetCategory] = None
    source: Optional[str] = None  # 来源（用户、AI、导入等）
    language: str = "zh"


@dataclass
class UsageStats:
    """使用统计"""
    usage_count: int = 0
    success_count: int = 0  # 成功应用次数
    rating_sum: float = 0.0  # 评分总和
    rating_count: int = 0  # 评分人数
    last_used: Optional[datetime] = None

    @property
    def average_rating(self) -> float:
        """平均评分"""
        if self.rating_count == 0:
            return 0.0
        return self.rating_sum / self.rating_count

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count


@dataclass
class Asset:
    """资产基类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    asset_type: AssetType = AssetType.PATTERN
    name: str = ""
    description: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    status: AssetStatus = AssetStatus.ACTIVE
    usage_stats: UsageStats = field(default_factory=UsageStats)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        """从字典创建"""
        # 处理枚举类型
        if 'asset_type' in data and isinstance(data['asset_type'], str):
            data['asset_type'] = AssetType(data['asset_type'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = AssetStatus(data['status'])
        if 'metadata' in data and 'category' in data['metadata']:
            if isinstance(data['metadata']['category'], str):
                data['metadata']['category'] = AssetCategory(data['metadata']['category'])

        # 处理 datetime
        if 'metadata' in data and 'created_at' in data['metadata']:
            if isinstance(data['metadata']['created_at'], str):
                data['metadata']['created_at'] = datetime.fromisoformat(data['metadata']['created_at'])
        if 'metadata' in data and 'updated_at' in data['metadata']:
            if isinstance(data['metadata']['updated_at'], str):
                data['metadata']['updated_at'] = datetime.fromisoformat(data['metadata']['updated_at'])
        if 'usage_stats' in data and 'last_used' in data['usage_stats']:
            if data['usage_stats']['last_used']:
                if isinstance(data['usage_stats']['last_used'], str):
                    data['usage_stats']['last_used'] = datetime.fromisoformat(data['usage_stats']['last_used'])

        return cls(**data)

    def update_usage(self, success: bool = True, rating: Optional[float] = None):
        """更新使用统计"""
        self.usage_stats.usage_count += 1
        if success:
            self.usage_stats.success_count += 1
        if rating is not None:
            self.usage_stats.rating_sum += rating
            self.usage_stats.rating_count += 1
        self.usage_stats.last_used = datetime.now()
        self.metadata.updated_at = datetime.now()

    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.metadata.updated_at = datetime.now()

    def remove_tag(self, tag: str):
        """移除标签"""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.updated_at = datetime.now()

    def archive(self):
        """归档资产"""
        self.status = AssetStatus.ARCHIVED
        self.metadata.updated_at = datetime.now()

    def activate(self):
        """激活资产"""
        self.status = AssetStatus.ACTIVE
        self.metadata.updated_at = datetime.now()


# ============================================================================
# 具体资产类型
# ============================================================================

@dataclass
class PatternAsset(Asset):
    """故事模式资产"""
    asset_type: AssetType = AssetType.PATTERN

    # 模式特定字段
    pattern_type: str = ""  # 模式类型（如"英雄之旅"、"三幕式"等）
    context: str = ""  # 适用场景
    examples: List[str] = field(default_factory=list)  # 示例

    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用模式到上下文"""
        result = {
            "pattern": self.name,
            "content": self.content,
            "context": context,
            "suggestions": []
        }

        # 根据模式类型生成建议
        if self.pattern_type == "character_arc":
            result["suggestions"] = self._generate_character_arc(context)
        elif self.pattern_type == "plot_structure":
            result["suggestions"] = self._generate_plot_structure(context)

        return result

    def _generate_character_arc(self, context: Dict[str, Any]) -> List[str]:
        """生成角色弧线建议"""
        return [
            f"角色 {context.get('character', '主角')} 面临挑战",
            f"经历转变和成长",
            f"最终达成目标或接受失败"
        ]

    def _generate_plot_structure(self, context: Dict[str, Any]) -> List[str]:
        """生成情节结构建议"""
        return [
            "铺垫：介绍背景和角色",
            "冲突：引入问题和挑战",
            "高潮：矛盾激化到顶点",
            "结局：问题解决或留下悬念"
        ]


@dataclass
class NPCTemplateAsset(Asset):
    """NPC 模板资产"""
    asset_type: AssetType = AssetType.NPC_TEMPLATE

    # NPC 特定字段
    role: str = ""  # 角色（如"导师"、"反派"等）
    personality_traits: List[str] = field(default_factory=list)  # 性格特征
    dialogue_style: str = ""  # 对话风格
    background_template: str = ""  # 背景模板

    def generate_npc(self, name: str, customization: Dict[str, Any]) -> Dict[str, Any]:
        """生成 NPC 实例"""
        return {
            "name": name,
            "role": self.role,
            "personality": customization.get("personality", self.personality_traits),
            "dialogue_style": self.dialogue_style,
            "background": self.background_template.format(**customization),
            "template_id": self.id
        }


@dataclass
class WorldRuleAsset(Asset):
    """世界规则资产"""
    asset_type: AssetType = AssetType.WORLD_RULE

    # 规则特定字段
    rule_type: str = ""  # 规则类型（如"魔法"、"科技"、"社会"等）
    constraints: List[str] = field(default_factory=list)  # 约束条件
    examples: List[str] = field(default_factory=list)  # 应用示例

    def validate(self, content: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证内容是否符合规则"""
        errors = []

        # 检查约束条件
        for constraint in self.constraints:
            if not self._check_constraint(content, constraint):
                errors.append(f"违反约束: {constraint}")

        return len(errors) == 0, errors

    def _check_constraint(self, content: Dict[str, Any], constraint: str) -> bool:
        """检查单个约束"""
        # 简化实现，实际需要更复杂的约束检查
        return True


@dataclass
class DialogueAsset(Asset):
    """对话模板资产"""
    asset_type: AssetType = AssetType.DIALOGUE

    # 对话特定字段
    mood: str = ""  # 情绪基调
    speakers: List[str] = field(default_factory=list)  # 说话者角色
    template: str = ""  # 对话模板

    def generate_dialogue(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成对话"""
        # 简化实现
        return [
            {
                "speaker": self.speakers[0] if self.speakers else "未知",
                "dialogue": self.template.format(**context),
                "mood": self.mood
            }
        ]


@dataclass
class NarrativeAsset(Asset):
    """叙事框架资产"""
    asset_type: AssetType = AssetType.NARRATIVE

    # 叙事特定字段
    narrative_structure: str = ""  # 叙事结构
    pacing: str = ""  # 节奏
    pov: str = ""  # 视角
    tone: str = ""  # 基调

    def apply_to_story(self, story_content: str) -> Dict[str, Any]:
        """将叙事框架应用到故事"""
        return {
            "original": story_content,
            "structure": self.narrative_structure,
            "pacing": self.pacing,
            "pov": self.pov,
            "tone": self.tone,
            "suggestions": [
                f"使用 {self.pov} 视角",
                f"保持 {self.tone} 的基调",
                f"遵循 {self.narrative_structure} 结构"
            ]
        }


@dataclass
class AssetPackAsset(Asset):
    """资产包"""
    asset_type: AssetType = AssetType.ASSET_PACK

    # 资产包特定字段
    asset_ids: List[str] = field(default_factory=list)  # 包含的资产 ID
    pack_type: str = ""  # 包类型（如"完整故事"、"特定主题"等）

    def get_assets(self, asset_store: 'AssetStore') -> List[Asset]:
        """获取包中所有资产"""
        return [
            asset_store.get_asset(asset_id)
            for asset_id in self.asset_ids
            if asset_store.get_asset(asset_id) is not None
        ]


# ============================================================================
# 资产工厂
# ============================================================================

class AssetFactory:
    """资产工厂"""

    _asset_classes = {
        AssetType.PATTERN: PatternAsset,
        AssetType.NPC_TEMPLATE: NPCTemplateAsset,
        AssetType.WORLD_RULE: WorldRuleAsset,
        AssetType.DIALOGUE: DialogueAsset,
        AssetType.NARRATIVE: NarrativeAsset,
        AssetType.ASSET_PACK: AssetPackAsset,
    }

    @classmethod
    def create_asset(
        cls,
        asset_type: AssetType,
        **kwargs
    ) -> Asset:
        """创建资产"""
        asset_class = cls._asset_classes.get(asset_type, Asset)
        return asset_class(asset_type=asset_type, **kwargs)

    @classmethod
    def register_asset_class(cls, asset_type: AssetType, asset_class: type):
        """注册自定义资产类"""
        cls._asset_classes[asset_type] = asset_class

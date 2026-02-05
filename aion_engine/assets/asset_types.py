from enum import Enum


class AssetType(Enum):
    """资产类型"""
    PATTERN = "causal_pattern"  # 因果模式
    NPC_TEMPLATE = "npc_template"  # NPC模板
    WORLD_RULE = "world_rule"  # 世界规则
    DIALOGUE = "dialogue_fragment"  # 对话片段
    NARRATIVE = "narrative_trope"  # 叙事套路
    ASSET_PACK = "asset_pack"  # 资产包

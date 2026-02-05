"""
Medici Synapse - 跨域创新引擎
通过结构同构性识别跨域创新机会
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class DomainType(Enum):
    """领域类型"""
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    ART = "art"
    SCIENCE = "science"
    SPORTS = "sports"
    POLITICS = "politics"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    MILITARY = "military"
    MEDICINE = "medicine"


@dataclass
class StructurePattern:
    """结构模式"""
    id: str
    name: str
    domain: DomainType
    core_logic: str  # 核心逻辑
    components: List[str]  # 组成部分
    relationships: List[str]  # 关系
    success_metrics: List[str]  # 成功指标
    examples: List[Dict[str, Any]] = field(default_factory=list)

    def extract_abstraction(self) -> Dict[str, Any]:
        """提取抽象结构"""
        return {
            "name": self.name,
            "core_logic": self.core_logic,
            "components": self.components,
            "relationships": self.relationships,
            "success_metrics": self.success_metrics,
        }


@dataclass
class StructuralIsomorphism:
    """结构同构"""
    source_domain: DomainType
    target_domain: DomainType
    source_pattern: StructurePattern
    target_pattern: StructurePattern
    similarity_score: float  # 相似度得分 0-1
    mapping: Dict[str, str]  # 映射关系
    innovation_opportunities: List[str] = field(default_factory=list)


@dataclass
class InnovationIdea:
    """创新点子"""
    title: str
    description: str
    source_domain: DomainType
    target_domain: DomainType
    core_concept: str
    business_model: str
    market_opportunity: str
    risks: List[str] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    estimated_impact: str = ""
    confidence: float = 0.0


class StructuralAnalyzer:
    """结构分析器"""

    def __init__(self):
        self.patterns: Dict[DomainType, List[StructurePattern]] = {}

    def extract_structure(self, domain: DomainType, description: str) -> StructurePattern:
        """从描述中提取结构"""
        # 简化实现：使用规则提取
        components = self._extract_components(description)
        relationships = self._extract_relationships(description)

        pattern = StructurePattern(
            id=f"{domain.value}_{datetime.now().timestamp()}",
            name=f"{domain.value} pattern",
            domain=domain,
            core_logic=self._extract_core_logic(description),
            components=components,
            relationships=relationships,
            success_metrics=self._extract_success_metrics(description)
        )

        return pattern

    def _extract_components(self, description: str) -> List[str]:
        """提取组成部分"""
        # 简化实现：使用关键词提取
        components = []

        # 常见组件关键词
        if "用户" in description or "客户" in description:
            components.append("users/customers")
        if "产品" in description or "服务" in description:
            components.append("product/service")
        if "平台" in description:
            components.append("platform")
        if "数据" in description:
            components.append("data")
        if "算法" in description or "模型" in description:
            components.append("algorithm/model")

        return components

    def _extract_relationships(self, description: str) -> List[str]:
        """提取关系"""
        relationships = []

        # 简单的关系提取
        if "通过" in description:
            relationships.append("mediated_by")
        if "基于" in description:
            relationships.append("based_on")
        if "包含" in description:
            relationships.append("includes")

        return relationships

    def _extract_core_logic(self, description: str) -> str:
        """提取核心逻辑"""
        # 找主要动词和宾语
        sentences = description.split('。')
        if sentences:
            return sentences[0][:100]  # 第一句话的前100字
        return description[:100]

    def _extract_success_metrics(self, description: str) -> List[str]:
        """提取成功指标"""
        metrics = []

        # 常见指标关键词
        if "收入" in description or "盈利" in description:
            metrics.append("revenue/profit")
        if "用户" in description and "增长" in description:
            metrics.append("user_growth")
        if "效率" in description or "提升" in description:
            metrics.append("efficiency_gain")

        return metrics


class IsomorphismDetector:
    """同构检测器"""

    def __init__(self):
        self.analyzer = StructuralAnalyzer()

    def detect_isomorphism(
        self,
        source_pattern: StructurePattern,
        target_domain: DomainType,
        target_description: str
    ) -> StructuralIsomorphism:
        """检测结构同构"""
        # 提取目标领域的结构
        target_pattern = self.analyzer.extract_structure(target_domain, target_description)

        # 计算相似度
        similarity = self._calculate_similarity(source_pattern, target_pattern)

        # 创建映射
        mapping = self._create_mapping(source_pattern, target_pattern)

        # 生成创新机会
        opportunities = self._identify_opportunities(source_pattern, target_pattern, mapping)

        return StructuralIsomorphism(
            source_domain=source_pattern.domain,
            target_domain=target_domain,
            source_pattern=source_pattern,
            target_pattern=target_pattern,
            similarity_score=similarity,
            mapping=mapping,
            innovation_opportunities=opportunities
        )

    def _calculate_similarity(
        self,
        pattern1: StructurePattern,
        pattern2: StructurePattern
    ) -> float:
        """计算结构相似度"""
        # 比较组件
        components1 = set(pattern1.components)
        components2 = set(pattern2.components)

        if not components1 or not components2:
            return 0.0

        component_similarity = len(components1 & components2) / len(components1 | components2)

        # 比较关系
        relationships1 = set(pattern1.relationships)
        relationships2 = set(pattern2.relationships)

        if not relationships1 or not relationships2:
            return component_similarity

        relationship_similarity = len(relationships1 & relationships2) / len(relationships1 | relationships2)

        # 加权平均
        return component_similarity * 0.6 + relationship_similarity * 0.4

    def _create_mapping(
        self,
        pattern1: StructurePattern,
        pattern2: StructurePattern
    ) -> Dict[str, str]:
        """创建映射关系"""
        mapping = {}

        # 简单的词汇映射
        word_map = {
            "用户": "客户",
            "产品": "服务",
            "平台": "系统",
            "数据": "信息",
        }

        for key, value in word_map.items():
            if key in pattern1.core_logic and value in pattern2.core_logic:
                mapping[key] = value

        return mapping

    def _identify_opportunities(
        self,
        source_pattern: StructurePattern,
        target_pattern: StructurePattern,
        mapping: Dict[str, str]
    ) -> List[str]:
        """识别创新机会"""
        opportunities = []

        # 基于组件差异识别机会
        source_components = set(source_pattern.components)
        target_components = set(target_pattern.components)

        # 源领域有但目标领域没有的组件
        new_components = source_components - target_components
        for component in new_components:
            opportunities.append(f"引入 {component} 组件")

        # 目标领域有但源领域没有的组件
        unique_components = target_components - source_components
        for component in unique_components:
            opportunities.append(f"结合 {component} 元素")

        return opportunities


class InnovationGenerator:
    """创新生成器"""

    def __init__(self):
        self.detector = IsomorphismDetector()

    def generate_innovation(
        self,
        source_domain: DomainType,
        source_description: str,
        target_domain: DomainType,
        target_description: str,
        user_customization: Optional[Dict[str, Any]] = None
    ) -> InnovationIdea:
        """生成创新点子"""
        # 提取源领域结构
        source_pattern = self.detector.analyzer.extract_structure(
            source_domain,
            source_description
        )

        # 检测同构
        isomorphism = self.detector.detect_isomorphism(
            source_pattern,
            target_domain,
            target_description
        )

        # 基于同构生成创新点子
        idea = InnovationIdea(
            title=self._generate_title(source_domain, target_domain),
            description=self._generate_description(isomorphism),
            source_domain=source_domain,
            target_domain=target_domain,
            core_concept=self._generate_core_concept(isomorphism),
            business_model=self._generate_business_model(isomorphism),
            market_opportunity=self._generate_market_opportunity(isomorphism),
            implementation_steps=self._generate_implementation_steps(isomorphism),
            estimated_impact=self._estimate_impact(isomorphism),
            confidence=isomorphism.similarity_score
        )

        return idea

    def _generate_title(self, source: DomainType, target: DomainType) -> str:
        """生成标题"""
        return f"{source.value.title()} → {target.value.title()} 创新模式"

    def _generate_description(self, isomorphism: StructuralIsomorphism) -> str:
        """生成描述"""
        return f"将 {isomorphism.source_domain.value} 领域的 {isomorphism.source_pattern.name} 模式" \
               f"创新性地应用到 {isomorphism.target_domain.value} 领域"

    def _generate_core_concept(self, isomorphism: StructuralIsomorphism) -> str:
        """生成核心概念"""
        abstraction = isomorphism.source_pattern.extract_abstraction()

        concept = f"核心概念：{abstraction['core_logic']}\n"
        concept += f"通过结构同构，将此模式迁移到 {isomorphism.target_domain.value} 领域"

        return concept

    def _generate_business_model(self, isomorphism: StructuralIsomorphism) -> str:
        """生成商业模式"""
        model = f"商业模式：\n"
        model += f"1. 在 {isomorphism.target_domain.value} 领域复制验证过的 {isomorphism.source_domain.value} 模式\n"
        model += f"2. 利用结构相似性降低实施风险\n"
        model += f"3. 通过本地化适应提升成功率"

        return model

    def _generate_market_opportunity(self, isomorphism: StructuralIsomorphism) -> str:
        """生成市场机会"""
        opportunity = f"市场机会：\n"
        opportunity += f"- {isomorphism.target_domain.value} 领域缺乏 {isomorphism.source_domain.value} 的成熟模式\n"
        opportunity += f"- 结构相似度 {isomorphism.similarity_score:.1%}，降低学习曲线\n"
        opportunity += f"- 创新先发优势"

        return opportunity

    def _generate_implementation_steps(self, isomorphism: StructuralIsomorphism) -> List[str]:
        """生成实施步骤"""
        steps = [
            "1. 深度分析源领域模式的核心逻辑和成功因素",
            f"2. 识别 {isomorphism.target_domain.value} 领域的痛点和机会",
            "3. 设计结构映射和本地化方案",
            "4. 小规模测试和验证",
            "5. 快速迭代和规模化",
        ]

        if isomorphism.mapping:
            steps.append("6. 根据映射关系优化实施路径")

        return steps

    def _estimate_impact(self, isomorphism: StructuralIsomorphism) -> str:
        """估算影响"""
        if isomorphism.similarity_score > 0.8:
            return "高影响：结构高度相似，成功概率很高"
        elif isomorphism.similarity_score > 0.6:
            return "中高影响：结构基本相似，需要适度调整"
        elif isomorphism.similarity_score > 0.4:
            return "中等影响：有相似性但需要显著创新"
        else:
            return "实验性：低相似度，高风险高回报"


class MediciSynapse:
    """Medici Synapse 主类"""

    def __init__(self):
        self.analyzer = StructuralAnalyzer()
        self.detector = IsomorphismDetector()
        self.generator = InnovationGenerator()
        self.ideas: List[InnovationIdea] = []

    def brainstorm(
        self,
        source_domain: DomainType,
        source_description: str,
        target_domains: List[DomainType],
        target_descriptions: Dict[DomainType, str],
        limit: int = 5
    ) -> List[InnovationIdea]:
        """头脑风暴创新点子"""
        self.ideas = []

        for target_domain in target_domains:
            if target_domain not in target_descriptions:
                continue

            try:
                idea = self.generator.generate_innovation(
                    source_domain,
                    source_description,
                    target_domain,
                    target_descriptions[target_domain]
                )

                if idea.confidence > 0.4:  # 置信度阈值
                    self.ideas.append(idea)

            except Exception as e:
                print(f"Error generating idea for {target_domain}: {e}")

        # 按置信度排序
        self.ideas.sort(key=lambda i: i.confidence, reverse=True)

        return self.ideas[:limit]

    def create_pitch_deck(self, idea: InnovationIdea) -> Dict[str, str]:
        """创建 Pitch Deck"""
        return {
            "title": idea.title,
            "tagline": self._generate_tagline(idea),
            "problem": self._identify_problem(idea),
            "solution": idea.core_concept,
            "business_model": idea.business_model,
            "market_opportunity": idea.market_opportunity,
            "implementation": "\n".join(idea.implementation_steps),
            "impact": idea.estimated_impact,
            "risks": "\n".join(idea.risks) if idea.risks else "主要风险：跨域执行难度",
            "confidence": f"{idea.confidence:.1%}",
        }

    def _generate_tagline(self, idea: InnovationIdea) -> str:
        """生成标语"""
        return f"将 {idea.source_domain.value} 的成功模式创新性地应用到 {idea.target_domain.value}"

    def _identify_problem(self, idea: InnovationIdea) -> str:
        """识别问题"""
        return f"{idea.target_domain.value} 领域缺乏 {idea.source_domain.value} 的成熟模式和最佳实践"

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.ideas:
            return {"total_ideas": 0}

        domain_pairs = {}
        for idea in self.ideas:
            pair = f"{idea.source_domain.value} → {idea.target_domain.value}"
            domain_pairs[pair] = domain_pairs.get(pair, 0) + 1

        return {
            "total_ideas": len(self.ideas),
            "avg_confidence": sum(i.confidence for i in self.ideas) / len(self.ideas),
            "high_confidence_count": len([i for i in self.ideas if i.confidence > 0.7]),
            "domain_pairs": domain_pairs,
        }


# 全局 Medici Synapse 实例
_medici_synapse: Optional[MediciSynapse] = None


def get_medici_synapse() -> MediciSynapse:
    """获取 Medici Synapse 单例"""
    global _medici_synapse
    if _medici_synapse is None:
        _medici_synapse = MediciSynapse()
    return _medici_synapse

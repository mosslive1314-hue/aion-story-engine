"""
Skill Growth Tracking - 技能成长追踪
追踪用户技能发展和成长曲线
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json
import os


class SkillType(Enum):
    """技能类型"""
    WRITING = "writing"  # 写作技能
    PLOTTING = "plotting"  # 情节设计
    DIALOGUE = "dialogue"  # 对话写作
    WORLD_BUILDING = "world_building"  # 世界观构建
    CHARACTER_DESIGN = "character_design"  # 角色设计
    PACING = "pacing"  # 节奏控制
    DESCRIPTION = "description"  # 描写技能
    CREATIVITY = "creativity"  # 创意能力


class SkillLevel(Enum):
    """技能等级"""
    NOVICE = "novice"  # 新手 (1-20分)
    BEGINNER = "beginner"  # 初学者 (21-40分)
    INTERMEDIATE = "intermediate"  # 中级 (41-60分)
    ADVANCED = "advanced"  # 高级 (61-80分)
    EXPERT = "expert"  # 专家 (81-95分)
    MASTER = "master"  # 大师 (96-100分)


@dataclass
class SkillMilestone:
    """技能里程碑"""
    id: str
    skill_type: SkillType
    name: str
    description: str
    required_score: float  # 所需分数
    achieved: bool = False
    achieved_at: Optional[datetime] = None
    evidence: List[str] = field(default_factory=list)  # 证明材料

    def check(self, current_score: float) -> bool:
        """检查是否达成"""
        if not self.achieved and current_score >= self.required_score:
            self.achieved = True
            self.achieved_at = datetime.now()
            return True
        return False


@dataclass
class SkillAssessment:
    """技能评估"""
    skill_type: SkillType
    score: float  # 0-100
    level: SkillLevel
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.now)
    evidence: Dict[str, Any] = field(default_factory=dict)

    def get_level(self) -> SkillLevel:
        """获取等级"""
        if self.score >= 96:
            return SkillLevel.MASTER
        elif self.score >= 81:
            return SkillLevel.EXPERT
        elif self.score >= 61:
            return SkillLevel.ADVANCED
        elif self.score >= 41:
            return SkillLevel.INTERMEDIATE
        elif self.score >= 21:
            return SkillLevel.BEGINNER
        else:
            return SkillLevel.NOVICE


@dataclass
class GrowthDataPoint:
    """成长数据点"""
    timestamp: datetime
    skill_scores: Dict[SkillType, float]
    activities: List[str] = field(default_factory=list)


@dataclass
class LearningPath:
    """学习路径"""
    skill_type: SkillType
    current_level: SkillLevel
    target_level: SkillLevel
    resources: List[Dict[str, Any]] = field(default_factory=list)
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    estimated_duration_days: int = 30


class SkillTracker:
    """技能追踪器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/skill_tracking.json"
        self.skill_scores: Dict[SkillType, List[float]] = defaultdict(list)
        self.milestones: Dict[SkillType, List[SkillMilestone]] = {}
        self.growth_history: List[GrowthDataPoint] = []

        # 加载已保存的数据
        self._load_data()

        # 默认里程碑
        self._init_default_milestones()

    def _load_data(self):
        """加载保存的数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载技能分数
            for skill_str, scores in data.get("skill_scores", {}).items():
                skill_type = SkillType(skill_str)
                self.skill_scores[skill_type] = scores

            # 加载里程碑
            for skill_str, milestones in data.get("milestones", {}).items():
                skill_type = SkillType(skill_str)
                self.milestones[skill_type] = [
                    SkillMilestone(
                        id=m["id"],
                        skill_type=SkillType(m["skill_type"]),
                        name=m["name"],
                        description=m["description"],
                        required_score=m["required_score"],
                        achieved=m["achieved"],
                        achieved_at=datetime.fromisoformat(m["achieved_at"]) if m.get("achieved_at") else None,
                        evidence=m.get("evidence", [])
                    )
                    for m in milestones
                ]

            # 加载成长历史
            for point in data.get("growth_history", []):
                self.growth_history.append(GrowthDataPoint(
                    timestamp=datetime.fromisoformat(point["timestamp"]),
                    skill_scores={
                        SkillType(k): v for k, v in point["skill_scores"].items()
                    },
                    activities=point.get("activities", [])
                ))

        except Exception as e:
            print(f"Error loading skill tracking data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "skill_scores": {
                    skill_type.value: scores
                    for skill_type, scores in self.skill_scores.items()
                },
                "milestones": {
                    skill_type.value: [
                        {
                            "id": m.id,
                            "skill_type": m.skill_type.value,
                            "name": m.name,
                            "description": m.description,
                            "required_score": m.required_score,
                            "achieved": m.achieved,
                            "achieved_at": m.achieved_at.isoformat() if m.achieved_at else None,
                            "evidence": m.evidence
                        }
                        for m in milestones
                    ]
                    for skill_type, milestones in self.milestones.items()
                },
                "growth_history": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "skill_scores": {
                            k.value: v for k, v in point.skill_scores.items()
                        },
                        "activities": point.activities
                    }
                    for point in self.growth_history
                ],
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving skill tracking data: {e}")

    def _init_default_milestones(self):
        """初始化默认里程碑"""
        default_milestones = {
            SkillType.WRITING: [
                ("novice_writer", "新手作者", "能够完成基本的句子写作", 20),
                ("beginner_writer", "入门作者", "能够写出完整的段落", 40),
                ("intermediate_writer", "中级作者", "能够写出结构完整的场景", 60),
                ("advanced_writer", "高级作者", "能够写出富有感染力的章节", 80),
                ("expert_writer", "专家作者", "能够创作高质量作品", 90),
                ("master_writer", "大师作者", "创作出传世之作", 96),
            ],
            SkillType.PLOTTING: [
                ("novice_plotter", "新手编剧", "能够设计简单情节", 20),
                ("beginner_plotter", "入门编剧", "能够设计完整故事线", 40),
                ("intermediate_plotter", "中级编剧", "能够设计复杂情节和转折", 60),
                ("advanced_plotter", "高级编剧", "能够设计多线叙事", 80),
                ("expert_plotter", "专家编剧", "能够设计史诗级故事", 90),
                ("master_plotter", "大师编剧", "开创性叙事革新", 96),
            ],
            SkillType.DIALOGUE: [
                ("novice_dialogue", "新手对话", "能够写出基本对话", 20),
                ("beginner_dialogue", "入门对话", "对话自然流畅", 40),
                ("intermediate_dialogue", "中级对话", "对话体现角色性格", 60),
                ("advanced_dialogue", "高级对话", "对话推动情节发展", 80),
                ("expert_dialogue", "专家对话", "对话富有潜台词", 90),
                ("master_dialogue", "大师对话", "对话即故事", 96),
            ],
        }

        for skill_type, milestones in default_milestones.items():
            self.milestones[skill_type] = [
                SkillMilestone(
                    id=f"{skill_type.value}_{name}",
                    skill_type=skill_type,
                    name=name,
                    description=description,
                    required_score=score
                )
                for name, description, score in milestones
            ]

    def record_skill_score(
        self,
        skill_type: SkillType,
        score: float,
        evidence: Optional[Dict[str, Any]] = None
    ):
        """记录技能分数"""
        self.skill_scores[skill_type].append(score)

        # 检查里程碑
        if skill_type in self.milestones:
            for milestone in self.milestones[skill_type]:
                milestone.check(score)

        # 添加到成长历史
        self.growth_history.append(GrowthDataPoint(
            timestamp=datetime.now(),
            skill_scores={k: self._get_latest_score(k) for k in SkillType},
            activities=[f"assessed_{skill_type.value}"]
        ))

        self._save_data()

    def assess_skill(
        self,
        skill_type: SkillType,
        content: str,
        context: Dict[str, Any]
    ) -> SkillAssessment:
        """评估技能"""
        # 简化实现：基于多维度评分
        scores = []

        # 1. 内容长度和复杂度
        word_count = len(content)
        scores.append(min(50, word_count / 10))  # 最多50分

        # 2. 多样性
        if skill_type == SkillType.WRITING:
            scores.append(self._assess_writing(content))
        elif skill_type == SkillType.DIALOGUE:
            scores.append(self._assess_dialogue(content))
        elif skill_type == SkillType.PLOTTING:
            scores.append(self._assess_plot(content))

        # 3. 技术质量
        scores.append(self._assess_technical_quality(content, skill_type))

        # 计算总分
        total_score = sum(scores) / len(scores) if scores else 50

        # 确定等级
        assessment = SkillAssessment(
            skill_type=skill_type,
            score=total_score,
            level=self._get_level_from_score(total_score),
            assessed_at=datetime.now()
        )

        # 记录分数
        self.record_skill_score(skill_type, total_score, {"content": content})

        return assessment

    def _assess_writing(self, content: str) -> float:
        """评估写作"""
        score = 0

        # 词汇丰富度
        words = content.split()
        unique_words = set(words)
        if words:
            score += min(20, len(unique_words) / len(words) * 100)

        # 句子结构
        sentences = content.split('。')
        if len(sentences) > 0:
            avg_sentence_length = len(words) / len(sentences)
            if 10 <= avg_sentence_length <= 25:
                score += 20

        # 描写
        if any(c in content for c in '，。！？；：'):
            score += 10

        return min(100, score)

    def _assess_dialogue(self, content: str) -> float:
        """评估对话"""
        score = 0

        # 对话标记
        if '"' in content or '"' in content:
            score += 30

        # 轮次
        lines = [line for line in content.split('\n') if line.strip()]
        if len(lines) >= 2:
            score += 30

        # 口语化
        colloquialisms = ["嗯", "啊", "哦", "呢", "吧"]
        if any(c in content for c in colloquialisms):
            score += 20

        return min(100, score)

    def _assess_plot(self, content: str) -> float:
        """评估情节"""
        score = 0

        # 情节元素
        plot_elements = ["冲突", "转折", "高潮", "结局"]
        found_elements = sum(1 for elem in plot_elements if elem in content)
        score += found_elements * 20

        # 逻辑连接
        connectors = ["但是", "然后", "因此", "所以"]
        connector_count = sum(1 for conn in connectors if conn in content)
        score += min(20, connector_count * 10)

        return min(100, score)

    def _assess_technical_quality(self, content: str, skill_type: SkillType) -> float:
        """评估技术质量"""
        score = 0

        # 基础质量检查
        if content.strip():
            score += 20

        # 特定技能的质量指标
        if skill_type == SkillType.DIALOGUE:
            # 对话格式
            if '"' in content or '"' in content:
                score += 20

        elif skill_type == SkillType.WRITING:
            # 段落结构
            if '\n' in content or '。' in content:
                score += 20

        return min(100, score)

    def _get_level_from_score(self, score: float) -> SkillLevel:
        """从分数获取等级"""
        if score >= 96:
            return SkillLevel.MASTER
        elif score >= 81:
            return SkillLevel.EXPERT
        elif score >= 61:
            return SkillLevel.ADVANCED
        elif score >= 41:
            return SkillLevel.INTERMEDIATE
        elif score >= 21:
            return SkillLevel.BEGINNER
        else:
            return SkillLevel.NOVICE

    def _get_latest_score(self, skill_type: SkillType) -> float:
        """获取最新分数"""
        scores = self.skill_scores.get(skill_type, [])
        return scores[-1] if scores else 0

    def get_skill_profile(self) -> Dict[str, Any]:
        """获取技能概况"""
        profile = {}

        for skill_type in SkillType:
            scores = self.skill_scores.get(skill_type, [])
            if scores:
                latest_score = scores[-1]
                avg_score = sum(scores) / len(scores)

                # 计算趋势
                if len(scores) >= 3:
                    recent_avg = sum(scores[-3:]) / 3
                    trend = recent_avg - avg_score
                else:
                    trend = 0

                profile[skill_type.value] = {
                    "latest_score": latest_score,
                    "average_score": round(avg_score, 2),
                    "level": self._get_level_from_score(latest_score).value,
                    "trend": round(trend, 2),
                    "assessment_count": len(scores),
                }
            else:
                profile[skill_type.value] = {
                    "latest_score": 0,
                    "average_score": 0,
                    "level": SkillLevel.NOVICE.value,
                    "trend": 0,
                    "assessment_count": 0
                }

        return profile

    def get_milestones_progress(self, skill_type: SkillType) -> List[Dict[str, Any]]:
        """获取里程碑进度"""
        milestones = self.milestones.get(skill_type, [])

        return [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "required_score": m.required_score,
                "achieved": m.achieved,
                "current_score": self._get_latest_score(skill_type),
                "progress_pct": min(100, (self._get_latest_score(skill_type) / m.required_score) * 100)
            }
            for m in milestones
        ]

    def get_learning_path(
        self,
        skill_type: SkillType,
        target_level: SkillLevel
    ) -> LearningPath:
        """获取学习路径"""
        current_level = self._get_level_from_score(self._get_latest_score(skill_type))

        # 估算所需时间（每个等级约30天）
        level_order = [
            SkillLevel.NOVICE,
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
            SkillLevel.MASTER
        ]

        current_idx = level_order.index(current_level)
        target_idx = level_order.index(target_level)

        resources = []
        exercises = []

        # 生成学习资源和练习
        for i in range(current_idx, target_idx):
            level = level_order[i]
            next_level = level_order[i + 1] if i + 1 < len(level_order) else None

            if next_level:
                # 查找下一个里程碑
                next_milestone = None
                if skill_type in self.milestones:
                    for m in self.milestones[skill_type]:
                        if m.required_score > self._get_latest_score(skill_type):
                            next_milestone = m
                            break

                resources.append({
                    "level": level.value,
                    "target_level": next_level.value if next_level else None,
                    "resources": f"学习资源 for {level.value}",
                    "estimated_days": 30
                })

                exercises.append({
                    "level": level.value,
                    "exercises": f"练习任务 for {level.value}",
                })

        return LearningPath(
            skill_type=skill_type,
            current_level=current_level,
            target_level=target_level,
            resources=resources,
            exercises=exercises,
            estimated_duration_days=(target_idx - current_idx) * 30
        )

    def get_growth_statistics(self) -> Dict[str, Any]:
        """获取成长统计"""
        if not self.growth_history:
            return {"message": "No growth data yet"}

        first_point = self.growth_history[0]
        latest_point = self.growth_history[-1]

        # 计算总体成长
        growth = {}
        for skill_type in SkillType:
            first_score = first_point.skill_scores.get(skill_type, 0)
            latest_score = latest_point.skill_scores.get(skill_type, 0)
            growth[skill_type.value] = latest_score - first_score

        return {
            "first_assessment": first_point.timestamp.isoformat(),
            "latest_assessment": latest_point.timestamp.isoformat(),
            "total_assessments": len(self.growth_history),
            "skill_growth": {k: round(v, 2) for k, v in growth.items()},
            "active_skills": len([s for s, scores in self.skill_scores.items() if scores]),
        }


# 全局技能追踪器实例
_skill_tracker: Optional[SkillTracker] = None


def get_skill_tracker(storage_path: Optional[str] = None) -> SkillTracker:
    """获取技能追踪器单例"""
    global _skill_tracker
    if _skill_tracker is None:
        _skill_tracker = SkillTracker(storage_path)
    return _skill_tracker

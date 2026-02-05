"""
Basic User Profiling - 基础用户画像
创作指纹和意图追踪
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
from collections import Counter


class CreativeStyle(Enum):
    """创作风格"""
    DESCRIPTIVE = "descriptive"  # 描写型
    DIALOGUE_HEAVY = "dialogue_heavy"  # 对话型
    ACTION_FOCUSED = "action_focused"  # 动作型
    ATMOSPHERIC = "atmospheric"  # 氛围型
    MINIMALIST = "minimalist"  # 极简型
    EXPERIMENTAL = "experimental"  # 实验型


class IntentType(Enum):
    """意图类型"""
    CREATE = "create"  # 创建
    EDIT = "edit"  # 编辑
    SEARCH = "search"  # 搜索
    EXPLORE = "explore"  # 探索
    EXPORT = "export"  # 导出
    TEST = "test"  # 测试


@dataclass
class CreativeFingerprint:
    """创作指纹"""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 风格特征
    primary_style: CreativeStyle = CreativeStyle.DESCRIPTIVE
    style_scores: Dict[str, float] = field(default_factory=dict)  # 各风格得分

    # 内容偏好
    preferred_genres: List[str] = field(default_factory=list)
    preferred_themes: List[str] = field(default_factory=list)
    preferred_pov: str = "third"  # 视角偏好

    # 创作习惯
    avg_session_length: float = 0.0  # 平均会话长度（分钟）
    avg_words_per_session: int = 0  # 平均每会话字数
    most_active_time: str = ""  # 最活跃时间段

    # 技能水平
    writing_skill_score: float = 3.0  # 写作技能评分（1-5）
    creativity_score: float = 3.0  # 创意评分（1-5）
    consistency_score: float = 3.0  # 一致性评分（1-5）

    # 统计
    total_sessions: int = 0
    total_words_written: int = 0
    total_assets_created: int = 0

    def update_style_scores(self, new_scores: Dict[str, float]):
        """更新风格得分"""
        for style, score in new_scores.items():
            if style in self.style_scores:
                # 加权平均
                old_score = self.style_scores[style]
                self.style_scores[style] = (old_score * 0.7 + score * 0.3)
            else:
                self.style_scores[style] = score

        # 更新主要风格
        if self.style_scores:
            self.primary_style = CreativeStyle(
                max(self.style_scores.items(), key=lambda x: x[1])[0]
            )

        self.updated_at = datetime.now()

    def record_session(self, duration_minutes: float, word_count: int):
        """记录创作会话"""
        self.total_sessions += 1
        self.total_words_written += word_count

        # 更新平均值
        self.avg_session_length = (
            (self.avg_session_length * (self.total_sessions - 1) + duration_minutes) /
            self.total_sessions
        )
        self.avg_words_per_session = (
            (self.avg_words_per_session * (self.total_sessions - 1) + word_count) /
            self.total_sessions
        )

        self.updated_at = datetime.now()


@dataclass
class Intent:
    """用户意图"""
    intent_type: IntentType
    confidence: float  # 置信度 0-1
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def resolve(self):
        """标记意图已解决"""
        self.resolved = True


@dataclass
class UserAction:
    """用户行为"""
    action_type: str  # 行为类型
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None  # 持续时间


class IntentTracker:
    """意图追踪器"""

    def __init__(self):
        self.intents: List[Intent] = []
        self.actions: List[UserAction] = []

    def record_action(self, action: UserAction):
        """记录用户行为"""
        self.actions.append(action)

    def infer_intent(self, recent_actions: int = 5) -> Optional[Intent]:
        """从行为推断意图"""
        if not self.actions:
            return None

        # 获取最近的行为
        recent = self.actions[-recent_actions:]

        # 简单的规则推断
        action_counts = Counter(a.action_type for a in recent)

        # 判断主要意图
        if action_counts["create_node"] > 0 or action_counts["write_content"] > 0:
            return Intent(
                intent_type=IntentType.CREATE,
                confidence=0.8,
                context={"action_counts": dict(action_counts)}
            )

        if action_counts["search"] > 0:
            return Intent(
                intent_type=IntentType.SEARCH,
                confidence=0.7,
                context={"search_terms": [a.context.get("query") for a in recent if a.action_type == "search"]}
            )

        if action_counts["export"] > 0:
            return Intent(
                intent_type=IntentType.EXPORT,
                confidence=0.9,
                context={}
            )

        return None

    def get_intent_history(self, limit: int = 10) -> List[Intent]:
        """获取意图历史"""
        return self.intents[-limit:]


class UserProfileManager:
    """用户画像管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/user_profiles.json"
        self.profiles: Dict[str, CreativeFingerprint] = {}
        self.intent_tracker = IntentTracker()

        # 创建数据目录
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # 加载已保存的画像
        self._load_profiles()

    def _load_profiles(self):
        """加载用户画像"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for user_id, profile_data in data.get("profiles", {}).items():
                self.profiles[user_id] = self._dict_to_fingerprint(profile_data)

        except Exception as e:
            print(f"Error loading profiles: {e}")

    def _save_profiles(self):
        """保存用户画像"""
        try:
            data = {
                "profiles": {
                    user_id: self._fingerprint_to_dict(profile)
                    for user_id, profile in self.profiles.items()
                },
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving profiles: {e}")

    def _fingerprint_to_dict(self, fingerprint: CreativeFingerprint) -> Dict[str, Any]:
        """将指纹转换为字典"""
        return {
            "user_id": fingerprint.user_id,
            "created_at": fingerprint.created_at.isoformat(),
            "updated_at": fingerprint.updated_at.isoformat(),
            "primary_style": fingerprint.primary_style.value,
            "style_scores": fingerprint.style_scores,
            "preferred_genres": fingerprint.preferred_genres,
            "preferred_themes": fingerprint.preferred_themes,
            "preferred_pov": fingerprint.preferred_pov,
            "avg_session_length": fingerprint.avg_session_length,
            "avg_words_per_session": fingerprint.avg_words_per_session,
            "most_active_time": fingerprint.most_active_time,
            "writing_skill_score": fingerprint.writing_skill_score,
            "creativity_score": fingerprint.creativity_score,
            "consistency_score": fingerprint.consistency_score,
            "total_sessions": fingerprint.total_sessions,
            "total_words_written": fingerprint.total_words_written,
            "total_assets_created": fingerprint.total_assets_created,
        }

    def _dict_to_fingerprint(self, data: Dict[str, Any]) -> CreativeFingerprint:
        """从字典创建指纹"""
        return CreativeFingerprint(
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            primary_style=CreativeStyle(data["primary_style"]),
            style_scores=data.get("style_scores", {}),
            preferred_genres=data.get("preferred_genres", []),
            preferred_themes=data.get("preferred_themes", []),
            preferred_pov=data.get("preferred_pov", "third"),
            avg_session_length=data.get("avg_session_length", 0.0),
            avg_words_per_session=data.get("avg_words_per_session", 0),
            most_active_time=data.get("most_active_time", ""),
            writing_skill_score=data.get("writing_skill_score", 3.0),
            creativity_score=data.get("creativity_score", 3.0),
            consistency_score=data.get("consistency_score", 3.0),
            total_sessions=data.get("total_sessions", 0),
            total_words_written=data.get("total_words_written", 0),
            total_assets_created=data.get("total_assets_created", 0),
        )

    def get_or_create_profile(self, user_id: str) -> CreativeFingerprint:
        """获取或创建用户画像"""
        if user_id not in self.profiles:
            self.profiles[user_id] = CreativeFingerprint(user_id=user_id)
            self._save_profiles()

        return self.profiles[user_id]

    def update_profile_from_action(self, user_id: str, action: UserAction, content_analysis: Optional[Dict] = None):
        """从行为更新画像"""
        profile = self.get_or_create_profile(user_id)

        # 记录行为
        self.intent_tracker.record_action(action)

        # 如果有内容分析结果，更新风格得分
        if content_analysis:
            profile.update_style_scores(content_analysis.get("style_scores", {}))

            # 更新偏好
            if "genre" in content_analysis:
                genre = content_analysis["genre"]
                if genre not in profile.preferred_genres:
                    profile.preferred_genres.append(genre)

            if "theme" in content_analysis:
                theme = content_analysis["theme"]
                if theme not in profile.preferred_themes:
                    profile.preferred_themes.append(theme)

        self._save_profiles()

    def record_session(
        self,
        user_id: str,
        duration_minutes: float,
        word_count: int
    ):
        """记录创作会话"""
        profile = self.get_or_create_profile(user_id)
        profile.record_session(duration_minutes, word_count)
        self._save_profiles()

    def get_user_intent(self, user_id: str) -> Optional[Intent]:
        """获取用户当前意图"""
        return self.intent_tracker.infer_intent()

    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像摘要"""
        profile = self.profiles.get(user_id)
        if not profile:
            return {"error": "Profile not found"}

        return {
            "user_id": profile.user_id,
            "primary_style": profile.primary_style.value,
            "style_scores": profile.style_scores,
            "preferred_genres": profile.preferred_genres,
            "preferred_themes": profile.preferred_themes,
            "writing_stats": {
                "total_sessions": profile.total_sessions,
                "total_words": profile.total_words_written,
                "avg_session_length": round(profile.avg_session_length, 2),
                "avg_words_per_session": round(profile.avg_words_per_session, 0),
            },
            "skill_scores": {
                "writing": round(profile.writing_skill_score, 2),
                "creativity": round(profile.creativity_score, 2),
                "consistency": round(profile.consistency_score, 2),
            },
            "member_since": profile.created_at.isoformat(),
            "last_active": profile.updated_at.isoformat(),
        }

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """分析内容特征"""
        analysis = {
            "word_count": len(content),
            "sentence_count": len([s for s in content.split('。') if s.strip()]),
            "style_scores": {},
            "genre": "",
            "theme": "",
        }

        # 分析风格特征
        dialogue_ratio = content.count('"') / max(len(content), 1)
        description_ratio = len([c for c in content if c in '的一是了']) / max(len(content), 1)

        analysis["style_scores"] = {
            "dialogue_heavy": min(1.0, dialogue_ratio * 100),
            "descriptive": min(1.0, description_ratio * 50),
        }

        # 推断类型和主题
        if any(word in content for word in ["战斗", "冲突", "武器"]):
            analysis["genre"] = "action"
        elif any(word in content for word in ["感情", "爱情", "喜欢"]):
            analysis["genre"] = "romance"

        if any(word in content for word in ["冒险", "探索", "旅程"]):
            analysis["theme"] = "adventure"
        elif any(word in content for word in ["成长", "学习", "进步"]):
            analysis["theme"] = "growth"

        return analysis


# 全局画像管理器实例
_profile_manager: Optional[UserProfileManager] = None


def get_profile_manager(storage_path: Optional[str] = None) -> UserProfileManager:
    """获取画像管理器单例"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UserProfileManager(storage_path)
    return _profile_manager

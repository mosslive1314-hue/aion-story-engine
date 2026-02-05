"""
AI 辅助创作服务
整合 LLM 和 Prompt 模板，提供创作辅助功能
"""

import asyncio
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass

from .llm import LLMService, get_llm_service, LLMProvider
from .ai_prompts import (
    get_template,
    PromptTemplate,
    DEFAULT_PARAMS
)


@dataclass
class CompletionSuggestion:
    """补全建议"""
    text: str
    confidence: float
    source: str = "ai"


@dataclass
class DialogueResponse:
    """对话响应"""
    character_name: str
    dialogue: str
    emotion: Optional[str] = None
    action: Optional[str] = None


@dataclass
class PlotSuggestion:
    """情节建议"""
    title: str
    development: str
    conflict: str
    twist: str


class AIAssistantService:
    """AI 辅助创作服务"""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        provider: LLMProvider = LLMProvider.CLAUDE
    ):
        self.llm = llm_service or get_llm_service(provider=provider)

    async def complete_content(
        self,
        context: str,
        min_words: int = 100,
        max_words: int = 500,
        additional_requirements: str = "",
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """智能内容补全"""
        template = get_template("content_completion")
        if not template:
            raise ValueError("Template not found: content_completion")

        # 格式化 Prompt
        prompt = template.format(
            context=context,
            min_words=min_words,
            max_words=max_words,
            additional_requirements=additional_requirements or "无特殊要求"
        )

        # 调用 LLM
        if stream:
            async for chunk in self.llm.generate_stream(
                prompt=prompt,
                context=template.get_system_prompt(),
                temperature=0.8
            ):
                yield chunk
        else:
            response = await self.llm.generate(
                prompt=prompt,
                context=template.get_system_prompt(),
                temperature=0.8
            )
            return response.content

    async def generate_dialogue(
        self,
        character_name: str,
        personality: str,
        background: str,
        current_state: str,
        scene_context: str,
        dialogue_history: str = "",
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """生成角色对话"""
        template = get_template("character_dialogue")
        if not template:
            raise ValueError("Template not found: character_dialogue")

        prompt = template.format(
            character_name=character_name,
            personality=personality,
            background=background,
            current_state=current_state,
            scene_context=scene_context,
            dialogue_history=dialogue_history or "（无对话历史）"
        )

        if stream:
            async for chunk in self.llm.generate_stream(
                prompt=prompt,
                context=template.get_system_prompt(),
                temperature=0.9
            ):
                yield chunk
        else:
            response = await self.llm.generate(
                prompt=prompt,
                context=template.get_system_prompt(),
                temperature=0.9
            )
            return response.content

    async def suggest_plot(
        self,
        current_plot: str,
        genre: str,
        characters: str,
        existing_clues: str = "",
        num_suggestions: int = 3
    ) -> List[PlotSuggestion]:
        """提供情节建议"""
        template = get_template("plot_suggestion")
        if not template:
            raise ValueError("Template not found: plot_suggestion")

        prompt = template.format(
            current_plot=current_plot,
            genre=genre,
            characters=characters,
            existing_clues=existing_clues or "暂无特殊线索",
            num_suggestions=num_suggestions
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.9,
            max_tokens=2000
        )

        # 解析响应
        return self._parse_plot_suggestions(response.content)

    def _parse_plot_suggestions(self, response: str) -> List[PlotSuggestion]:
        """解析情节建议响应"""
        suggestions = []
        current_suggestion = None
        current_field = None

        for line in response.split('\n'):
            line = line.strip()

            # 新建议
            if line.startswith('建议') and '：' in line:
                if current_suggestion:
                    suggestions.append(current_suggestion)

                title = line.split('：')[1].strip()
                current_suggestion = PlotSuggestion(
                    title=title,
                    development="",
                    conflict="",
                    twist=""
                )

            # 各个字段
            elif '情节发展：' in line:
                current_field = 'development'
                if current_suggestion:
                    current_suggestion.development = line.split('情节发展：')[1].strip()
            elif '冲突点：' in line:
                current_field = 'conflict'
                if current_suggestion:
                    current_suggestion.conflict = line.split('冲突点：')[1].strip()
            elif '转折：' in line:
                current_field = 'twist'
                if current_suggestion:
                    current_suggestion.twist = line.split('转折：')[1].strip()
            elif line and current_suggestion and current_field:
                # 继续当前字段的内容
                if current_field == 'development':
                    current_suggestion.development += ' ' + line
                elif current_field == 'conflict':
                    current_suggestion.conflict += ' ' + line
                elif current_field == 'twist':
                    current_suggestion.twist += ' ' + line

        # 添加最后一个建议
        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions

    async def expand_text(
        self,
        original_text: str,
        expansion_ratio: int = 2
    ) -> str:
        """扩写文本"""
        template = get_template("text_expansion")
        if not template:
            raise ValueError("Template not found: text_expansion")

        prompt = template.format(
            original_text=original_text,
            expansion_ratio=expansion_ratio
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.7,
            max_tokens=3000
        )

        return response.content

    async def polish_text(
        self,
        original_text: str,
        polish_goals: str = "提升表达，增强感染力"
    ) -> str:
        """润色文本"""
        template = get_template("text_polish")
        if not template:
            raise ValueError("Template not found: text_polish")

        prompt = template.format(
            original_text=original_text,
            polish_goals=polish_goals
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.6
        )

        return response.content

    async def create_character(
        self,
        requirements: str,
        story_background: str
    ) -> str:
        """创建角色"""
        template = get_template("character_creation")
        if not template:
            raise ValueError("Template not found: character_creation")

        prompt = template.format(
            requirements=requirements,
            story_background=story_background
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.8,
            max_tokens=1500
        )

        return response.content

    async def describe_scene(
        self,
        location: str,
        time: str,
        weather: str,
        atmosphere: str,
        purpose: str,
        min_words: int = 150,
        max_words: int = 400
    ) -> str:
        """描述场景"""
        template = get_template("scene_description")
        if not template:
            raise ValueError("Template not found: scene_description")

        prompt = template.format(
            location=location,
            time=time,
            weather=weather,
            atmosphere=atmosphere,
            purpose=purpose,
            min_words=min_words,
            max_words=max_words
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.8,
            max_tokens=1000
        )

        return response.content

    async def generate_opening(
        self,
        genre: str,
        theme: str,
        style: str,
        key_elements: str,
        min_words: int = 200,
        max_words: int = 500
    ) -> str:
        """生成故事开头"""
        template = get_template("story_opening")
        if not template:
            raise ValueError("Template not found: story_opening")

        prompt = template.format(
            genre=genre,
            theme=theme,
            style=style,
            key_elements=key_elements,
            min_words=min_words,
            max_words=max_words
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.9,
            max_tokens=1500
        )

        return response.content

    async def design_twist(
        self,
        current_plot: str,
        twist_requirements: str,
        existing_foreshadowing: str = ""
    ) -> str:
        """设计情节转折"""
        template = get_template("plot_twist")
        if not template:
            raise ValueError("Template not found: plot_twist")

        prompt = template.format(
            current_plot=current_plot,
            twist_requirements=twist_requirements,
            existing_foreshadowing=existing_foreshadowing or "暂无伏笔"
        )

        response = await self.llm.generate(
            prompt=prompt,
            context=template.get_system_prompt(),
            temperature=0.9,
            max_tokens=2000
        )

        return response.content

    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return self.llm.get_stats()


# 全局服务实例
_ai_assistant: Optional[AIAssistantService] = None


def get_ai_assistant(
    provider: LLMProvider = LLMProvider.CLAUDE,
    api_key: Optional[str] = None
) -> AIAssistantService:
    """获取 AI 助手服务单例"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistantService(
            llm_service=get_llm_service(provider=provider, api_key=api_key)
        )
    return _ai_assistant

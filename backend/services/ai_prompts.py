"""
AI Prompt 模板库
为不同场景优化的 Prompt 模板
"""

from typing import Optional, Dict, Any, List


class PromptTemplate:
    """Prompt 模板基类"""

    def __init__(
        self,
        template: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.template = template
        self.system_prompt = system_prompt
        self.parameters = parameters or {}

    def format(self, **kwargs) -> str:
        """格式化模板"""
        return self.template.format(**kwargs)

    def get_system_prompt(self) -> Optional[str]:
        """获取系统提示"""
        return self.system_prompt

    def get_parameters(self) -> Dict[str, Any]:
        """获取参数定义"""
        return self.parameters


# ============================================================================
# 内容补全模板
# ============================================================================

CONTENT_COMPLETION = PromptTemplate(
    template="""请根据以下上下文，续写内容：

【上下文】
{context}

【要求】
1. 保持与前文的风格和语气一致
2. 字数控制在 {min_words} 到 {max_words} 字之间
3. 逻辑连贯，情节自然
4. {additional_requirements}

请直接开始续写，不要添加任何说明：""",
    system_prompt="""你是一位专业的创作助手，擅长根据上下文续写故事内容。你需要保持原有风格，确保情节连贯，语言流畅。""",
    parameters={
        "context": "上下文内容",
        "min_words": "最少字数（默认100）",
        "max_words": "最多字数（默认500）",
        "additional_requirements": "额外要求（可选）"
    }
)

# ============================================================================
# 角色对话生成模板
# ============================================================================

CHARACTER_DIALOGUE = PromptTemplate(
    template="""请为以下角色生成对话：

【角色信息】
姓名：{character_name}
性格：{personality}
背景：{background}
当前状态：{current_state}

【对话场景】
{scene_context}

【对话历史】
{dialogue_history}

【要求】
1. 对话要符合角色的性格特点
2. 考虑角色当前的状态和情绪
3. 与对话历史保持连贯
4. 自然真实，避免生硬
5. 语言风格要贴合角色设定

请生成角色的回应（只输出对话内容）：""",
    system_prompt="""你是一位专业的角色扮演专家，擅长为不同性格的角色创作符合人设的对话。你需要深入理解角色的性格、背景和当前状态，生成真实自然、富有感染力的对话。""",
    parameters={
        "character_name": "角色姓名",
        "personality": "角色性格",
        "background": "角色背景",
        "current_state": "当前状态",
        "scene_context": "对话场景",
        "dialogue_history": "对话历史"
    }
)

# ============================================================================
# 情节建议模板
# ============================================================================

PLOT_SUGGESTION = PromptTemplate(
    template="""根据以下情节，请提供创意建议：

【当前情节】
{current_plot}

【故事类型】
{genre}

【已有角色】
{characters}

【已有线索】
{existing_clues}

【要求】
1. 提供 {num_suggestions} 个不同的情节发展方向
2. 每个建议要包含冲突、转折或意外
3. 考虑已有角色的特点和关系
4. 可以埋下伏笔或呼应前文
5. 创意独特，避免俗套

请按以下格式输出：
建议1：[标题]
- 情节发展：...
- 冲突点：...
- 转折：...

建议2：...""",
    system_prompt="""你是一位富有创意的故事策划专家，擅长为小说、影视等内容提供情节建议。你的建议总是出人意料又合情合理，能够推动故事向更有趣的方向发展。""",
    parameters={
        "current_plot": "当前情节",
        "genre": "故事类型",
        "characters": "已有角色",
        "existing_clues": "已有线索",
        "num_suggestions": "建议数量（默认3个）"
    }
)

# ============================================================================
# 文本扩写模板
# ============================================================================

TEXT_EXPANSION = PromptTemplate(
    template="""请对以下文本进行扩写：

【原文】
{original_text}

【扩写要求】
1. 扩写倍数：{expansion_ratio}x
2. 保持原文的核心内容和主旨
3. 增加细节描述（环境、心理、动作等）
4. 丰富表达，增强感染力
5. 保持原文的风格和基调

请直接输出扩写后的内容：""",
    system_prompt="""你是一位专业的文字编辑，擅长在不改变原文主旨的前提下，通过增加细节、丰富描写来扩写文本，使其更加生动饱满。""",
    parameters={
        "original_text": "原文内容",
        "expansion_ratio": "扩写倍数（如2、3等）"
    }
)

# ============================================================================
# 文本润色模板
# ============================================================================

TEXT_POLISH = PromptTemplate(
    template="""请对以下文本进行润色优化：

【原文】
{original_text}

【润色目标】
{polish_goals}

【要求】
1. 保持原文的核心意思
2. 提升表达的准确性和流畅度
3. 增强文本的感染力
4. 修正语法和用词错误
5. 保持整体风格一致

请输出润色后的文本：""",
    system_prompt="""你是一位专业的文学编辑，擅长润色和优化文本。你能够在保持原文意思的基础上，显著提升文本的表达质量和阅读体验。""",
    parameters={
        "original_text": "原文内容",
        "polish_goals": "润色目标（如：提升表达、增强感染力、统一风格等）"
    }
)

# ============================================================================
# 角色创建模板
# ============================================================================

CHARACTER_CREATION = PromptTemplate(
    template="""请创建一个原创角色：

【角色要求】
{requirements}

【故事背景】
{story_background}

【要求】
1. 角色要有鲜明的性格特点
2. 背景故事要合理且有深度
3. 外貌描写要生动
4. 语言风格要贴合角色设定
5. 避免脸谱化和刻板印象

请按以下格式输出：
姓名：
年龄：
外貌：
性格：
背景：
语言风格：
其他特点：""",
    system_prompt="""你是一位专业的角色设计专家，擅长创造立体、鲜活、有深度的角色。你设计的角色总是让人过目不忘，具有独特的魅力。""",
    parameters={
        "requirements": "角色要求（如：主角的对手、神秘人物等）",
        "story_background": "故事背景"
    }
)

# ============================================================================
# 场景描述模板
# ============================================================================

SCENE_DESCRIPTION = PromptTemplate(
    template="""请描述以下场景：

【场景信息】
地点：{location}
时间：{time}
天气：{weather}
氛围：{atmosphere}

【场景目的】
{purpose}

【要求】
1. 运用五感（视、听、嗅、味、触）描写
2. 突出场景的氛围和基调
3. 描写要细腻生动
4. 字数在 {min_words} 到 {max_words} 字之间

请直接输出场景描述：""",
    system_prompt="""你是一位专业的场景描写专家，擅长通过细腻的描写营造生动真实的场景，让读者仿佛身临其境。""",
    parameters={
        "location": "地点",
        "time": "时间",
        "weather": "天气",
        "atmosphere": "氛围",
        "purpose": "场景目的",
        "min_words": "最少字数",
        "max_words": "最多字数"
    }
)

# ============================================================================
# 开头生成模板
# ============================================================================

STORY_OPENING = PromptTemplate(
    template="""请为故事创作一个吸引人的开头：

【故事信息】
类型：{genre}
主题：{theme}
风格：{style}

【核心要素】
{key_elements}

【要求】
1. 开头要吸引人，快速抓住读者注意力
2. 建立故事的基本情境
3. 可以设置悬念或冲突
4. 语言风格要符合整体基调
5. 字数在 {min_words} 到 {max_words} 字之间

请直接输出开头：""",
    system_prompt="""你是一位资深的故事创作专家，擅长创作引人入胜的故事开头。你明白一个好的开头对于整个故事的重要性，总能在寥寥数语间抓住读者的心。""",
    parameters={
        "genre": "故事类型",
        "theme": "主题",
        "style": "风格",
        "key_elements": "核心要素",
        "min_words": "最少字数",
        "max_words": "最多字数"
    }
)

# ============================================================================
# 情节转折模板
# ============================================================================

PLOT_TWIST = PromptTemplate(
    template="""请为以下情节设计一个出人意料的转折：

【当前情节】
{current_plot}

【转折要求】
{twist_requirements}

【已有伏笔】
{existing_foreshadowing}

【要求】
1. 转折要出人意料但合情合理
2. 能够重新定义之前的情节
3. 如果有伏笔，要巧妙呼应
4. 避免俗套和机械降神
5. 为后续发展打开新的可能性

请输出：
转折设计：
实施方式：
前情呼应：
后续影响：""",
    system_prompt="""你是一位擅长设计情节转折的大师，总能在读者意想不到的地方埋下伏笔，然后在合适的时机给出令人震撼又合情合理的转折。""",
    parameters={
        "current_plot": "当前情节",
        "twist_requirements": "转折要求",
        "existing_foreshadowing": "已有伏笔"
    }
)

# ============================================================================
# 工具函数
# ============================================================================

def get_template(template_name: str) -> Optional[PromptTemplate]:
    """获取指定模板"""
    templates = {
        "content_completion": CONTENT_COMPLETION,
        "character_dialogue": CHARACTER_DIALOGUE,
        "plot_suggestion": PLOT_SUGGESTION,
        "text_expansion": TEXT_EXPANSION,
        "text_polish": TEXT_POLISH,
        "character_creation": CHARACTER_CREATION,
        "scene_description": SCENE_DESCRIPTION,
        "story_opening": STORY_OPENING,
        "plot_twist": PLOT_TWIST,
    }

    return templates.get(template_name)


def list_templates() -> List[str]:
    """列出所有可用模板"""
    return [
        "content_completion",
        "character_dialogue",
        "plot_suggestion",
        "text_expansion",
        "text_polish",
        "character_creation",
        "scene_description",
        "story_opening",
        "plot_twist",
    ]


# 默认参数
DEFAULT_PARAMS = {
    "min_words": 100,
    "max_words": 500,
    "num_suggestions": 3,
    "expansion_ratio": 2,
}

"""
LLM API 集成模块
支持 Claude API 和 OpenAI GPT API
"""

import os
import json
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import httpx


class LLMProvider(Enum):
    """LLM 提供商"""
    CLAUDE = "claude"
    GPT = "gpt"


class LLMModel(Enum):
    """支持的 LLM 模型"""
    # Claude 模型
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"

    # GPT 模型
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"


@dataclass
class LLMMessage:
    """LLM 消息"""
    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    tokens_used: int = 0
    finish_reason: str = ""
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMRequestStats:
    """LLM 请求统计"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0
    errors: int = 0


class ClaudeClient:
    """Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    async def generate(
        self,
        messages: List[LLMMessage],
        model: str = LLMModel.CLAUDE_SONNET.value,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> LLMResponse:
        """生成文本"""
        # 转换消息格式
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        request_data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=request_data
            )
            response.raise_for_status()
            data = response.json()

        # 提取响应
        content = data["content"][0]["text"]
        tokens = data.get("usage", {}).get("input_tokens", 0) + \
                 data.get("usage", {}).get("output_tokens", 0)

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens,
            finish_reason=data.get("stop_reason", ""),
            raw_response=data
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str = LLMModel.CLAUDE_SONNET.value,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        request_data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.base_url,
                headers=self.headers,
                json=request_data
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if data["type"] == "content_block_delta":
                                yield data["delta"]["text"]
                        except (json.JSONDecodeError, KeyError):
                            continue


class GPTClient:
    """OpenAI GPT API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate(
        self,
        messages: List[LLMMessage],
        model: str = LLMModel.GPT_4_TURBO.value,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> LLMResponse:
        """生成文本"""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        request_data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=request_data
            )
            response.raise_for_status()
            data = response.json()

        # 提取响应
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens,
            finish_reason=data["choices"][0].get("finish_reason", ""),
            raw_response=data
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str = LLMModel.GPT_4_TURBO.value,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        request_data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.base_url,
                headers=self.headers,
                json=request_data
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            continue


class LLMService:
    """统一的 LLM 服务"""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.CLAUDE,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None
    ):
        self.provider = provider
        self.stats = LLMRequestStats()

        if provider == LLMProvider.CLAUDE:
            self.client = ClaudeClient(api_key)
            self.default_model = default_model or LLMModel.CLAUDE_SONNET.value
        elif provider == LLMProvider.GPT:
            self.client = GPTClient(api_key)
            self.default_model = default_model or LLMModel.GPT_4_TURBO.value
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> LLMResponse:
        """生成文本（简化接口）"""
        # 构建消息
        messages = [
            LLMMessage(role="user", content=prompt)
        ]

        if context:
            messages.insert(0, LLMMessage(role="system", content=context))

        # 调用 API
        start_time = time.time()
        try:
            response = await self.client.generate(
                messages=messages,
                model=model or self.default_model,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 更新统计
            self.stats.total_requests += 1
            self.stats.total_tokens += response.tokens_used

            return response

        except Exception as e:
            self.stats.errors += 1
            raise e

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成文本（简化接口）"""
        messages = [
            LLMMessage(role="user", content=prompt)
        ]

        if context:
            messages.insert(0, LLMMessage(role="system", content=context))

        async for chunk in self.client.generate_stream(
            messages=messages,
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature
        ):
            yield chunk

    def get_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "total_requests": self.stats.total_requests,
            "total_tokens": self.stats.total_tokens,
            "cache_hits": self.stats.cache_hits,
            "errors": self.stats.errors,
            "provider": self.provider.value,
            "model": self.default_model
        }


# 全局服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service(
    provider: LLMProvider = LLMProvider.CLAUDE,
    api_key: Optional[str] = None
) -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(provider=provider, api_key=api_key)
    return _llm_service


# 估算成本（美元/1K tokens）
COST_PER_1K_TOKENS = {
    LLMModel.CLAUDE_SONNET: {"input": 0.003, "output": 0.015},
    LLMModel.CLAUDE_HAIKU: {"input": 0.0008, "output": 0.004},
    LLMModel.GPT_4: {"input": 0.03, "output": 0.06},
    LLMModel.GPT_4_TURBO: {"input": 0.01, "output": 0.03},
    LLMModel.GPT_35_TURBO: {"input": 0.0005, "output": 0.0015},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """估算请求成本"""
    model_enum = None
    for m in LLMModel:
        if m.value == model:
            model_enum = m
            break

    if not model_enum or model_enum not in COST_PER_1K_TOKENS:
        return 0.0

    pricing = COST_PER_1K_TOKENS[model_enum]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return input_cost + output_cost

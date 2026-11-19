"""OpenAI chat service for the 心靈契合 consultation chatbot."""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI, OpenAIError

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)

# System prompt for the Heart Alignment consultation chatbot
SYSTEM_PROMPT = """\
你是「心靈契合」的 AI 諮詢顧問，專門幫助尋求心靈成長與深度連結的人們。
你的風格溫暖、同理、真誠，善於傾聽並提供有深度的回應。
請以中文回答，語氣親切自然，避免過於制式化。
如果用戶詢問關於活動、課程或靜修營的詳細資訊，請引導他們填寫申請表。
"""


def _get_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise AppError(
            status_code=503,
            code=ErrorCode.INTERNAL_ERROR,
            message="OpenAI API key is not configured.",
        )
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def chat_completion(messages: list[dict]) -> str:
    """Send a list of messages to OpenAI and return the assistant reply."""
    settings = get_settings()
    client = _get_client()

    # Prepend system prompt if not already present
    if not messages or messages[0].get("role") != "system":
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    else:
        full_messages = messages

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=full_messages,  # type: ignore[arg-type]
            max_tokens=settings.openai_max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""
    except OpenAIError as exc:
        logger.error("OpenAI API error: %s", exc)
        raise AppError(
            status_code=502,
            code=ErrorCode.INTERNAL_ERROR,
            message=f"AI service error: {exc}",
        ) from exc


async def chat_completion_stream(messages: list[dict]) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens from OpenAI."""
    settings = get_settings()
    client = _get_client()

    if not messages or messages[0].get("role") != "system":
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    else:
        full_messages = messages

    try:
        stream = await client.chat.completions.create(
            model=settings.openai_model,
            messages=full_messages,  # type: ignore[arg-type]
            max_tokens=settings.openai_max_tokens,
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except OpenAIError as exc:
        logger.error("OpenAI stream error: %s", exc)
        raise AppError(
            status_code=502,
            code=ErrorCode.INTERNAL_ERROR,
            message=f"AI service error: {exc}",
        ) from exc

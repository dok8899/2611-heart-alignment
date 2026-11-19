"""Chat API route – POST /api/v1/chat"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.chat_service import chat_completion, chat_completion_stream

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse, summary="心靈契合 AI 諮詢對話")
async def chat(body: ChatRequest):
    """
    傳送對話訊息給 AI 顧問並取得回覆。

    - `messages`: 完整的對話歷史（`user` / `assistant` 輪流），最後一筆必須是 `user`
    - `stream`: 設為 `true` 時以 Server-Sent Events 串流回傳
    """
    messages_dicts = [m.model_dump() for m in body.messages]

    if body.stream:
        async def event_stream():
            async for token in chat_completion_stream(messages_dicts):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    reply = await chat_completion(messages_dicts)
    return ChatResponse(reply=reply)

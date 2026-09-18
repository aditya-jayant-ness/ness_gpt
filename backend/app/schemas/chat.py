from typing import Any

from pydantic import BaseModel, HttpUrl


class ChatRequest(BaseModel):
    session_id: str
    website_url: HttpUrl
    question: str


class SourceSnippet(BaseModel):
    url: str
    title: str | None = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    tool_events: list[dict[str, Any]] = []

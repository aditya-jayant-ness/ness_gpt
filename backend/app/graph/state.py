from typing import Any, TypedDict


class ChatGraphState(TypedDict):
    session_id: str
    website_url: str
    question: str
    crawled_chunks: list[str]
    sources: list[dict[str, str]]
    answer: str
    tool_events: list[dict[str, Any]]

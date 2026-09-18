from collections import defaultdict

from app.schemas.analytics import AnalyticsSummary


class InMemoryAnalyticsStore:
    def __init__(self) -> None:
        self._messages: dict[str, list[dict]] = defaultdict(list)

    def track_message(self, session_id: str, role: str, content: str, crawled: bool, tool_used: bool) -> None:
        self._messages[session_id].append(
            {
                "role": role,
                "content": content,
                "crawled": crawled,
                "tool_used": tool_used,
            }
        )

    def summary(self, session_id: str) -> AnalyticsSummary:
        items = self._messages.get(session_id, [])
        assistant_msgs = [m for m in items if m["role"] == "assistant"]
        question_count = len([m for m in items if m["role"] == "user"])
        avg_answer_len = 0.0
        if assistant_msgs:
            avg_answer_len = sum(len(m["content"]) for m in assistant_msgs) / len(assistant_msgs)

        return AnalyticsSummary(
            session_id=session_id,
            total_messages=len(items),
            total_questions=question_count,
            avg_answer_length=avg_answer_len,
            crawl_count=len([m for m in items if m["crawled"]]),
            tool_invocations=len([m for m in items if m["tool_used"]]),
        )


analytics_store = InMemoryAnalyticsStore()

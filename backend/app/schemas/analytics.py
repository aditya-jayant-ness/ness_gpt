from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    session_id: str
    total_messages: int
    total_questions: int
    avg_answer_length: float
    crawl_count: int
    tool_invocations: int

from fastapi import APIRouter, HTTPException

from app.graph.workflow import chat_graph
from app.schemas.chat import ChatRequest, ChatResponse, SourceSnippet
from app.services.analytics.service import analytics_store

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(payload: ChatRequest) -> ChatResponse:
    initial_state = {
        "session_id": payload.session_id,
        "website_url": str(payload.website_url),
        "question": payload.question,
        "crawled_chunks": [],
        "sources": [],
        "answer": "",
        "tool_events": [],
        "crawl_stats": {},
    }

    try:
        final_state = await chat_graph.ainvoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat workflow failed: {exc}") from exc

    analytics_store.track_message(payload.session_id, "user", payload.question, crawled=False, tool_used=False)
    analytics_store.track_message(payload.session_id, "assistant", final_state["answer"], crawled=True, tool_used=False)

    return ChatResponse(
        answer=final_state["answer"],
        sources=[SourceSnippet(**s) for s in final_state["sources"]],
        tool_events=final_state["tool_events"],
    )

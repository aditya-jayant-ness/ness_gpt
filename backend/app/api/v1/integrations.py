from fastapi import APIRouter, HTTPException

from app.schemas.integrations import CalendarEventRequest, EmailRequest
from app.services.analytics.service import analytics_store
from app.services.mcp.server import mcp_server

router = APIRouter()


@router.get("/tools")
def list_tools() -> list[dict[str, str]]:
    return mcp_server.list_tools()


@router.post("/email")
def send_email(payload: EmailRequest) -> dict:
    try:
        result = mcp_server.invoke("send_email", payload.model_dump())
        analytics_store.track_message("integration", "tool", "send_email", crawled=False, tool_used=True)
        return result.output
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/calendar")
def create_calendar_event(payload: CalendarEventRequest) -> dict:
    try:
        result = mcp_server.invoke("create_calendar_event", payload.model_dump())
        analytics_store.track_message("integration", "tool", "create_calendar_event", crawled=False, tool_used=True)
        return result.output
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

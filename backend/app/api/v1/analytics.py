from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.analytics.report_pdf import build_pdf_report
from app.services.analytics.service import analytics_store

router = APIRouter()


@router.get("/{session_id}")
def session_summary(session_id: str):
    return analytics_store.summary(session_id)


@router.get("/{session_id}/report")
def session_report(session_id: str):
    summary = analytics_store.summary(session_id)
    path = build_pdf_report(summary)
    return FileResponse(path=path, filename=f"chat_report_{session_id}.pdf", media_type="application/pdf")

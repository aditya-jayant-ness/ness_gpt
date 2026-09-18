from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.schemas.analytics import AnalyticsSummary


def build_pdf_report(summary: AnalyticsSummary, output_dir: str = "reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"chat_report_{summary.session_id}.pdf"

    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "Chat Analysis Report")

    c.setFont("Helvetica", 11)
    rows = [
        f"Session ID: {summary.session_id}",
        f"Total Messages: {summary.total_messages}",
        f"Total Questions: {summary.total_questions}",
        f"Average Answer Length: {summary.avg_answer_length:.2f}",
        f"Crawl Count: {summary.crawl_count}",
        f"Tool Invocations: {summary.tool_invocations}",
    ]

    y = 710
    for row in rows:
        c.drawString(72, y, row)
        y -= 22

    c.save()
    return str(output_path)

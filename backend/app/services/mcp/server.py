from dataclasses import dataclass
from typing import Any

from app.schemas.integrations import CalendarEventRequest, EmailRequest
from app.services.integrations.calendar_google import GoogleCalendarService
from app.services.integrations.email_smtp import SMTPEmailService


@dataclass
class MCPToolResult:
    tool: str
    output: dict[str, Any]


class InternalMCPServer:
    def __init__(self) -> None:
        self.email_service = SMTPEmailService()
        self.calendar_service = GoogleCalendarService()

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": "send_email", "description": "Send email through SMTP."},
            {"name": "create_calendar_event", "description": "Create Google Calendar event."},
        ]

    def invoke(self, tool_name: str, payload: dict[str, Any]) -> MCPToolResult:
        if tool_name == "send_email":
            output = self.email_service.send(EmailRequest(**payload))
            return MCPToolResult(tool=tool_name, output=output)

        if tool_name == "create_calendar_event":
            output = self.calendar_service.create_event(CalendarEventRequest(**payload))
            return MCPToolResult(tool=tool_name, output=output)

        raise ValueError(f"Unsupported MCP tool: {tool_name}")


mcp_server = InternalMCPServer()

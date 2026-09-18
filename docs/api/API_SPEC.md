# API Spec (v1)

Base URL: http://localhost:8000/api/v1

## Chat

POST /chat/ask

Request JSON:
{
  "session_id": "string",
  "website_url": "https://example.com",
  "question": "What does this company do?"
}

Response JSON:
{
  "answer": "string",
  "sources": [
    {
      "url": "string",
      "title": "string",
      "snippet": "string"
    }
  ],
  "tool_events": []
}

## Integrations

GET /integrations/tools
- Returns available MCP tools.

POST /integrations/email
Request JSON:
{
  "to": ["person@example.com"],
  "subject": "Summary",
  "body": "..."
}

POST /integrations/calendar
Request JSON:
{
  "summary": "Meeting title",
  "description": "optional",
  "start_iso": "2026-09-18T10:00:00Z",
  "end_iso": "2026-09-18T10:30:00Z",
  "attendee_emails": ["person@example.com"]
}

## Analytics

GET /analytics/{session_id}
- Returns session metrics summary.

GET /analytics/{session_id}/report
- Returns PDF report for the session.

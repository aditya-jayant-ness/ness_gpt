from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.settings import get_settings
from app.schemas.integrations import CalendarEventRequest


class GoogleCalendarService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _build_client(self):
        if not self.settings.google_client_id or not self.settings.google_refresh_token:
            raise ValueError("Google Calendar is not configured.")

        creds = Credentials(
            None,
            refresh_token=self.settings.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.google_client_id,
            client_secret=self.settings.google_client_secret,
        )
        return build("calendar", "v3", credentials=creds)

    def create_event(self, request: CalendarEventRequest) -> dict:
        service = self._build_client()
        payload = {
            "summary": request.summary,
            "description": request.description or "",
            "start": {"dateTime": request.start_iso},
            "end": {"dateTime": request.end_iso},
            "attendees": [{"email": email} for email in request.attendee_emails],
        }
        event = service.events().insert(calendarId="primary", body=payload).execute()
        return {"status": "created", "event_id": event.get("id"), "html_link": event.get("htmlLink")}

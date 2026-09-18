from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    to: list[EmailStr]
    subject: str
    body: str


class CalendarEventRequest(BaseModel):
    summary: str
    description: str | None = None
    start_iso: str
    end_iso: str
    attendee_emails: list[EmailStr] = []

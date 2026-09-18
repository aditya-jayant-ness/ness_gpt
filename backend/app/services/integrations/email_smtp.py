import smtplib
from email.mime.text import MIMEText

from app.core.settings import get_settings
from app.schemas.integrations import EmailRequest


class SMTPEmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def send(self, request: EmailRequest) -> dict[str, str]:
        if not self.settings.smtp_host or not self.settings.smtp_from:
            raise ValueError("SMTP is not configured. Set SMTP_HOST and SMTP_FROM.")

        msg = MIMEText(request.body)
        msg["Subject"] = request.subject
        msg["From"] = self.settings.smtp_from
        msg["To"] = ", ".join(request.to)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            if self.settings.smtp_use_tls:
                server.starttls()
            if self.settings.smtp_username:
                server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.sendmail(self.settings.smtp_from, request.to, msg.as_string())

        return {"status": "sent"}

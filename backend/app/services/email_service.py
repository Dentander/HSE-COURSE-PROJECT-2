import asyncio
import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import quote
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _ascii_safe(text: str) -> str:
    return text


def _verification_html(confirm_url: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="font-family:system-ui,-apple-system,sans-serif;line-height:1.6;color:#1a1a1a;">
  <p>Здравствуйте!</p>
  <p>Спасибо за регистрацию. Чтобы завершить её, подтвердите адрес электронной почты — нажмите кнопку ниже.</p>
  <p style="margin:28px 0;">
    <a href="{confirm_url}" style="display:inline-block;padding:12px 28px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:600;">Подтвердить адрес</a>
  </p>
  <p style="font-size:13px;color:#555;">Если кнопка не открывается, скопируйте ссылку в адресную строку браузера:<br/>
  <span style="word-break:break-all;">{confirm_url}</span></p>
  <p style="font-size:13px;color:#777;margin-top:24px;">Если вы не регистрировались на нашем сервисе, просто удалите это письмо.</p>
</body>
</html>"""


def _reset_html(form_url: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="font-family:system-ui,-apple-system,sans-serif;line-height:1.5;color:#111;">
  <p>Здравствуйте!</p>
  <p>Нажмите кнопку, чтобы открыть страницу и задать новый пароль.</p>
  <p style="margin:24px 0;">
    <a href="{form_url}" style="display:inline-block;padding:12px 24px;background:#059669;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:600;">Сбросить пароль</a>
  </p>
  <p style="font-size:13px;color:#555;">Если кнопка не работает:<br/>
  <span style="word-break:break-all;">{form_url}</span></p>
</body>
</html>"""


class EmailService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_from:
            logger.warning(
                "Email skipped (SMTP not configured): to=%s subject=%s",
                to_email,
                _ascii_safe(subject),
            )
            return
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.smtp_from
        msg["To"] = to_email
        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype="html")

        def _send_sync() -> None:
            try:
                with smtplib.SMTP(
                    self.settings.smtp_host, self.settings.smtp_port
                ) as smtp:
                    if self.settings.smtp_use_tls:
                        smtp.starttls()
                    if self.settings.smtp_user and self.settings.smtp_password:
                        smtp.login(self.settings.smtp_user, self.settings.smtp_password)
                    smtp.send_message(msg)
            except Exception:
                logger.exception(
                    "Failed to send email via SMTP: host=%s port=%s user=%s to=%s subject=%s",
                    self.settings.smtp_host,
                    self.settings.smtp_port,
                    self.settings.smtp_user,
                    to_email,
                    _ascii_safe(subject),
                )

        await asyncio.to_thread(_send_sync)

    def _frontend_base(self) -> str:
        return self.settings.frontend_base_url.rstrip("/")

    async def send_verification_email(self, to_email: str, token: str) -> None:
        safe = quote(token, safe="")
        confirm_url = f"{self._frontend_base()}/verify-email?token={safe}"
        body_text = (
            "Здравствуйте!\n\n"
            "Спасибо за регистрацию. Чтобы подтвердить адрес электронной почты, перейдите по ссылке:\n\n"
            f"{confirm_url}\n\n"
            "Если вы не регистрировались на нашем сервисе, проигнорируйте это письмо.\n"
        )
        body_html = _verification_html(confirm_url)
        await self.send_email(
            to_email, "Подтвердите адрес электронной почты", body_text, body_html
        )

    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        safe = quote(token, safe="")
        reset_url = f"{self._frontend_base()}/reset-password?token={safe}"
        body_text = (
            f"Сброс пароля:\n\n{reset_url}\n\nСсылка действует ограниченное время."
        )
        body_html = _reset_html(reset_url)
        await self.send_email(to_email, "Восстановление пароля", body_text, body_html)

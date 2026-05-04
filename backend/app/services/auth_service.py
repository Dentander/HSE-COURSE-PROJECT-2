import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.core.config import Settings, get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token_payload,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas import MessageOut, UserCreate, UserOut, TokenPair
from app.services.email_service import EmailService


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        email_service: EmailService,
        settings: Settings | None = None,
    ):
        self.user_repo = user_repo
        self.email_service = email_service
        self.settings = settings or get_settings()

    def _tokens_for_user(self, user_id: int) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def register(self, data: UserCreate) -> UserOut:
        verification_token = secrets.token_urlsafe(32)
        pwd_hash = hash_password(data.password)
        email_norm = str(data.email).lower().strip()
        name_clean = data.name.strip()

        existing = await self.user_repo.get_user_by_email(email_norm)
        if existing:
            if existing.email_verified:
                raise HTTPException(
                    status_code=400,
                    detail="Этот email уже зарегистрирован. Используйте вход.",
                )
            if not await self.user_repo.update_unverified_user_for_reregistration(
                existing.user_id,
                name_clean,
                pwd_hash,
                verification_token,
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Не удалось обновить данные для повторной отправки письма.",
                )
            refreshed = await self.user_repo.get_user_by_id(existing.user_id)
            if not refreshed:
                raise HTTPException(status_code=500, detail="User not found")
            await self.email_service.send_verification_email(
                refreshed.email, verification_token
            )
            return UserOut.model_validate(refreshed)

        try:
            user = await self.user_repo.create_user(
                name_clean,
                email_norm,
                pwd_hash,
                email_verification_token=verification_token,
            )
        except ValueError:
            raced = await self.user_repo.get_user_by_email(email_norm)
            if (
                raced
                and not raced.email_verified
                and await self.user_repo.update_unverified_user_for_reregistration(
                    raced.user_id, name_clean, pwd_hash, verification_token
                )
            ):
                refreshed = await self.user_repo.get_user_by_id(raced.user_id)
                if refreshed:
                    await self.email_service.send_verification_email(
                        refreshed.email, verification_token
                    )
                    return UserOut.model_validate(refreshed)
            raise HTTPException(
                status_code=400,
                detail="Этот email уже зарегистрирован. Используйте вход.",
            )

        await self.email_service.send_verification_email(user.email, verification_token)
        return UserOut.model_validate(user)

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.user_repo.get_user_by_email(email.lower().strip())
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.email_verified:
            raise HTTPException(
                status_code=403, detail="Email не подтверждён. Проверьте почту."
            )
        return self._tokens_for_user(user.user_id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, "refresh")
            user_id = get_user_id_from_token_payload(payload)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return self._tokens_for_user(user_id)

    async def verify_email(self, token: str) -> MessageOut:
        user = await self.user_repo.get_user_by_email_verification_token(token)
        if not user:
            raise HTTPException(
                status_code=400, detail="Invalid or expired verification token"
            )
        await self.user_repo.mark_email_verified(user.user_id)
        return MessageOut(message="Email confirmed")

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> MessageOut:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        await self.user_repo.set_password_hash(user_id, hash_password(new_password))
        return MessageOut(message="Password updated")

    async def forgot_password(self, email: str) -> MessageOut:
        user = await self.user_repo.get_user_by_email(str(email).lower().strip())
        if not user:
            return MessageOut(
                message="If the email exists, reset instructions were sent"
            )
        reset_token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(
            hours=self.settings.password_reset_token_hours
        )
        await self.user_repo.set_password_reset_token(
            user.user_id, reset_token, expires
        )
        await self.email_service.send_password_reset_email(user.email, reset_token)
        return MessageOut(message="If the email exists, reset instructions were sent")

    def _utcnow_naive(self) -> datetime:
        return datetime.utcnow()

    def _as_naive_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(timezone.utc).replace(tzinfo=None)

    async def reset_password(self, token: str, new_password: str) -> MessageOut:
        user = await self.user_repo.get_user_by_password_reset_token(token)
        if not user or not user.password_reset_expires:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
        now = self._utcnow_naive()
        expires = self._as_naive_utc(user.password_reset_expires)
        if now > expires:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
        await self.user_repo.set_password_hash(
            user.user_id, hash_password(new_password)
        )
        await self.user_repo.clear_password_reset_token(user.user_id)
        return MessageOut(message="Password has been reset")

    async def validate_reset_password_token(self, token: str) -> MessageOut:
        user = await self.user_repo.get_user_by_password_reset_token(token)
        if not user or not user.password_reset_expires:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
        now = self._utcnow_naive()
        expires = self._as_naive_utc(user.password_reset_expires)
        if now > expires:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
        return MessageOut(message="Token is valid")

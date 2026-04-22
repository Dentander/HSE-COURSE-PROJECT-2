from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from .base_repository import BaseRepository
from ..models.users import Users


class UserRepository(BaseRepository):
    async def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        email_verification_token: str | None,
    ) -> Users:
        user = Users(
            name=name,
            email=email,
            password_hash=password_hash,
            email_verified=False,
            email_verification_token=email_verification_token,
        )
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("The user's email address already exists.")

    async def get_user_by_id(self, user_id: int) -> Users | None:
        stmt = select(Users).where(Users.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Users | None:
        stmt = select(Users).where(Users.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email_verification_token(self, token: str) -> Users | None:
        stmt = select(Users).where(Users.email_verification_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_password_reset_token(self, token: str) -> Users | None:
        stmt = select(Users).where(Users.password_reset_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_email_verified(self, user_id: int) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(email_verified=True, email_verification_token=None)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_password_hash(self, user_id: int, password_hash: str) -> None:
        stmt = update(Users).where(Users.user_id == user_id).values(password_hash=password_hash)
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_password_reset_token(
        self, user_id: int, token: str | None, expires: datetime | None
    ) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(password_reset_token=token, password_reset_expires=expires)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def clear_password_reset_token(self, user_id: int) -> None:
        await self.set_password_reset_token(user_id, None, None)

    async def add_xp(self, user_id: int, amount: int) -> None:
        if amount <= 0:
            return
        stmt = update(Users).where(Users.user_id == user_id).values(xp=Users.xp + amount)
        await self.session.execute(stmt)
        await self.session.commit()

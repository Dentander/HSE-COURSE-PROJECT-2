from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from .base_repository import BaseRepository
from ..models.users import Users


class UserRepository(BaseRepository):
    async def create_user(self, name: str, email: str, password_hash: str) -> Users:
        user = Users(name=name, email=email, password_hash=password_hash)
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

    async def add_xp(self, user_id: int, amount: int) -> None:
        stmt = update(Users).where(Users.user_id == user_id).values(xp=Users.xp + amount)
        await self.session.execute(stmt)

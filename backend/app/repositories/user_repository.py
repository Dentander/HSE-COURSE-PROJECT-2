from datetime import datetime
from sqlalchemy import func, select, update
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
            fire_streak=0,
            is_fire_frozen=False,
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

    async def update_unverified_user_for_reregistration(
        self,
        user_id: int,
        name: str,
        password_hash: str,
        email_verification_token: str,
    ) -> bool:
        stmt = (
            update(Users)
            .where(
                Users.user_id == user_id,
                Users.email_verified.is_(False),
            )
            .values(
                name=name,
                password_hash=password_hash,
                email_verification_token=email_verification_token,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    async def mark_email_verified(self, user_id: int) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(email_verified=True, email_verification_token=None)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_password_hash(self, user_id: int, password_hash: str) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(password_hash=password_hash)
        )
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
        stmt = (
            update(Users).where(Users.user_id == user_id).values(xp=Users.xp + amount)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_fire_streak(self, user_id: int, value: int) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(fire_streak=int(value))
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def freeze_fire_streak(self, user_id: int, locked_value: int) -> None:
        stmt = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(is_fire_frozen=True, fire_streak=int(locked_value))
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_leaderboard_top_rows(
        self, limit: int = 30, *, sort_by_fire: bool = False
    ) -> list[tuple[str, int, int, int]]:
        if sort_by_fire:
            top = (
                select(Users.user_id, Users.name, Users.xp, Users.fire_streak)
                .order_by(Users.fire_streak.desc(), Users.user_id.asc())
                .limit(limit)
                .subquery()
            )
            rank_sq = (
                select(func.count())
                .select_from(Users)
                .where(Users.fire_streak > top.c.fire_streak)
                .scalar_subquery()
                + 1
            )
        else:
            top = (
                select(Users.user_id, Users.name, Users.xp, Users.fire_streak)
                .order_by(Users.xp.desc(), Users.user_id.asc())
                .limit(limit)
                .subquery()
            )
            rank_sq = (
                select(func.count())
                .select_from(Users)
                .where(Users.xp > top.c.xp)
                .scalar_subquery()
                + 1
            )
        stmt = select(
            top.c.name, top.c.xp, top.c.fire_streak, rank_sq.label("rank")
        )
        result = await self.session.execute(stmt)
        return [
            (row.name, int(row.xp), int(row.fire_streak or 0), int(row.rank))
            for row in result.all()
        ]

    async def count_users_with_strictly_higher_xp(self, xp: int) -> int:
        stmt = select(func.count()).select_from(Users).where(Users.xp > xp)
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

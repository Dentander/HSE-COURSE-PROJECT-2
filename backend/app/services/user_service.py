from fastapi import HTTPException
from werkzeug.security import generate_password_hash

from ..repositories.user_repository import UserRepository
from ..schemas import UserCreate, UserOut


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, data: UserCreate) -> UserOut:
        password_hash = generate_password_hash(data.password)
        user = await self.user_repo.create_user(data.name, data.email, password_hash)
        return UserOut.from_orm(user)

    async def get_user_info(self, user_id: int) -> UserOut:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return UserOut.from_orm(user)

    async def add_xp(self, user_id: int, amount: int) -> None:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        await self.user_repo.add_xp(user_id, amount)

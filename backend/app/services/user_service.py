from fastapi import HTTPException

from ..repositories.user_repository import UserRepository
from ..schemas import UserOut


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_info(self, user_id: int) -> UserOut:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return UserOut.model_validate(user)

    async def add_xp(self, user_id: int, amount: int) -> None:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        await self.user_repo.add_xp(user_id, amount)

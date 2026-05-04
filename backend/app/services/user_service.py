from fastapi import HTTPException
from ..repositories.user_repository import UserRepository
from ..schemas import LeaderboardEntryOut, LeaderboardTopOut, MyXpRankOut, UserOut


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

    async def get_leaderboard_top(self, limit: int = 30) -> LeaderboardTopOut:
        rows = await self.user_repo.get_leaderboard_top_rows(limit=limit)
        entries = [
            LeaderboardEntryOut(rank=rank, name=name, xp=xp) for name, xp, rank in rows
        ]
        return LeaderboardTopOut(entries=entries)

    async def get_my_xp_rank(self, user_id: int) -> MyXpRankOut:
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        higher = await self.user_repo.count_users_with_strictly_higher_xp(user.xp)
        return MyXpRankOut(rank=higher + 1, name=user.name, xp=user.xp)

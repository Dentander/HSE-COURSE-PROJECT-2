from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas import UserOut
from app.services.user_service import UserService
from app.api.v1.dependencies import get_user_service, get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service)
):
    return await service.get_user_info(user_id)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user_info(user_id)
    return user

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import UserCreate, UserOut
from app.services.user_service import UserService
from app.api.v1.dependencies import get_user_service, get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        created_user = await service.create_user(user_data)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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

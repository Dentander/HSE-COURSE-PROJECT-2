from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.v1.dependencies import get_auth_service, get_current_user_id
from app.schemas import (
    ChangePasswordIn,
    ForgotPasswordIn,
    LoginIn,
    MessageOut,
    RefreshTokenIn,
    ResetPasswordIn,
    ResetPasswordValidateIn,
    TokenPair,
    UserCreate,
    UserOut,
    VerifyEmailIn,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    return await service.register(data)


@router.post("/login", response_model=TokenPair)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(get_auth_service),
):
    return await service.login((form.username or "").strip(), form.password)


@router.post("/login/json", response_model=TokenPair)
async def login_json(body: LoginIn, service: AuthService = Depends(get_auth_service)):
    return await service.login(str(body.email), body.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    body: RefreshTokenIn, service: AuthService = Depends(get_auth_service)
):
    return await service.refresh(body.refresh_token)


@router.post("/verify-email", response_model=MessageOut)
async def verify_email(
    body: VerifyEmailIn, service: AuthService = Depends(get_auth_service)
):
    return await service.verify_email(body.token)


@router.get("/verify-email", response_model=MessageOut)
async def verify_email_from_link(
    token: str = Query(min_length=1), service: AuthService = Depends(get_auth_service)
):
    return await service.verify_email(token)


@router.post("/change-password", response_model=MessageOut)
async def change_password(
    body: ChangePasswordIn,
    user_id: int = Depends(get_current_user_id),
    service: AuthService = Depends(get_auth_service),
):
    return await service.change_password(
        user_id, body.current_password, body.new_password
    )


@router.post("/forgot-password", response_model=MessageOut)
async def forgot_password(
    body: ForgotPasswordIn, service: AuthService = Depends(get_auth_service)
):
    return await service.forgot_password(str(body.email))


@router.post("/reset-password", response_model=MessageOut)
async def reset_password(
    body: ResetPasswordIn, service: AuthService = Depends(get_auth_service)
):
    return await service.reset_password(body.token, body.new_password)


@router.post("/reset-password/validate", response_model=MessageOut)
async def validate_reset_password_token(
    body: ResetPasswordValidateIn, service: AuthService = Depends(get_auth_service)
):
    return await service.validate_reset_password_token(body.token)

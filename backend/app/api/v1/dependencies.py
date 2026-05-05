from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token, get_user_id_from_token_payload
from app.core.config import get_settings
from app.db.database import get_db
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.course_service import CourseService
from app.services.email_service import EmailService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session(db: AsyncSession = Depends(get_db)):
    yield db


def get_email_service() -> EmailService:
    return EmailService()


async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    email: EmailService = Depends(get_email_service),
) -> AuthService:
    return AuthService(UserRepository(db), email)


async def get_user_service(db: AsyncSession = Depends(get_db_session)):
    return UserService(UserRepository(db))


async def get_course_service(
    db: AsyncSession = Depends(get_db_session),
) -> CourseService:
    return CourseService(CourseRepository(db), UserRepository(db), get_settings())


async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        payload = decode_token(token, "access")
        return get_user_id_from_token_payload(payload)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

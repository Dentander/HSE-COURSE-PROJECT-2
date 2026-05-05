import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
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

_http_basic_course_admin = HTTPBasic(auto_error=False)


async def require_course_admin_basic(
    credentials: Annotated[
        HTTPBasicCredentials | None, Depends(_http_basic_course_admin)
    ],
) -> None:
    settings = get_settings()
    expected_email = settings.course_admin_email
    expected_password = settings.course_admin_password
    if not expected_email or not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Course admin is not configured (set COURSE_ADMIN_EMAIL and COURSE_ADMIN_PASSWORD).",
        )
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    user_ok = secrets.compare_digest(
        credentials.username.strip().lower(),
        expected_email.lower(),
    )
    pass_ok = secrets.compare_digest(credentials.password, expected_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


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

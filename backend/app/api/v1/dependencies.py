from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.user_service import UserService
from app.services.learning_service import LearningService
from app.repositories.user_repository import UserRepository
from app.repositories.module_repository import ModuleRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.answer_repository import AnswerRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_db_session(db: AsyncSession = Depends(get_db)):
    yield db


async def get_learning_service(db: AsyncSession = Depends(get_db_session)):
    return LearningService(
        module_repo=ModuleRepository(db),
        material_repo=MaterialRepository(db),
        answer_repo=AnswerRepository(db),
        user_repo=UserRepository(db),
    )


async def get_user_service(db: AsyncSession = Depends(get_db_session)):
    return UserService(UserRepository(db))


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> int:
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
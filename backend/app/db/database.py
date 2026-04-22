from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

_settings = get_settings()
DATABASE_URL = _settings.database_url

_engine_kwargs: dict = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session

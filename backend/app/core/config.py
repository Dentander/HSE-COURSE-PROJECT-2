import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/education",
    )

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    smtp_host: str | None = os.getenv("SMTP_HOST") or None
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER") or None
    smtp_password: str | None = os.getenv("SMTP_PASSWORD") or None
    smtp_from: str | None = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or None
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    api_public_base_url: str = os.getenv("API_PUBLIC_BASE_URL", "http://localhost:8000")

    password_reset_token_hours: int = int(os.getenv("PASSWORD_RESET_TOKEN_HOURS", "24"))


@lru_cache
def get_settings() -> Settings:
    return Settings()

import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH, override=True)


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/education",
        )
        if not self.database_url.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql+asyncpg://' (PostgreSQL only)."
            )
        self.jwt_secret_key: str = os.getenv(
            "JWT_SECRET_KEY", "change-me-in-production"
        )
        self.jwt_algorithm: str = "HS256"
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_token_expire_days: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )
        self.smtp_host: str | None = os.getenv("SMTP_HOST") or None
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user: str | None = os.getenv("SMTP_USER") or None
        self.smtp_password: str | None = os.getenv("SMTP_PASSWORD") or None
        self.smtp_from: str | None = (
            os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or None
        )
        self.smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in (
            "1",
            "true",
            "yes",
        )
        self.frontend_base_url: str = os.getenv(
            "FRONTEND_BASE_URL", "http://localhost:5173"
        )
        self.api_public_base_url: str = os.getenv(
            "API_PUBLIC_BASE_URL", "http://localhost:8000"
        )
        self.password_reset_token_hours: int = int(
            os.getenv("PASSWORD_RESET_TOKEN_HOURS", "24")
        )
        self.task_reward_xp_penalty_per_wrong_attempt: int = max(
            0,
            int(os.getenv("TASK_REWARD_XP_PENALTY_PER_WRONG_ATTEMPT", "1")),
        )
        self.task_reward_xp_floor: int = max(
            0, int(os.getenv("TASK_REWARD_XP_FLOOR", "0"))
        )
        self.course_admin_email: str = (os.getenv("COURSE_ADMIN_EMAIL") or "").strip()
        self.course_admin_password: str = (
            os.getenv("COURSE_ADMIN_PASSWORD") or ""
        ).strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()

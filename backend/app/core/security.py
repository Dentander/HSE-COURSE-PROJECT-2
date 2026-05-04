from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from werkzeug.security import check_password_hash, generate_password_hash
from app.core.config import get_settings


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(plain: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    subject_user_id: int, extra_claims: dict[str, Any] | None = None
) -> str:
    settings = get_settings()
    expire = _utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(subject_user_id),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(subject_user_id: int) -> str:
    settings = get_settings()
    expire = _utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(subject_user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    return payload


def get_user_id_from_token_payload(payload: dict[str, Any]) -> int:
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Missing subject")
    return int(sub)

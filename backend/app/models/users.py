from sqlalchemy import Boolean, Column, DateTime, Integer, String, false
from sqlalchemy.sql import func
from app.db.base import Base


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    email_verified = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    email_verification_token = Column(String, nullable=True, index=True)
    password_reset_token = Column(String, nullable=True, index=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    email_verified: bool = False
    xp: int = 0

    class Config:
        from_attributes = True

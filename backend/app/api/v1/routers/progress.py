from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_course_service, get_current_user_id
from app.services.course_service import CourseService

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressMarkIn(BaseModel):
    topicId: str = Field(alias="topicId")
    itemId: str = Field(alias="itemId")


@router.get("/me")
async def get_my_progress(
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.get_progress(user_id)


@router.get("/{user_id}")
async def get_progress(user_id: int, service: CourseService = Depends(get_course_service)):
    return await service.get_progress(user_id)


@router.post("")
async def mark_progress(
    body: ProgressMarkIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    await service.mark_progress(user_id, body.topicId, body.itemId)
    return {"ok": True}


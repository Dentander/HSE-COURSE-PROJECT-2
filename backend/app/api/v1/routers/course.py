from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_course_service, get_current_user_id
from app.schemas.course import TopicOut
from app.services.course_service import CourseService

router = APIRouter(prefix="/course", tags=["course"])


@router.get("", response_model=list[TopicOut])
async def get_course(service: CourseService = Depends(get_course_service)):
    return await service.get_course()


@router.get("/me", response_model=list[TopicOut])
async def get_course_me(
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.get_course(user_id=user_id)

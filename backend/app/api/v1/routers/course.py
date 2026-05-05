from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_course_service
from app.schemas.course import TopicOut
from app.services.course_service import CourseService

router = APIRouter(prefix="/course", tags=["course"])


@router.get("", response_model=list[TopicOut])
async def get_course(service: CourseService = Depends(get_course_service)):
    return await service.get_course()

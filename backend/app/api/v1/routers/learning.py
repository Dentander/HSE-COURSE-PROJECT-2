from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import (
    ModuleOut,
    MaterialShortOut,
    MaterialDetailOut,
    AnswerSubmitIn,
    AnswerGroupResultOut,
)
from app.services.learning_service import LearningService
from app.api.v1.dependencies import get_learning_service, get_current_user_id

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/modules", response_model=List[ModuleOut])
async def get_all_modules(
    service: LearningService = Depends(get_learning_service)
):
    return await service.get_all_modules()


@router.get("/modules/{module_id}/materials", response_model=List[MaterialShortOut])
async def get_module_materials(
    module_id: int,
    user_id: Optional[int] = Depends(get_current_user_id),
    service: LearningService = Depends(get_learning_service)
):
    return await service.get_materials_by_module(module_id, user_id)


@router.get("/materials/{material_id}", response_model=MaterialDetailOut)
async def get_material_detail(
    material_id: int,
    user_id: Optional[int] = Depends(get_current_user_id),
    service: LearningService = Depends(get_learning_service)
):
    return await service.get_material_detail(material_id, user_id)


@router.post("/materials/{material_id}/submit", response_model=AnswerGroupResultOut)
async def submit_answer(
    material_id: int,
    data: AnswerSubmitIn,
    user_id: int = Depends(get_current_user_id),
    service: LearningService = Depends(get_learning_service)
):
    return await service.submit_answer(user_id, material_id, data)

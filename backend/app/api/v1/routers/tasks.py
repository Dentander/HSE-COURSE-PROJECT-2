from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.dependencies import get_course_service, get_current_user_id
from app.schemas.tasks import (
    SubmitCodeOrderIn,
    SubmitFillBlankIn,
    SubmitFindBugIn,
    SubmitMatchPairsIn,
    SubmitOut,
    SubmitSingleChoiceIn,
    TaskAttemptOut,
    TaskGetOut,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{item_id}", response_model=TaskGetOut)
async def get_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_task(item_id)

@router.get("/{item_id}/single-choice", response_model=TaskGetOut)
async def get_single_choice_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_single_choice_task(item_id)


@router.get("/{item_id}/fill-in-blank", response_model=TaskGetOut)
async def get_fill_in_blank_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_fill_in_blank_task(item_id)


@router.get("/{item_id}/find-the-bug", response_model=TaskGetOut)
async def get_find_the_bug_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_find_the_bug_task(item_id)


@router.get("/{item_id}/code-order", response_model=TaskGetOut)
async def get_code_order_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_code_order_task(item_id)


@router.get("/{item_id}/match-pairs", response_model=TaskGetOut)
async def get_match_pairs_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_match_pairs_task(item_id)


@router.post("/{item_id}/submit", response_model=SubmitOut)
async def submit_task(
    item_id: str,
    body: dict,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body)

@router.post("/{item_id}/submit/single-choice", response_model=SubmitOut)
async def submit_single_choice(
    item_id: str,
    body: SubmitSingleChoiceIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    task = await service.get_task(item_id)
    if task.taskType != "single-choice":
        raise HTTPException(400, "Task type mismatch")
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body.model_dump(by_alias=True))


@router.post("/{item_id}/submit/fill-in-blank", response_model=SubmitOut)
async def submit_fill_in_blank(
    item_id: str,
    body: SubmitFillBlankIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    task = await service.get_task(item_id)
    if task.taskType != "fill-in-blank":
        raise HTTPException(400, "Task type mismatch")
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body.model_dump())


@router.post("/{item_id}/submit/find-the-bug", response_model=SubmitOut)
async def submit_find_the_bug(
    item_id: str,
    body: SubmitFindBugIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    task = await service.get_task(item_id)
    if task.taskType != "find-the-bug":
        raise HTTPException(400, "Task type mismatch")
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body.model_dump(by_alias=True))


@router.post("/{item_id}/submit/code-order", response_model=SubmitOut)
async def submit_code_order(
    item_id: str,
    body: SubmitCodeOrderIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    task = await service.get_task(item_id)
    if task.taskType != "code-order":
        raise HTTPException(400, "Task type mismatch")
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body.model_dump())


@router.post("/{item_id}/submit/match-pairs", response_model=SubmitOut)
async def submit_match_pairs(
    item_id: str,
    body: SubmitMatchPairsIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    task = await service.get_task(item_id)
    if task.taskType != "match-pairs":
        raise HTTPException(400, "Task type mismatch")
    return await service.submit_task(user_id=user_id, item_id=item_id, answer=body.model_dump())


@router.get("/{item_id}/attempts", response_model=list[TaskAttemptOut])
async def get_attempts(
    item_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.list_attempts(user_id=user_id, item_id=item_id)


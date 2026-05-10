import asyncio

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_course_service, get_current_user_id
from app.schemas.tasks import (
    CodeRunJobStatusOut,
    CodeSubmitAcceptedOut,
    CodeWithTestsResultsOut,
    SubmitCodeOrderIn,
    SubmitCodeWithTestsIn,
    SubmitFillBlankIn,
    SubmitFindBugIn,
    SubmitMatchPairsIn,
    SubmitOut,
    SubmitSingleChoiceIn,
    TaskAttemptOut,
    TaskGetOut,
    TaskMyRewardXpOut,
)
from app.services.code_run_worker import dispatch_code_run_job
from app.services.course_service import CourseService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{item_id}/my-reward-xp", response_model=TaskMyRewardXpOut)
async def get_my_personal_task_reward_xp(
    item_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.get_my_personal_task_reward_xp(user_id, item_id)


@router.get("/{item_id}", response_model=TaskGetOut)
async def get_task(item_id: str, service: CourseService = Depends(get_course_service)):
    return await service.get_task(item_id)


@router.get("/{item_id}/single-choice", response_model=TaskGetOut)
async def get_single_choice_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_single_choice_task(item_id)


@router.get("/{item_id}/fill-in-blank", response_model=TaskGetOut)
async def get_fill_in_blank_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_fill_in_blank_task(item_id)


@router.get("/{item_id}/find-the-bug", response_model=TaskGetOut)
async def get_find_the_bug_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_find_the_bug_task(item_id)


@router.get("/{item_id}/code-order", response_model=TaskGetOut)
async def get_code_order_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_code_order_task(item_id)


@router.get("/{item_id}/match-pairs", response_model=TaskGetOut)
async def get_match_pairs_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_match_pairs_task(item_id)


@router.get("/{item_id}/code-with-tests/results", response_model=CodeWithTestsResultsOut)
async def get_code_with_tests_results(
    item_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.get_code_with_tests_verdict_summary(user_id, item_id)


@router.get("/{item_id}/code-with-tests/status", response_model=CodeRunJobStatusOut)
async def get_code_with_tests_status(
    item_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.get_code_with_tests_status(user_id, item_id)


@router.get("/{item_id}/code-with-tests", response_model=TaskGetOut)
async def get_code_with_tests_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    return await service.get_code_with_tests_task(item_id)


@router.post("/{item_id}/submit/single-choice", response_model=SubmitOut)
async def submit_single_choice(
    item_id: str,
    body: SubmitSingleChoiceIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_single_choice(
        user_id=user_id, item_id=item_id, body=body
    )


@router.post("/{item_id}/submit/fill-in-blank", response_model=SubmitOut)
async def submit_fill_in_blank(
    item_id: str,
    body: SubmitFillBlankIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_fill_in_blank(
        user_id=user_id, item_id=item_id, body=body
    )


@router.post("/{item_id}/submit/find-the-bug", response_model=SubmitOut)
async def submit_find_the_bug(
    item_id: str,
    body: SubmitFindBugIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_find_the_bug(
        user_id=user_id, item_id=item_id, body=body
    )


@router.post("/{item_id}/submit/code-order", response_model=SubmitOut)
async def submit_code_order(
    item_id: str,
    body: SubmitCodeOrderIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_code_order(user_id=user_id, item_id=item_id, body=body)


@router.post("/{item_id}/submit/match-pairs", response_model=SubmitOut)
async def submit_match_pairs(
    item_id: str,
    body: SubmitMatchPairsIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.submit_match_pairs(user_id=user_id, item_id=item_id, body=body)


@router.post("/{item_id}/submit/code-with-tests", response_model=CodeSubmitAcceptedOut)
async def submit_code_with_tests(
    item_id: str,
    body: SubmitCodeWithTestsIn,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    job_id = await service.enqueue_code_with_tests(
        user_id=user_id, item_id=item_id, body=body
    )
    asyncio.create_task(dispatch_code_run_job(job_id))
    return CodeSubmitAcceptedOut()


@router.get("/{item_id}/attempts", response_model=list[TaskAttemptOut])
async def get_attempts(
    item_id: str,
    user_id: int = Depends(get_current_user_id),
    service: CourseService = Depends(get_course_service),
):
    return await service.list_attempts(user_id=user_id, item_id=item_id)

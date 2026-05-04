from typing import Literal
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_course_service
from app.services.course_service import CourseService

router = APIRouter(prefix="/course/admin", tags=["course-admin"])


class TopicCreateIn(BaseModel):
    id: str
    title: str
    order: int


class ItemCreateIn(BaseModel):
    id: str
    topicId: str = Field(alias="topicId")
    type: Literal["lesson", "task"]
    title: str
    order: int


class TheoryBlockCreateIn(BaseModel):
    itemId: str = Field(alias="itemId")
    type: Literal["title", "subtitle", "text", "code", "image"]
    content: str
    order: int
    src: str | None = None
    alt: str | None = None


class TaskBaseIn(BaseModel):
    itemId: str = Field(alias="itemId")
    npcText: str | None = Field(default=None, alias="npcText")
    rewardXp: int | None = Field(default=None, alias="rewardXp")


class TaskSingleChoiceCreateIn(TaskBaseIn):
    question: str
    answers: list[str]
    correctIndex: int = Field(alias="correctIndex")


class TaskFillBlankCreateIn(TaskBaseIn):
    codeTemplate: str = Field(alias="codeTemplate")
    blank: str


class TaskFindBugCreateIn(TaskBaseIn):
    bugLineIndex: int = Field(alias="bugLineIndex")
    explanation: str | None = None
    codeLines: list[str] = Field(alias="codeLines")


class TaskCodeOrderCreateIn(TaskBaseIn):
    description: str | None = None
    codeLines: list[str] = Field(alias="codeLines")
    correctOrder: list[int] | None = Field(default=None, alias="correctOrder")


class TaskMatchPairsCreateIn(TaskBaseIn):
    class PairIn(BaseModel):
        left: str
        right: str
        order: int | None = None

    pairs: list[PairIn]


@router.post("/topics")
async def create_topic(
    body: TopicCreateIn, service: CourseService = Depends(get_course_service)
):
    t = await service.admin_create_topic(body.id, body.title, body.order)
    return {"id": t.id, "title": t.title, "order": t.order}


@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: str, service: CourseService = Depends(get_course_service)
):
    await service.admin_delete_topic(topic_id)
    return {"ok": True}


@router.post("/items")
async def create_item(
    body: ItemCreateIn, service: CourseService = Depends(get_course_service)
):
    it = await service.admin_create_item(
        body.id, body.topicId, body.type, body.title, body.order
    )
    return {
        "id": it.id,
        "topicId": it.topic_id,
        "type": it.type,
        "title": it.title,
        "order": it.order,
    }


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    await service.admin_delete_item(item_id)
    return {"ok": True}


@router.post("/theory-blocks")
async def create_theory_block(
    body: TheoryBlockCreateIn, service: CourseService = Depends(get_course_service)
):
    b = await service.admin_create_theory_block(
        body.itemId, body.type, body.content, body.order, body.src, body.alt
    )
    return {"id": b.id}


@router.delete("/theory-blocks/{block_id}")
async def delete_theory_block(
    block_id: int, service: CourseService = Depends(get_course_service)
):
    await service.admin_delete_theory_block(block_id)
    return {"ok": True}


@router.post("/tasks/single-choice")
async def create_task_single_choice(
    body: TaskSingleChoiceCreateIn,
    service: CourseService = Depends(get_course_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) | {
        "taskType": "single-choice"
    }
    task = await service.admin_create_task(payload)
    return {"id": task.id, "itemId": task.item_id, "taskType": task.task_type}


@router.post("/tasks/fill-in-blank")
async def create_task_fill_blank(
    body: TaskFillBlankCreateIn,
    service: CourseService = Depends(get_course_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) | {
        "taskType": "fill-in-blank"
    }
    task = await service.admin_create_task(payload)
    return {"id": task.id, "itemId": task.item_id, "taskType": task.task_type}


@router.post("/tasks/find-the-bug")
async def create_task_find_bug(
    body: TaskFindBugCreateIn,
    service: CourseService = Depends(get_course_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) | {
        "taskType": "find-the-bug"
    }
    task = await service.admin_create_task(payload)
    return {"id": task.id, "itemId": task.item_id, "taskType": task.task_type}


@router.post("/tasks/code-order")
async def create_task_code_order(
    body: TaskCodeOrderCreateIn,
    service: CourseService = Depends(get_course_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) | {
        "taskType": "code-order"
    }
    task = await service.admin_create_task(payload)
    return {"id": task.id, "itemId": task.item_id, "taskType": task.task_type}


@router.post("/tasks/match-pairs")
async def create_task_match_pairs(
    body: TaskMatchPairsCreateIn,
    service: CourseService = Depends(get_course_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) | {
        "taskType": "match-pairs"
    }
    task = await service.admin_create_task(payload)
    return {"id": task.id, "itemId": task.item_id, "taskType": task.task_type}


@router.delete("/tasks/{item_id}")
async def delete_task(
    item_id: str, service: CourseService = Depends(get_course_service)
):
    await service.admin_delete_task(item_id)
    return {"ok": True}

from importlib import util
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.v1.dependencies import get_course_service, require_course_admin_basic
from app.services.course_service import CourseService

router = APIRouter(
    prefix="/course/admin",
    tags=["course-admin"],
    dependencies=[Depends(require_course_admin_basic)],
)


def _sharpik_course_file() -> Path:
    backend_root = Path(__file__).resolve().parents[4]
    candidates = [
        backend_root / "course_content" / "sharpik_course.py",
        backend_root / "scripts" / "coursecontent" / "sharpik_course.py",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise RuntimeError(
        "sharpik_course.py not found. Expected one of: "
        + ", ".join(str(p) for p in candidates)
    )


def _load_sharpik_course_topics() -> list[dict]:
    path = _sharpik_course_file()
    spec = util.spec_from_file_location("sharpik_course", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load sharpik course from {path}")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.COURSE_SHARPIK)


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


class ReplaceEntireCourseIn(BaseModel):
    topics: list[dict[str, Any]]


@router.post("/replace-entire-course")
async def replace_entire_course(
    body: ReplaceEntireCourseIn,
    service: CourseService = Depends(get_course_service),
):
    n = await service.admin_replace_entire_course(body.topics)
    return {"ok": True, "topicsLoaded": n}


@router.post("/replace-with-sharpik-course")
async def replace_with_sharpik_course(
    service: CourseService = Depends(get_course_service),
):
    topics = _load_sharpik_course_topics()
    n = await service.admin_replace_entire_course(topics)
    return {"ok": True, "topicsLoaded": n, "source": "course_content/sharpik_course.py"}


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

from typing import Literal
from pydantic import BaseModel, Field

TheoryBlockType = Literal["title", "subtitle", "text", "code", "image", "string"]
ItemType = Literal["lesson", "task"]
TaskType = Literal[
    "single-choice", "fill-in-blank", "find-the-bug", "code-order", "match-pairs"
]


class TheoryBlockOut(BaseModel):
    type: TheoryBlockType
    content: str
    src: str | None = None
    alt: str | None = None
    order: int | None = None


class LessonItemOut(BaseModel):
    id: str
    type: Literal["lesson"] = "lesson"
    title: str
    order: int | None = None
    theoryBlocks: list[TheoryBlockOut] = Field(default_factory=list)


class TaskItemOut(BaseModel):
    id: str
    type: Literal["task"] = "task"
    title: str
    order: int | None = None
    taskType: TaskType
    npcText: str = ""
    rewardXp: int = 0
    question: str | None = None
    answers: list[str] | None = None
    codeTemplate: str | None = None
    codeLines: list[str] | None = None
    description: str | None = None
    leftItems: list[str] | None = None
    rightItems: list[str] | None = None


CourseItemOut = LessonItemOut | TaskItemOut


class TopicOut(BaseModel):
    id: str
    title: str
    order: int | None = None
    items: list[CourseItemOut] = Field(default_factory=list)

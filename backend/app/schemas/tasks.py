from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


TaskType = Literal["single-choice", "fill-in-blank", "find-the-bug", "code-order", "match-pairs"]


class TaskGetOut(BaseModel):
    itemId: str
    title: str
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


class SubmitSingleChoiceIn(BaseModel):
    selectedIndex: int = Field(alias="selectedIndex")


class SubmitFillBlankIn(BaseModel):
    text: str


class SubmitFindBugIn(BaseModel):
    bugLineIndex: int = Field(alias="bugLineIndex")


class SubmitCodeOrderIn(BaseModel):
    order: list[int]


class SubmitMatchPairsIn(BaseModel):
    pairs: list[dict[str, str]]


SubmitIn = SubmitSingleChoiceIn | SubmitFillBlankIn | SubmitFindBugIn | SubmitCodeOrderIn | SubmitMatchPairsIn


class SubmitOut(BaseModel):
    isCorrect: bool
    message: str
    rewardXp: int = 0


class TaskAttemptOut(BaseModel):
    id: int
    taskType: TaskType
    answer: dict[str, Any]
    isCorrect: bool
    createdAt: datetime


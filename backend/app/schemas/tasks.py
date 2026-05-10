from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

TaskType = Literal[
    "single-choice",
    "fill-in-blank",
    "find-the-bug",
    "code-order",
    "match-pairs",
    "code-with-tests",
]


class TaskMyRewardXpOut(BaseModel):
    itemId: str
    rewardXp: int


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


class SubmitCodeWithTestsIn(BaseModel):
    code: str


class CodeSubmitAcceptedOut(BaseModel):
    """Решение принято; проверка идёт — смотрите GET …/code-with-tests/status."""

    ok: bool = True


class CodeRunJobStatusOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["idle", "pending", "done"]
    verdict: str | None = None
    detail: str = ""
    isCorrect: bool | None = None
    rewardXp: int | None = None


class CodeWithTestsVerdictSnapshot(BaseModel):
    """Один зафиксированный вердикт проверки кода."""

    model_config = ConfigDict(populate_by_name=True)

    verdict: str | None = None
    detail: str = ""
    isCorrect: bool | None = Field(default=None, alias="isCorrect")
    createdAt: datetime | None = Field(default=None, alias="createdAt")


class CodeWithTestsResultsOut(BaseModel):
    """
    Сводка по заданию «код с тестами»: лучший достигнутый вердикт и последняя попытка.
    Шкала (лучше → хуже): OK → WA → RE → TL → ML → CE.
    """

    model_config = ConfigDict(populate_by_name=True)

    itemId: str
    best: CodeWithTestsVerdictSnapshot | None = None
    last: CodeWithTestsVerdictSnapshot | None = None
    verdictRanking: list[str] = Field(
        default_factory=lambda: ["OK", "WA", "RE", "TL", "ML", "CE"],
        description="Порядок вердиктов от лучшего к худшему",
    )


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

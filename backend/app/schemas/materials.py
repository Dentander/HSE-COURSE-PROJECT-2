from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from .answers import PossibleAnswerOut
from ..models.materials import MaterialType


class MaterialStatus(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    ATTEMPTED_INCORRECT = "attempted_incorrect"
    SOLVED = "solved"


class MaterialShortOut(BaseModel):
    material_id: int
    name: str
    description: Optional[str] = None
    type: MaterialType
    xp_reward: int
    status: MaterialStatus | None = None

    class Config:
        from_attributes = True


class MaterialDetailOut(BaseModel):
    material_id: int
    module_id: int
    name: str
    description: Optional[str] = None
    type: MaterialType
    xp_reward: int
    possible_answers: List[PossibleAnswerOut] = Field(default_factory=list)
    is_solved: bool | None = None

    class Config:
        from_attributes = True

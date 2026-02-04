from pydantic import BaseModel, Field
from typing import List


class PossibleAnswerOut(BaseModel):
    possible_answer_id: int
    text: str

    class Config:
        from_attributes = True


class AnswerSubmitIn(BaseModel):
    selected_answer_ids: List[int] = Field(min_items=1)


class AnswerGroupResultOut(BaseModel):
    answer_group_id: int
    is_correct: bool
    message: str
    xp_earned: int = 0

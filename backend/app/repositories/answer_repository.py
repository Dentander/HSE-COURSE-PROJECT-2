from typing import List

from .base_repository import BaseRepository
from ..models.answer_groups import AnswerGroups
from ..models.user_answer import UserAnswer


class AnswerRepository(BaseRepository):
    async def create_answer_group(self, user_id: int, material_id: int, is_correct: bool) -> AnswerGroups:
        group = AnswerGroups(user_id=user_id, task_id=material_id, is_correct=is_correct)
        self.session.add(group)
        await self.session.flush()
        return group

    async def create_user_answers(self, answer_group_id: int, selected_answers: List[tuple[int, bool]]) -> None:
        for ans_id, is_correct in selected_answers:
            ua = UserAnswer(
                answer_group_id=answer_group_id,
                answer_id=ans_id,
                is_correct=is_correct
            )
            self.session.add(ua)
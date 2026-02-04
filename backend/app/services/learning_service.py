from typing import List, Optional
from fastapi import HTTPException

from ..repositories.module_repository import ModuleRepository
from ..repositories.material_repository import MaterialRepository
from ..repositories.answer_repository import AnswerRepository
from ..repositories.user_repository import UserRepository
from ..schemas import ModuleOut, MaterialShortOut, MaterialDetailOut, AnswerSubmitIn, AnswerGroupResultOut
from ..models.materials import MaterialType


class LearningService:
    def __init__(
        self,
        module_repo: ModuleRepository,
        material_repo: MaterialRepository,
        answer_repo: AnswerRepository,
        user_repo: UserRepository
    ):
        self.module_repo = module_repo
        self.material_repo = material_repo
        self.answer_repo = answer_repo
        self.user_repo = user_repo

    async def get_all_modules(self) -> List[ModuleOut]:
        return await self.module_repo.get_all_modules()

    async def get_materials_by_module(self, module_id: int, user_id: Optional[int] = None) -> List[MaterialShortOut]:
        return await self.material_repo.get_materials_by_module(module_id, user_id)

    async def get_material_detail(self, material_id: int, user_id: Optional[int] = None) -> MaterialDetailOut:
        material = await self.material_repo.get_material_detail(material_id, user_id)
        if not material:
            raise HTTPException(404, "Material not found")
        return material

    async def submit_answer(self, user_id: int, material_id: int, data: AnswerSubmitIn) -> AnswerGroupResultOut:
        material = await self.material_repo.get_material_detail(material_id)
        if not material:
            raise HTTPException(404, "Material not found")
        if material.type == MaterialType.THEORY:
            raise HTTPException(400, "Theory not found")

        possible_answers = await self.material_repo.get_possible_answers(material_id)
        correct_ids = {a.possible_answer_id for a in possible_answers if a.is_correct}
        selected_ids = set(data.selected_answer_ids)

        if not selected_ids.issubset({a.possible_answer_id for a in possible_answers}):
            raise HTTPException(400, "Wrong answer ID's")

        is_multiple = material.type == MaterialType.TEST_WITH_MULTIPLE_CHOICE
        if not is_multiple and len(selected_ids) != 1:
            raise HTTPException(400, "Chose only 1 answer for test with single")

        is_correct = selected_ids == correct_ids

        group = await self.answer_repo.create_answer_group(user_id, material_id, is_correct)

        selected_with_correct = [(ans_id, ans_id in correct_ids) for ans_id in data.selected_answer_ids]
        await self.answer_repo.create_user_answers(group.answer_group_id, selected_with_correct)

        xp_earned = material.xp_reward if is_correct else 0
        if xp_earned > 0:
            await self.user_repo.add_xp(user_id, xp_earned)

        try:
            await self.answer_repo.session.commit()
        except:
            await self.answer_repo.session.rollback()
            raise HTTPException(400, "Saving error")

        return AnswerGroupResultOut(
            answer_group_id=group.answer_group_id,
            is_correct=is_correct,
            message="Ответ принят",
            xp_earned=xp_earned
        )

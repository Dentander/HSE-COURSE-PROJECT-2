from typing import List, Optional
from sqlalchemy import select, exists, func, or_

from .base_repository import BaseRepository
from ..models.materials import Materials, MaterialType
from ..models.possible_answers import PossibleAnswer
from ..models.answer_groups import AnswerGroups
from ..schemas import MaterialShortOut, MaterialDetailOut, PossibleAnswerOut, MaterialStatus


class MaterialRepository(BaseRepository):
    async def get_materials_by_module(self, module_id: int, user_id: Optional[int] = None) -> List[MaterialShortOut]:
        stmt = select(Materials).where(Materials.module_id == module_id).order_by(Materials.created_at.asc())
        result = await self.session.execute(stmt)
        materials = result.scalars().all()

        outputs = []
        for m in materials:
            out = MaterialShortOut.from_orm(m)
            if user_id is not None and m.type != MaterialType.THEORY:
                has_any_attempt = await self._has_any_attempt(user_id, m.material_id)
                has_successful = await self._is_solved(user_id, m.material_id)

                if has_successful:
                    out.status = MaterialStatus.SOLVED
                elif has_any_attempt:
                    out.status = MaterialStatus.ATTEMPTED_INCORRECT
                else:
                    out.status = MaterialStatus.NOT_ATTEMPTED
            outputs.append(out)
        return outputs

    async def _has_any_attempt(self, user_id: int, material_id: int) -> bool:
        stmt = select(exists().where(
            AnswerGroups.user_id == user_id,
            AnswerGroups.task_id == material_id
        ))
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def _is_solved(self, user_id: int, material_id: int) -> bool:
        stmt = select(exists().where(
            AnswerGroups.user_id == user_id,
            AnswerGroups.task_id == material_id,
            AnswerGroups.is_correct == True
        ))
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def get_material_detail(self, material_id: int, user_id: Optional[int] = None) -> Optional[MaterialDetailOut]:
        stmt = select(Materials).where(Materials.material_id == material_id)
        result = await self.session.execute(stmt)
        material = result.scalar_one_or_none()
        if not material:
            return None

        out = MaterialDetailOut.from_orm(material)
        if material.type != MaterialType.THEORY:
            ans_stmt = select(PossibleAnswer).where(PossibleAnswer.task_id == material_id)
            ans_result = await self.session.execute(ans_stmt)
            answers = ans_result.scalars().all()
            out.possible_answers = [PossibleAnswerOut.from_orm(a) for a in answers]

        if user_id is not None:
            out.is_solved = await self._is_solved(user_id, material_id)

        return out

    async def get_possible_answers(self, material_id: int) -> List[PossibleAnswer]:
        stmt = select(PossibleAnswer).where(PossibleAnswer.task_id == material_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

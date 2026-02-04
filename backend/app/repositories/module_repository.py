from typing import List
from sqlalchemy import select

from .base_repository import BaseRepository
from ..models.modules import Modules
from ..schemas import ModuleOut


class ModuleRepository(BaseRepository):
    async def get_all_modules(self) -> List[ModuleOut]:
        stmt = select(Modules).order_by(Modules.priority.asc(), Modules.created_at.asc())
        result = await self.session.execute(stmt)
        modules = result.scalars().all()
        return [ModuleOut.from_orm(m) for m in modules]
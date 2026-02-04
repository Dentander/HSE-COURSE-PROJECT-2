from pydantic import BaseModel
from typing import Optional


class ModuleOut(BaseModel):
    module_id: int
    title: str
    description: Optional[str] = None
    priority: int

    class Config:
        from_attributes = True

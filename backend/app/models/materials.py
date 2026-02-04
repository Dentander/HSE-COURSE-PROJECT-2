from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class MaterialType(str, enum.Enum):
    THEORY = "theory"
    TEST_WITH_MULTIPLE_CHOICE = "test_with_multiple_choice"
    TEST_WITH_SINGLE_CHOICE = "test_with_single_choice"


class Materials(Base):
    __tablename__ = "materials"

    material_id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.module_id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum(MaterialType), nullable=False)
    priority = Column(Integer, default=100, nullable=False)
    xp_reward = Column(Integer, default=10, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

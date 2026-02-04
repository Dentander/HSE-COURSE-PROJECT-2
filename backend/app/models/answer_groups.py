from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func

from app.db.base import Base


class AnswerGroups(Base):
    __tablename__ = "answer_groups"

    answer_group_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    task_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

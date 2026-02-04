from sqlalchemy import Column, Integer, Boolean, ForeignKey, String

from app.db.base import Base


class PossibleAnswer(Base):
    __tablename__ = "possible_answers"

    possible_answer_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("materials.material_id"), nullable=False)
    text = Column(String, nullable=False)

    is_correct = Column(Boolean, default=False)

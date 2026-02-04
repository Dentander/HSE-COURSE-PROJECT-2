from sqlalchemy import Column, Integer, Boolean, ForeignKey

from app.db.base import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    user_answer_id = Column(Integer, primary_key=True)
    answer_group_id = Column(
        Integer,
        ForeignKey("answer_groups.answer_group_id"),
        nullable=False
    )
    answer_id = Column(
        Integer,
        ForeignKey("possible_answers.possible_answer_id"),
        nullable=False
    )

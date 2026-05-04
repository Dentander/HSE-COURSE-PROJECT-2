from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ItemType(str, Enum):
    LESSON = "lesson"
    TASK = "task"


class TaskType(str, Enum):
    SINGLE_CHOICE = "single-choice"
    FILL_IN_BLANK = "fill-in-blank"
    FIND_THE_BUG = "find-the-bug"
    CODE_ORDER = "code-order"
    MATCH_PAIRS = "match-pairs"


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Item.order",
    )


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("topic_id", "order", name="uq_items_topic_order"),
    )
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    topic_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    topic: Mapped[Topic] = relationship("Topic", back_populates="items")
    theory_blocks: Mapped[list["TheoryBlock"]] = relationship(
        "TheoryBlock",
        back_populates="item",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TheoryBlock.order",
    )
    task: Mapped[Optional["Task"]] = relationship(
        "Task",
        back_populates="item",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )


class TheoryBlock(Base):
    __tablename__ = "theory_blocks"
    __table_args__ = (
        UniqueConstraint("item_id", "order", name="uq_theory_blocks_item_order"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    src: Mapped[str | None] = mapped_column(Text, nullable=True)
    alt: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    item: Mapped[Item] = relationship("Item", back_populates="theory_blocks")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    npc_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reward_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    item: Mapped[Item] = relationship("Item", back_populates="task")
    single_choice: Mapped[Optional["TaskSingleChoice"]] = relationship(
        "TaskSingleChoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    fill_blank: Mapped[Optional["TaskFillBlank"]] = relationship(
        "TaskFillBlank",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    find_bug: Mapped[Optional["TaskFindBug"]] = relationship(
        "TaskFindBug",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    code_order: Mapped[Optional["TaskCodeOrder"]] = relationship(
        "TaskCodeOrder",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    answers: Mapped[list["TaskAnswer"]] = relationship(
        "TaskAnswer",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TaskAnswer.order",
    )
    code_lines: Mapped[list["TaskCodeLine"]] = relationship(
        "TaskCodeLine",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TaskCodeLine.order",
    )
    pairs: Mapped[list["TaskPair"]] = relationship(
        "TaskPair",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TaskPair.order",
    )


class TaskSingleChoice(Base):
    __tablename__ = "task_single_choice"
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)


class TaskAnswer(Base):
    __tablename__ = "task_answers"
    __table_args__ = (
        UniqueConstraint("task_id", "order", name="uq_task_answers_task_order"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class TaskFillBlank(Base):
    __tablename__ = "task_fill_blank"
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    code_template: Mapped[str] = mapped_column(Text, nullable=False)
    blank: Mapped[str] = mapped_column(Text, nullable=False)


class TaskFindBug(Base):
    __tablename__ = "task_find_bug"
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bug_line_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")


class TaskCodeLine(Base):
    __tablename__ = "task_code_lines"
    __table_args__ = (
        UniqueConstraint("task_id", "order", name="uq_task_code_lines_task_order"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class TaskCodeOrder(Base):
    __tablename__ = "task_code_order"
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    correct_order: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class TaskPair(Base):
    __tablename__ = "task_pairs"
    __table_args__ = (
        UniqueConstraint("task_id", "order", name="uq_task_pairs_task_order"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    left: Mapped[str] = mapped_column(Text, nullable=False)
    right: Mapped[str] = mapped_column(Text, nullable=False)


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_progress_user_item"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class TaskAttempt(Base):
    __tablename__ = "task_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    answer_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

import datetime as dt
import json
from collections import defaultdict
from sqlalchemy import Date, cast, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.course import (
    Item,
    Task,
    TaskAnswer,
    TaskCodeLine,
    TaskCodeOrder,
    TaskAttempt,
    TaskFillBlank,
    TaskFindBug,
    TaskPair,
    TaskSingleChoice,
    TheoryBlock,
    Topic,
    UserProgress,
)


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_topics(self) -> list[Topic]:
        result = await self.session.execute(select(Topic).order_by(Topic.order))
        return list(result.scalars().all())

    async def list_items_for_topics(self, topic_ids: list[str]) -> list[Item]:
        if not topic_ids:
            return []
        result = await self.session.execute(
            select(Item)
            .where(Item.topic_id.in_(topic_ids))
            .order_by(Item.topic_id, Item.order)
        )
        return list(result.scalars().all())

    async def list_theory_blocks_for_items(
        self, item_ids: list[str]
    ) -> list[TheoryBlock]:
        if not item_ids:
            return []
        result = await self.session.execute(
            select(TheoryBlock)
            .where(TheoryBlock.item_id.in_(item_ids))
            .order_by(TheoryBlock.item_id, TheoryBlock.order)
        )
        return list(result.scalars().all())

    async def list_tasks_for_items(self, item_ids: list[str]) -> list[Task]:
        if not item_ids:
            return []
        result = await self.session.execute(
            select(Task).where(Task.item_id.in_(item_ids))
        )
        return list(result.scalars().all())

    async def list_task_single_choice(
        self, task_ids: list[int]
    ) -> list[TaskSingleChoice]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskSingleChoice).where(TaskSingleChoice.task_id.in_(task_ids))
        )
        return list(result.scalars().all())

    async def list_task_fill_blank(self, task_ids: list[int]) -> list[TaskFillBlank]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskFillBlank).where(TaskFillBlank.task_id.in_(task_ids))
        )
        return list(result.scalars().all())

    async def list_task_find_bug(self, task_ids: list[int]) -> list[TaskFindBug]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskFindBug).where(TaskFindBug.task_id.in_(task_ids))
        )
        return list(result.scalars().all())

    async def list_task_code_order(self, task_ids: list[int]) -> list[TaskCodeOrder]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskCodeOrder).where(TaskCodeOrder.task_id.in_(task_ids))
        )
        return list(result.scalars().all())

    async def list_task_answers(self, task_ids: list[int]) -> list[TaskAnswer]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskAnswer)
            .where(TaskAnswer.task_id.in_(task_ids))
            .order_by(TaskAnswer.task_id, TaskAnswer.order)
        )
        return list(result.scalars().all())

    async def list_task_code_lines(self, task_ids: list[int]) -> list[TaskCodeLine]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskCodeLine)
            .where(TaskCodeLine.task_id.in_(task_ids))
            .order_by(TaskCodeLine.task_id, TaskCodeLine.order)
        )
        return list(result.scalars().all())

    async def list_task_pairs(self, task_ids: list[int]) -> list[TaskPair]:
        if not task_ids:
            return []
        result = await self.session.execute(
            select(TaskPair)
            .where(TaskPair.task_id.in_(task_ids))
            .order_by(TaskPair.task_id, TaskPair.order)
        )
        return list(result.scalars().all())

    async def get_task_by_item_id(self, item_id: str) -> Task | None:
        result = await self.session.execute(select(Task).where(Task.item_id == item_id))
        return result.scalar_one_or_none()

    async def dates_with_correct_task_attempts(self, user_id: int) -> set[dt.date]:
        stmt = (
            select(cast(TaskAttempt.created_at, Date))
            .where(TaskAttempt.user_id == user_id, TaskAttempt.is_correct.is_(True))
            .distinct()
        )
        result = await self.session.execute(stmt)
        out: set[dt.date] = set()
        for (d,) in result.all():
            if d is None:
                continue
            if isinstance(d, dt.datetime):
                out.add(d.date())
            elif isinstance(d, dt.date):
                out.add(d)
            else:
                out.add(dt.date.fromisoformat(str(d).partition(" ")[0][:10]))
        return out

    async def create_task_attempt(
        self,
        user_id: int,
        item_id: str,
        task_type: str,
        answer_json: str,
        is_correct: bool,
    ) -> TaskAttempt:
        a = TaskAttempt(
            user_id=user_id,
            item_id=item_id,
            task_type=task_type,
            answer_json=answer_json,
            is_correct=is_correct,
        )
        self.session.add(a)
        await self.session.commit()
        return a

    async def list_task_attempts(self, user_id: int, item_id: str) -> list[TaskAttempt]:
        result = await self.session.execute(
            select(TaskAttempt)
            .where(TaskAttempt.user_id == user_id, TaskAttempt.item_id == item_id)
            .order_by(TaskAttempt.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_incorrect_attempts(self, user_id: int, item_id: str) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(TaskAttempt)
            .where(
                TaskAttempt.user_id == user_id,
                TaskAttempt.item_id == item_id,
                TaskAttempt.is_correct.is_(False),
            )
        )
        return int(result.scalar_one() or 0)

    async def get_progress_map(self, user_id: int) -> dict[str, list[str]]:
        result = await self.session.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        rows = list(result.scalars().all())
        m: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            m[r.topic_id].append(r.item_id)
        return dict(m)

    async def get_item(self, item_id: str) -> Item | None:
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()

    async def list_items_course_order(self) -> list[tuple[str, str, str]]:
        stmt = (
            select(Item.id, Item.topic_id, Item.type)
            .join(Topic, Topic.id == Item.topic_id)
            .order_by(Topic.order.asc(), Item.order.asc())
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def mark_completed(self, user_id: int, topic_id: str, item_id: str) -> bool:
        self.session.add(
            UserProgress(user_id=user_id, topic_id=topic_id, item_id=item_id)
        )
        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def create_topic(self, topic_id: str, title: str, order: int) -> Topic:
        t = Topic(id=topic_id, title=title, order=order)
        self.session.add(t)
        await self.session.commit()
        return t

    async def delete_topic(self, topic_id: str) -> None:
        await self.session.execute(delete(Topic).where(Topic.id == topic_id))
        await self.session.commit()

    async def delete_all_topics(self) -> None:
        await self.session.execute(delete(Topic))
        await self.session.commit()

    async def create_item(
        self, item_id: str, topic_id: str, type_: str, title: str, order: int
    ) -> Item:
        it = Item(id=item_id, topic_id=topic_id, type=type_, title=title, order=order)
        self.session.add(it)
        await self.session.commit()
        return it

    async def delete_item(self, item_id: str) -> None:
        await self.session.execute(delete(Item).where(Item.id == item_id))
        await self.session.commit()

    async def create_theory_block(
        self,
        item_id: str,
        type_: str,
        content: str,
        order: int,
        src: str | None = None,
        alt: str | None = None,
    ) -> TheoryBlock:
        b = TheoryBlock(
            item_id=item_id, type=type_, content=content, src=src, alt=alt, order=order
        )
        self.session.add(b)
        await self.session.commit()
        return b

    async def delete_theory_block(self, block_id: int) -> None:
        await self.session.execute(
            delete(TheoryBlock).where(TheoryBlock.id == block_id)
        )
        await self.session.commit()

    async def create_task(self, payload: dict) -> Task:
        task = Task(
            item_id=payload["itemId"],
            task_type=payload["taskType"],
            npc_text=payload.get("npcText") or "",
            reward_xp=int(payload.get("rewardXp") or 0),
        )
        self.session.add(task)
        await self.session.flush()
        ttype = task.task_type
        if ttype == "single-choice":
            self.session.add(
                TaskSingleChoice(
                    task_id=task.id,
                    question=payload["question"],
                    correct_index=int(payload["correctIndex"]),
                )
            )
            for idx, text in enumerate(payload.get("answers") or []):
                self.session.add(TaskAnswer(task_id=task.id, order=idx, text=str(text)))
        elif ttype == "fill-in-blank":
            self.session.add(
                TaskFillBlank(
                    task_id=task.id,
                    code_template=payload["codeTemplate"],
                    blank=payload["blank"],
                )
            )
        elif ttype == "find-the-bug":
            self.session.add(
                TaskFindBug(
                    task_id=task.id,
                    bug_line_index=int(payload["bugLineIndex"]),
                    explanation=payload.get("explanation") or "",
                )
            )
            for idx, text in enumerate(payload.get("codeLines") or []):
                self.session.add(
                    TaskCodeLine(task_id=task.id, order=idx, text=str(text))
                )
        elif ttype == "code-order":
            correct = payload.get("correctOrder")
            if correct is None:
                correct = list(range(len(payload.get("codeLines") or [])))
            self.session.add(
                TaskCodeOrder(
                    task_id=task.id,
                    description=payload.get("description") or "",
                    correct_order=json.dumps(correct),
                )
            )
            for idx, text in enumerate(payload.get("codeLines") or []):
                self.session.add(
                    TaskCodeLine(task_id=task.id, order=idx, text=str(text))
                )
        elif ttype == "match-pairs":
            for idx, pair in enumerate(payload.get("pairs") or []):
                self.session.add(
                    TaskPair(
                        task_id=task.id,
                        order=int(pair.get("order", idx)),
                        left=str(pair["left"]),
                        right=str(pair["right"]),
                    )
                )
        await self.session.commit()
        return task

    async def delete_task_by_item(self, item_id: str) -> None:
        await self.session.execute(delete(Task).where(Task.item_id == item_id))
        await self.session.commit()

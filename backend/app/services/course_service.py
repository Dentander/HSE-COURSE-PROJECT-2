from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.course import ItemType, TaskType
from app.repositories.course_repository import CourseRepository
from app.schemas.course import LessonItemOut, TaskItemOut, TheoryBlockOut, TopicOut
from app.schemas.tasks import SubmitOut, TaskAttemptOut, TaskGetOut


class CourseService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo

    async def _load_task_details(self, task_ids: list[int]) -> dict[str, dict]:
        single_choice = await self.repo.list_task_single_choice(task_ids)
        fill_blank = await self.repo.list_task_fill_blank(task_ids)
        find_bug = await self.repo.list_task_find_bug(task_ids)
        code_order = await self.repo.list_task_code_order(task_ids)
        answers = await self.repo.list_task_answers(task_ids)
        code_lines = await self.repo.list_task_code_lines(task_ids)
        pairs = await self.repo.list_task_pairs(task_ids)

        details = {
            "single_choice": {r.task_id: r for r in single_choice},
            "fill_blank": {r.task_id: r for r in fill_blank},
            "find_bug": {r.task_id: r for r in find_bug},
            "code_order": {r.task_id: r for r in code_order},
            "answers": defaultdict(list),
            "code_lines": defaultdict(list),
            "pairs": defaultdict(list),
        }
        for a in answers:
            details["answers"][a.task_id].append(a.text)
        for l in code_lines:
            details["code_lines"][l.task_id].append(l.text)
        for p in pairs:
            details["pairs"][p.task_id].append({"left": p.left, "right": p.right, "order": p.order})
        return details

    def _build_task_out(self, item, task, details: dict) -> TaskItemOut:
        out = TaskItemOut(
            id=item.id,
            title=item.title,
            order=item.order,
            taskType=task.task_type,
            npcText=task.npc_text or "",
            rewardXp=task.reward_xp or 0,
        )
        task_id = task.id
        sc = details["single_choice"].get(task_id)
        fb = details["fill_blank"].get(task_id)
        bug = details["find_bug"].get(task_id)
        co = details["code_order"].get(task_id)

        if task.task_type == TaskType.SINGLE_CHOICE.value and sc:
            out.question = sc.question
            out.answers = details["answers"].get(task_id, [])
        elif task.task_type == TaskType.FILL_IN_BLANK.value and fb:
            out.codeTemplate = fb.code_template
        elif task.task_type == TaskType.FIND_THE_BUG.value and bug:
            out.codeLines = details["code_lines"].get(task_id, [])
        elif task.task_type == TaskType.CODE_ORDER.value and co:
            out.description = co.description
            out.codeLines = details["code_lines"].get(task_id, [])
        elif task.task_type == TaskType.MATCH_PAIRS.value:
            pairs_for_task = details["pairs"].get(task_id, [])
            out.leftItems = [p["left"] for p in pairs_for_task]
            out.rightItems = [p["right"] for p in pairs_for_task]
        return out

    async def _get_task_item_out(self, item_id: str) -> TaskItemOut:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        if item.type != ItemType.TASK.value:
            raise HTTPException(400, "Item is not a task")
        task = await self.repo.get_task_by_item_id(item_id)
        if not task:
            raise HTTPException(404, "Task not found")
        details = await self._load_task_details([task.id])
        return self._build_task_out(item, task, details)

    async def get_course(self) -> list[TopicOut]:
        topics = await self.repo.list_topics()
        topic_ids = [t.id for t in topics]
        items = await self.repo.list_items_for_topics(topic_ids)
        item_ids = [i.id for i in items]

        theory_blocks = await self.repo.list_theory_blocks_for_items(item_ids)
        tasks = await self.repo.list_tasks_for_items(item_ids)
        task_by_item = {t.item_id: t for t in tasks}
        task_ids = [t.id for t in tasks]
        task_details = await self._load_task_details(task_ids)

        theory_by_item: dict[str, list[TheoryBlockOut]] = defaultdict(list)
        allowed_block_types = {"title", "subtitle", "text", "code", "image"}
        for b in theory_blocks:
            raw_type = str(b.type or "").strip().lower()
            block_type = {"string": "text"}.get(raw_type, raw_type)
            if block_type not in allowed_block_types:
                block_type = "text"
            theory_by_item[b.item_id].append(
                TheoryBlockOut(
                    type=block_type,
                    content=b.content,
                    src=b.src,
                    alt=b.alt,
                    order=b.order,
                )
            )

        items_by_topic: dict[str, list] = defaultdict(list)
        for it in items:
            if it.type == ItemType.LESSON.value:
                items_by_topic[it.topic_id].append(
                    LessonItemOut(
                        id=it.id,
                        title=it.title,
                        order=it.order,
                        theoryBlocks=theory_by_item.get(it.id, []),
                    )
                )
                continue

            if it.type != ItemType.TASK.value:
                continue

            task = task_by_item.get(it.id)
            if not task:
                raise HTTPException(500, f"Task item '{it.id}' has no tasks row")
            items_by_topic[it.topic_id].append(self._build_task_out(it, task, task_details))

        result: list[TopicOut] = []
        for t in topics:
            result.append(
                TopicOut(
                    id=t.id,
                    title=t.title,
                    order=t.order,
                    items=items_by_topic.get(t.id, []),
                )
            )
        return result

    async def get_progress(self, user_id: int) -> dict[str, list[str]]:
        return await self.repo.get_progress_map(user_id)

    async def assert_task_unlocked(self, user_id: int, item_id: str) -> None:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.type != ItemType.TASK.value:
            return

        ordered_task_ids = await self.repo.list_task_item_ids_in_order()
        if item_id not in ordered_task_ids:
            return

        idx = ordered_task_ids.index(item_id)
        progress = await self.repo.get_progress_map(user_id)
        completed = {it for items in progress.values() for it in items}
        missing_prev = [tid for tid in ordered_task_ids[:idx] if tid not in completed]
        if missing_prev:
            raise HTTPException(
                status_code=403,
                detail="This task is locked. Complete previous tasks first.",
            )

    async def mark_progress(self, user_id: int, topic_id: str, item_id: str) -> None:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        if item.type == ItemType.TASK.value:
            await self.assert_task_unlocked(user_id, item_id)

        await self.repo.mark_completed(user_id, topic_id, item_id)

    async def get_task(self, item_id: str) -> TaskGetOut:
        task_out = await self._get_task_item_out(item_id)
        return TaskGetOut(
            itemId=task_out.id,
            title=task_out.title,
            taskType=task_out.taskType,
            npcText=task_out.npcText,
            rewardXp=task_out.rewardXp,
            question=task_out.question,
            answers=task_out.answers,
            codeTemplate=task_out.codeTemplate,
            codeLines=task_out.codeLines,
            description=task_out.description,
            leftItems=task_out.leftItems,
            rightItems=task_out.rightItems,
        )

    async def get_single_choice_task(self, item_id: str) -> TaskGetOut:
        out = await self.get_task(item_id)
        if out.taskType != TaskType.SINGLE_CHOICE.value:
            raise HTTPException(400, "Task type mismatch")
        return out

    async def get_fill_in_blank_task(self, item_id: str) -> TaskGetOut:
        out = await self.get_task(item_id)
        if out.taskType != TaskType.FILL_IN_BLANK.value:
            raise HTTPException(400, "Task type mismatch")
        return out

    async def get_find_the_bug_task(self, item_id: str) -> TaskGetOut:
        out = await self.get_task(item_id)
        if out.taskType != TaskType.FIND_THE_BUG.value:
            raise HTTPException(400, "Task type mismatch")
        return out

    async def get_code_order_task(self, item_id: str) -> TaskGetOut:
        out = await self.get_task(item_id)
        if out.taskType != TaskType.CODE_ORDER.value:
            raise HTTPException(400, "Task type mismatch")
        return out

    async def get_match_pairs_task(self, item_id: str) -> TaskGetOut:
        out = await self.get_task(item_id)
        if out.taskType != TaskType.MATCH_PAIRS.value:
            raise HTTPException(400, "Task type mismatch")
        return out

    async def submit_task(self, user_id: int, item_id: str, answer: dict[str, Any]) -> SubmitOut:
        await self.assert_task_unlocked(user_id, item_id)

        item = await self.repo.get_item(item_id)
        if not item or item.type != ItemType.TASK.value:
            raise HTTPException(404, "Task item not found")

        task = await self.repo.get_task_by_item_id(item_id)
        if not task:
            raise HTTPException(404, "Task not found")

        task_ids = [task.id]
        sc = {r.task_id: r for r in await self.repo.list_task_single_choice(task_ids)}.get(task.id)
        fb = {r.task_id: r for r in await self.repo.list_task_fill_blank(task_ids)}.get(task.id)
        bug = {r.task_id: r for r in await self.repo.list_task_find_bug(task_ids)}.get(task.id)
        co = {r.task_id: r for r in await self.repo.list_task_code_order(task_ids)}.get(task.id)
        answers_rows = await self.repo.list_task_answers(task_ids)
        code_lines_rows = await self.repo.list_task_code_lines(task_ids)
        pairs_rows = await self.repo.list_task_pairs(task_ids)

        pairs_list = [{"left": p.left, "right": p.right} for p in pairs_rows]

        is_correct = False
        if task.task_type == TaskType.SINGLE_CHOICE.value:
            if not sc:
                raise HTTPException(500, "Task data missing")
            is_correct = int(answer.get("selectedIndex")) == int(sc.correct_index)
        elif task.task_type == TaskType.FILL_IN_BLANK.value:
            if not fb:
                raise HTTPException(500, "Task data missing")
            is_correct = str(answer.get("text", "")).strip() == str(fb.blank).strip()
        elif task.task_type == TaskType.FIND_THE_BUG.value:
            if not bug:
                raise HTTPException(500, "Task data missing")
            is_correct = int(answer.get("bugLineIndex")) == int(bug.bug_line_index)
        elif task.task_type == TaskType.CODE_ORDER.value:
            if not co:
                raise HTTPException(500, "Task data missing")
            try:
                correct_order = json.loads(co.correct_order or "[]")
            except Exception:
                correct_order = []
            is_correct = answer.get("order") == correct_order
        elif task.task_type == TaskType.MATCH_PAIRS.value:
            submitted = {(p.get("left"), p.get("right")) for p in (answer.get("pairs") or [])}
            expected = {(p["left"], p["right"]) for p in pairs_list}
            is_correct = submitted == expected

        attempt = await self.repo.create_task_attempt(
            user_id=user_id,
            item_id=item_id,
            task_type=task.task_type,
            answer_json=json.dumps(answer, ensure_ascii=False),
            is_correct=is_correct,
        )

        if is_correct:
            await self.repo.mark_completed(user_id, item.topic_id, item_id)
            return SubmitOut(isCorrect=True, message="Correct", rewardXp=task.reward_xp or 0)
        return SubmitOut(isCorrect=False, message="Incorrect", rewardXp=0)

    async def list_attempts(self, user_id: int, item_id: str) -> list[TaskAttemptOut]:
        rows = await self.repo.list_task_attempts(user_id, item_id)
        out: list[TaskAttemptOut] = []
        for r in rows:
            try:
                answer = json.loads(r.answer_json)
            except Exception:
                answer = {}
            out.append(
                TaskAttemptOut(
                    id=r.id,
                    taskType=r.task_type,
                    answer=answer,
                    isCorrect=r.is_correct,
                    createdAt=r.created_at,
                )
            )
        return out

    async def admin_create_topic(self, topic_id: str, title: str, order: int):
        return await self.repo.create_topic(topic_id, title, order)

    async def admin_delete_topic(self, topic_id: str):
        await self.repo.delete_topic(topic_id)

    async def admin_create_item(self, item_id: str, topic_id: str, type_: str, title: str, order: int):
        return await self.repo.create_item(item_id, topic_id, type_, title, order)

    async def admin_delete_item(self, item_id: str):
        await self.repo.delete_item(item_id)

    async def admin_create_theory_block(self, item_id: str, type_: str, content: str, order: int, src: str | None, alt: str | None):
        return await self.repo.create_theory_block(item_id=item_id, type_=type_, content=content, order=order, src=src, alt=alt)

    async def admin_delete_theory_block(self, block_id: int):
        await self.repo.delete_theory_block(block_id)

    async def admin_create_task(self, payload: dict):
        return await self.repo.create_task(payload)

    async def admin_delete_task(self, item_id: str):
        await self.repo.delete_task_by_item(item_id)


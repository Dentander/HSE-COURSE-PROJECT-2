import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any
from fastapi import HTTPException
from app.core.config import Settings, get_settings
from app.models.course import Item, ItemType, Task, TaskType
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.schemas.course import LessonItemOut, TaskItemOut, TheoryBlockOut, TopicOut
from app.schemas.progress import DailyCorrectTaskStreakOut, MyTasksProgressOut, TopicTasksProgressOut
from app.schemas.tasks import (
    SubmitCodeOrderIn,
    SubmitFillBlankIn,
    SubmitFindBugIn,
    SubmitMatchPairsIn,
    SubmitOut,
    SubmitSingleChoiceIn,
    TaskAttemptOut,
    TaskGetOut,
    TaskMyRewardXpOut,
)


def _compute_consecutive_days_with_correct_task(
    active_days: set[date], *, today_utc: date
) -> int:
    if not active_days:
        return 0
    anchor = today_utc
    if anchor not in active_days:
        anchor = today_utc - timedelta(days=1)
        if anchor not in active_days:
            return 0
    streak = 0
    d = anchor
    while d in active_days:
        streak += 1
        d -= timedelta(days=1)
    return streak


class CourseService:
    def __init__(
        self,
        repo: CourseRepository,
        user_repo: UserRepository | None = None,
        settings: Settings | None = None,
    ):
        self.repo = repo
        self.user_repo = user_repo
        self.settings = settings or get_settings()

    def _effective_task_reward_xp(
        self, base_xp: int, incorrect_attempts: int
    ) -> int:
        base = max(0, int(base_xp))
        wrong = max(0, int(incorrect_attempts))
        raw = base - wrong * self.settings.task_reward_xp_penalty_per_wrong_attempt
        merged = max(self.settings.task_reward_xp_floor, raw)
        return max(0, min(base, merged))

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
        for line_row in code_lines:
            details["code_lines"][line_row.task_id].append(line_row.text)
        for p in pairs:
            details["pairs"][p.task_id].append(
                {"left": p.left, "right": p.right, "order": p.order}
            )
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

    async def get_my_personal_task_reward_xp(
        self, user_id: int, item_id: str
    ) -> TaskMyRewardXpOut:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        if item.type != ItemType.TASK.value:
            raise HTTPException(400, "Item is not a task")
        task = await self.repo.get_task_by_item_id(item_id)
        if not task:
            raise HTTPException(404, "Task not found")
        incorrect = await self.repo.count_incorrect_attempts(user_id, item_id)
        xp = self._effective_task_reward_xp(task.reward_xp or 0, incorrect)
        return TaskMyRewardXpOut(itemId=item.id, rewardXp=xp)

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
            items_by_topic[it.topic_id].append(
                self._build_task_out(it, task, task_details)
            )
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

    async def get_my_tasks_progress_summary(self, user_id: int) -> MyTasksProgressOut:
        topics = await self.repo.list_topics()
        if not topics:
            return MyTasksProgressOut(
                topics=[], completedTasksTotal=0, totalTasksTotal=0
            )
        topic_ids = [t.id for t in topics]
        items = await self.repo.list_items_for_topics(topic_ids)
        progress_map = await self.repo.get_progress_map(user_id)
        completed_item_ids = {iid for ids in progress_map.values() for iid in ids}
        task_items_by_topic: dict[str, list[Item]] = defaultdict(list)
        for it in items:
            if it.type == ItemType.TASK.value:
                task_items_by_topic[it.topic_id].append(it)
        rows: list[TopicTasksProgressOut] = []
        completed_total = 0
        total_all = 0
        for t in topics:
            task_items = task_items_by_topic.get(t.id, [])
            n_tasks = len(task_items)
            n_done = sum(1 for it in task_items if it.id in completed_item_ids)
            rows.append(
                TopicTasksProgressOut(
                    topicId=t.id,
                    topicTitle=t.title,
                    topicOrder=t.order,
                    completedTasks=n_done,
                    totalTasks=n_tasks,
                )
            )
            total_all += n_tasks
            completed_total += n_done
        return MyTasksProgressOut(
            topics=rows,
            completedTasksTotal=completed_total,
            totalTasksTotal=total_all,
        )

    async def get_daily_correct_task_streak(
        self, user_id: int
    ) -> DailyCorrectTaskStreakOut:
        days = await self.repo.dates_with_correct_task_attempts(user_id)
        today_utc = datetime.now(timezone.utc).date()
        n = _compute_consecutive_days_with_correct_task(days, today_utc=today_utc)
        return DailyCorrectTaskStreakOut(consecutive_days=n)

    async def assert_task_unlocked(self, user_id: int, item_id: str) -> None:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.type != ItemType.TASK.value:
            return
        ordered = await self.repo.list_items_course_order()
        idx = next((i for i, row in enumerate(ordered) if row[0] == item_id), None)
        if idx is None:
            return
        progress = await self.repo.get_progress_map(user_id)
        completed = {it for items in progress.values() for it in items}
        missing_prev: list[str] = []
        for prev_id, prev_topic_id, prev_type in ordered[:idx]:
            if prev_type == ItemType.TASK.value and prev_topic_id == item.topic_id:
                continue
            if prev_id not in completed:
                missing_prev.append(prev_id)
        if missing_prev:
            raise HTTPException(
                status_code=403,
                detail="This task is locked. Complete earlier course items first.",
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

    async def _task_item_and_task(self, item_id: str) -> tuple[Item, Task]:
        item = await self.repo.get_item(item_id)
        if not item or item.type != ItemType.TASK.value:
            raise HTTPException(404, "Task item not found")
        task = await self.repo.get_task_by_item_id(item_id)
        if not task:
            raise HTTPException(404, "Task not found")
        return item, task

    async def _persist_task_attempt(
        self,
        user_id: int,
        item: Item,
        task: Task,
        answer: dict[str, Any],
        is_correct: bool,
    ) -> SubmitOut:
        base_xp = task.reward_xp or 0
        incorrect_before = 0
        if is_correct:
            incorrect_before = await self.repo.count_incorrect_attempts(
                user_id, item.id
            )
        reward_on_success = self._effective_task_reward_xp(
            base_xp, incorrect_before
        )
        await self.repo.create_task_attempt(
            user_id=user_id,
            item_id=item.id,
            task_type=task.task_type,
            answer_json=json.dumps(answer, ensure_ascii=False),
            is_correct=is_correct,
        )
        if is_correct:
            newly_completed = await self.repo.mark_completed(
                user_id, item.topic_id, item.id
            )
            if newly_completed and reward_on_success > 0 and self.user_repo is not None:
                await self.user_repo.add_xp(user_id, reward_on_success)
            return SubmitOut(
                isCorrect=True, message="Correct", rewardXp=reward_on_success
            )
        return SubmitOut(isCorrect=False, message="Incorrect", rewardXp=0)

    async def submit_single_choice(
        self, user_id: int, item_id: str, body: SubmitSingleChoiceIn
    ) -> SubmitOut:
        item, task = await self._task_item_and_task(item_id)
        if task.task_type != TaskType.SINGLE_CHOICE.value:
            raise HTTPException(400, "Task type mismatch")
        rows = await self.repo.list_task_single_choice([task.id])
        if not rows:
            raise HTTPException(500, "Task data missing")
        sc = rows[0]
        answer = body.model_dump(by_alias=True)
        is_correct = int(answer["selectedIndex"]) == int(sc.correct_index)
        return await self._persist_task_attempt(user_id, item, task, answer, is_correct)

    async def submit_fill_in_blank(
        self, user_id: int, item_id: str, body: SubmitFillBlankIn
    ) -> SubmitOut:
        item, task = await self._task_item_and_task(item_id)
        if task.task_type != TaskType.FILL_IN_BLANK.value:
            raise HTTPException(400, "Task type mismatch")
        rows = await self.repo.list_task_fill_blank([task.id])
        if not rows:
            raise HTTPException(500, "Task data missing")
        fb = rows[0]
        answer = body.model_dump()
        is_correct = str(answer.get("text", "")).strip() == str(fb.blank).strip()
        return await self._persist_task_attempt(user_id, item, task, answer, is_correct)

    async def submit_find_the_bug(
        self, user_id: int, item_id: str, body: SubmitFindBugIn
    ) -> SubmitOut:
        item, task = await self._task_item_and_task(item_id)
        if task.task_type != TaskType.FIND_THE_BUG.value:
            raise HTTPException(400, "Task type mismatch")
        rows = await self.repo.list_task_find_bug([task.id])
        if not rows:
            raise HTTPException(500, "Task data missing")
        bug = rows[0]
        answer = body.model_dump(by_alias=True)
        is_correct = int(answer["bugLineIndex"]) == int(bug.bug_line_index)
        return await self._persist_task_attempt(user_id, item, task, answer, is_correct)

    async def submit_code_order(
        self, user_id: int, item_id: str, body: SubmitCodeOrderIn
    ) -> SubmitOut:
        item, task = await self._task_item_and_task(item_id)
        if task.task_type != TaskType.CODE_ORDER.value:
            raise HTTPException(400, "Task type mismatch")
        rows = await self.repo.list_task_code_order([task.id])
        if not rows:
            raise HTTPException(500, "Task data missing")
        co = rows[0]
        answer = body.model_dump()
        try:
            correct_order = json.loads(co.correct_order or "[]")
        except Exception:
            correct_order = []
        is_correct = answer.get("order") == correct_order
        return await self._persist_task_attempt(user_id, item, task, answer, is_correct)

    async def submit_match_pairs(
        self, user_id: int, item_id: str, body: SubmitMatchPairsIn
    ) -> SubmitOut:
        item, task = await self._task_item_and_task(item_id)
        if task.task_type != TaskType.MATCH_PAIRS.value:
            raise HTTPException(400, "Task type mismatch")
        pairs_rows = await self.repo.list_task_pairs([task.id])
        pairs_list = [{"left": p.left, "right": p.right} for p in pairs_rows]
        answer = body.model_dump()
        submitted = {
            (p.get("left"), p.get("right")) for p in (answer.get("pairs") or [])
        }
        expected = {(p["left"], p["right"]) for p in pairs_list}
        is_correct = submitted == expected
        return await self._persist_task_attempt(user_id, item, task, answer, is_correct)

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

    async def admin_create_item(
        self, item_id: str, topic_id: str, type_: str, title: str, order: int
    ):
        return await self.repo.create_item(item_id, topic_id, type_, title, order)

    async def admin_delete_item(self, item_id: str):
        await self.repo.delete_item(item_id)

    async def admin_create_theory_block(
        self,
        item_id: str,
        type_: str,
        content: str,
        order: int,
        src: str | None,
        alt: str | None,
    ):
        return await self.repo.create_theory_block(
            item_id=item_id, type_=type_, content=content, order=order, src=src, alt=alt
        )

    async def admin_delete_theory_block(self, block_id: int):
        await self.repo.delete_theory_block(block_id)

    async def admin_create_task(self, payload: dict):
        return await self.repo.create_task(payload)

    async def admin_delete_task(self, item_id: str):
        await self.repo.delete_task_by_item(item_id)

    async def admin_wipe_all_topics(self) -> None:
        await self.repo.delete_all_topics()

    def _declarative_task_payload(self, item: dict) -> dict[str, Any]:
        tt = item["taskType"]
        base: dict[str, Any] = {
            "itemId": item["id"],
            "taskType": tt,
            "npcText": item.get("npcText", "") or "",
            "rewardXp": int(item.get("rewardXp") or 0),
        }
        if tt == "single-choice":
            base["question"] = item["question"]
            base["answers"] = item["answers"]
            base["correctIndex"] = item["correctIndex"]
        elif tt == "fill-in-blank":
            base["codeTemplate"] = item["codeTemplate"]
            base["blank"] = item["blank"]
        elif tt == "find-the-bug":
            base["bugLineIndex"] = item["bugLineIndex"]
            base["explanation"] = item.get("explanation", "") or ""
            base["codeLines"] = item["codeLines"]
        elif tt == "code-order":
            base["description"] = item.get("description", "") or ""
            base["codeLines"] = item["codeLines"]
            if item.get("correctOrder") is not None:
                base["correctOrder"] = item["correctOrder"]
        elif tt == "match-pairs":
            pairs = item.get("pairs") or []
            base["pairs"] = [
                {"left": p["left"], "right": p["right"], "order": int(p.get("order", pi))}
                for pi, p in enumerate(pairs)
            ]
        else:
            raise HTTPException(400, f"Unsupported taskType: {tt}")
        return base

    async def admin_publish_course_topics(self, topics: list[dict]) -> int:
        for ti, topic in enumerate(topics):
            await self.admin_create_topic(topic["id"], topic["title"], ti)
            for ii, item in enumerate(topic["items"]):
                await self.admin_create_item(
                    item["id"], topic["id"], item["type"], item["title"], ii
                )
                if item["type"] == "lesson":
                    for bi, block in enumerate(item.get("theoryBlocks", [])):
                        await self.admin_create_theory_block(
                            item["id"],
                            block["type"],
                            block.get("content", ""),
                            bi,
                            block.get("src"),
                            block.get("alt"),
                        )
                elif item["type"] == "task":
                    await self.admin_create_task(self._declarative_task_payload(item))
                else:
                    raise HTTPException(400, f"Unsupported item type: {item['type']}")
        return len(topics)

    async def admin_replace_entire_course(self, topics: list[dict]) -> int:
        await self.repo.delete_all_topics()
        return await self.admin_publish_course_topics(topics)

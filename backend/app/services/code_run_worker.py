import json
import logging

import httpx

from app.core.config import get_settings
from app.db.database import async_session
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.services.course_service import CourseService

logger = logging.getLogger(__name__)


async def dispatch_code_run_job(job_id: int) -> None:
    settings = get_settings()
    secret = settings.code_run_callback_secret
    if not secret.strip():
        async with async_session() as session:
            repo = CourseRepository(session)
            user_repo = UserRepository(session)
            svc = CourseService(repo, user_repo, settings)
            await svc.process_code_run_callback(
                job_id, "CE", "Секрет колбэка не настроен (CODE_RUN_CALLBACK_SECRET)"
            )
        return

    async with async_session() as session:
        repo = CourseRepository(session)
        job = await repo.get_code_run_job(job_id)
        if not job or job.status != "pending":
            return
        twt_rows = await repo.list_task_code_with_tests([job.task_id])
        if not twt_rows:
            user_repo = UserRepository(session)
            svc = CourseService(repo, user_repo, settings)
            await svc.process_code_run_callback(job_id, "CE", "Для задания нет тестов")
            return
        try:
            tests = json.loads(twt_rows[0].tests_json or "[]")
        except json.JSONDecodeError:
            tests = []
        inputs: list[str] = []
        outputs: list[str] = []
        for t in tests:
            inputs.append(str(t.get("input", "")))
            outputs.append(str(t.get("output", "")))
        if not inputs:
            user_repo = UserRepository(session)
            svc = CourseService(repo, user_repo, settings)
            await svc.process_code_run_callback(job_id, "CE", "Пустой набор тестов")
            return
        code_snapshot = job.code

    callback_url = (
        settings.code_run_internal_base_url.rstrip("/")
        + "/api/v1/internal/code-run/callback"
    )
    runner_url = settings.code_runner_url.rstrip("/") + "/run"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
            r = await client.post(
                runner_url,
                json={
                    "jobId": job_id,
                    "code": code_snapshot,
                    "inputs": inputs,
                    "outputs": outputs,
                    "callbackUrl": callback_url,
                    "callbackSecret": secret,
                    "timeLimitMs": 10_000,
                },
            )
            r.raise_for_status()
    except Exception:
        logger.exception("runner request failed for job_id=%s", job_id)
        async with async_session() as session:
            repo = CourseRepository(session)
            user_repo = UserRepository(session)
            svc = CourseService(repo, user_repo, settings)
            await svc.process_code_run_callback(
                job_id, "CE", "Не удалось выполнить проверку на сервисе-раннере"
            )

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import get_db
from app.repositories.course_repository import CourseRepository
from app.repositories.user_repository import UserRepository
from app.services.course_service import CourseService

router = APIRouter(prefix="/internal", tags=["internal"])


class CodeRunCallbackIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    jobId: int
    verdict: str
    detail: str = ""


@router.post("/code-run/callback")
async def code_run_callback(
    body: CodeRunCallbackIn,
    db: AsyncSession = Depends(get_db),
    x_code_run_secret: Annotated[str | None, Header(alias="X-Code-Run-Secret")] = None,
):
    settings = get_settings()
    expected = settings.code_run_callback_secret
    if not expected or (x_code_run_secret or "") != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    repo = CourseRepository(db)
    user_repo = UserRepository(db)
    svc = CourseService(repo, user_repo, settings)
    await svc.process_code_run_callback(body.jobId, body.verdict, body.detail)
    return {"ok": True}

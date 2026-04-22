"""Удаляет все таблицы и создаёт их заново (полная очистка данных)."""

from __future__ import annotations

import asyncio
import sys

import app.models  # noqa: F401 — регистрация моделей в metadata
from app.db.base import Base
from app.db.database import engine


async def reset() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def main() -> None:
    asyncio.run(reset())
    print("База данных очищена: таблицы пересозданы.", file=sys.stderr)


if __name__ == "__main__":
    main()

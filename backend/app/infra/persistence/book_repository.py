import os
from typing import Sequence

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.application.repositories.book_repository import BookRepository
from app.domain.entities.book import BookDomain
from app.infra.db.mappers.book_mapper import BookMapper
from app.infra.persistence.sql_guard import guard_select


class BookPostgreRepository(BookRepository):
    """Read-only structured search over PostgreSQL for the text-to-SQL path.

    The SELECT-only guard runs INSIDE this adapter so it cannot be bypassed; a
    per-statement ``statement_timeout`` caps runaway queries. Guard tuning is
    env-driven (``SQL_MAX_LIMIT`` / ``SQL_STATEMENT_TIMEOUT_MS``), matching the
    ``os.getenv`` style of ``infra/config.py``.
    """

    DEFAULT_MAX_LIMIT = 50
    DEFAULT_TIMEOUT_MS = 5000

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._max_limit = int(os.getenv("SQL_MAX_LIMIT", self.DEFAULT_MAX_LIMIT))
        self._timeout_ms = int(
            os.getenv("SQL_STATEMENT_TIMEOUT_MS", self.DEFAULT_TIMEOUT_MS)
        )

    async def execute_select(self, sql: str) -> Sequence[BookDomain]:
        safe_sql = guard_select(sql, self._max_limit)

        # Raw text runs on the connection (SET LOCAL + SELECT share one
        # transaction); session.exec is select/ORM-oriented and auto-scalars.
        conn = await self._session.connection()
        # Cap query runtime. Value is an int we control (not user input).
        await conn.execute(
            text(f"SET LOCAL statement_timeout = {int(self._timeout_ms)}")
        )
        result = await conn.execute(text(safe_sql))
        rows = result.mappings().all()
        return [BookMapper.from_row(row) for row in rows]

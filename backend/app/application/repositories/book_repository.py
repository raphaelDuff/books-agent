from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.book import BookDomain


class BookRepository(ABC):
    """Read-only data-access port for structured book search over PostgreSQL.

    ``execute_select`` runs an LLM-generated ``SELECT``. The implementation MUST
    enforce read-only safety (reject non-SELECT/multi-statement SQL, force a
    ``LIMIT``, apply a statement timeout) inside the adapter so no caller can
    bypass the guard.
    """

    @abstractmethod
    async def execute_select(self, sql: str) -> Sequence[BookDomain]:
        """Validate, guard, and execute a read-only SELECT, returning books.

        Raises:
            ValueError: if the SQL fails the SELECT-only guard.
        """
        raise NotImplementedError

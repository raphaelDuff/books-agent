from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.book import BookDomain


class BookVectorRepository(ABC):
    """Data-access port for semantic book search over the vector store."""

    @abstractmethod
    async def search_by_vector(
        self,
        vector: list[float],
        limit: int,
        isbn13_allowlist: Sequence[str] | None = None,
    ) -> Sequence[BookDomain]:
        """Return books nearest to ``vector``, ordered by similarity.

        When ``isbn13_allowlist`` is given (the HYBRID path), results are
        constrained to that set via a filtered nearest-neighbour search.
        """
        raise NotImplementedError

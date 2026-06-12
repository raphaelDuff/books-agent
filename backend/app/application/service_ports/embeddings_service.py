from abc import ABC, abstractmethod


class EmbeddingsService(ABC):
    """Capability port for turning text into a vector for semantic search.

    The same implementation must be used for ingest and query, or similarity is
    meaningless.
    """

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Embed a single piece of text into a dense vector."""
        raise NotImplementedError

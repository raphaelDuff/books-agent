from abc import ABC, abstractmethod

from app.application.common.result import Result
from app.application.dtos.book_dtos import BookRecommendationResponseModel
from app.application.repositories.book_repository import BookRepository


class BookRecommenderPort(ABC):
    """Capability port for the compiled recommendation agent.

    Implemented by the LangGraph adapter in ``app.agent``. The request-scoped
    ``book_repo`` (bound to the current UoW session) is supplied per call; the
    LLM, embeddings, and vector-store dependencies are bound when the graph is
    built. ``thread_id`` keys the checkpointer.
    """

    @abstractmethod
    async def recommend(
        self,
        question: str,
        book_repo: BookRepository,
        thread_id: str,
    ) -> Result[BookRecommendationResponseModel]:
        raise NotImplementedError

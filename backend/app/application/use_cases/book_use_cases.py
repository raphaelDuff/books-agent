from dataclasses import dataclass

from app.application.common.result import Result
from app.application.service_ports.book_recommender import BookRecommenderPort
from app.application.uow import UnitOfWork


@dataclass(frozen=True)
class AnswerBookQuestionUseCase:
    """Answer a natural-language book question via the recommendation agent.

    Read-only: the UoW is opened only to hand the request-scoped
    ``BookRepository`` to the graph for structured (text-to-SQL) search.
    """

    uow: UnitOfWork
    recommender: BookRecommenderPort

    async def execute(self, question: str, thread_id: str) -> Result:
        async with self.uow:
            return await self.recommender.recommend(
                question=question,
                book_repo=self.uow.books,
                thread_id=thread_id,
            )

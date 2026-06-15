from app.agent.graph import build_graph
from app.application.common.result import Result
from app.application.dtos.book_dtos import BookRecommendationResponseModel
from app.application.repositories.book_repository import BookRepository
from app.application.repositories.book_vector_repository import BookVectorRepository
from app.application.service_ports.book_recommender import BookRecommenderPort
from app.application.service_ports.embeddings_service import EmbeddingsService
from app.application.service_ports.llm_service import LLMService, RankedPick
from app.domain.entities.book import BookDomain


class GraphBookRecommender(BookRecommenderPort):
    """Adapter wrapping the compiled LangGraph graph as a ``BookRecommenderPort``.

    Holds the long-lived dependencies (LLM, embeddings, vector store) and the
    compiled graph; the request-scoped ``book_repo`` and ``thread_id`` arrive per
    call and are merged into the graph's ``RunnableConfig``.
    """

    def __init__(
        self,
        llm: LLMService,
        embeddings: EmbeddingsService,
        vector_repo: BookVectorRepository,
    ) -> None:
        self._llm = llm
        self._embeddings = embeddings
        self._vector_repo = vector_repo
        self._graph = build_graph()

    async def recommend(
        self,
        question: str,
        book_repo: BookRepository,
        thread_id: str,
    ) -> Result[BookRecommendationResponseModel]:
        config = {
            "configurable": {
                "thread_id": thread_id,
                "llm": self._llm,
                "embeddings": self._embeddings,
                "vector_repo": self._vector_repo,
                "book_repo": book_repo,
            }
        }
        final = await self._graph.ainvoke({"question": question}, config=config)

        picks = [
            RankedPick(
                book=BookDomain.from_dict(pick["book"]),
                justification=pick["justification"],
            )
            for pick in (final.get("picks") or [])
        ]
        response = BookRecommendationResponseModel.from_picks(
            intent=final.get("intent", ""),
            thread_id=thread_id,
            generated_sql=final.get("generated_sql"),
            picks=picks,
        )
        return Result.success(response)

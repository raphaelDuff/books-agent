from typing import TypedDict

from app.application.repositories.book_repository import BookRepository
from app.application.repositories.book_vector_repository import BookVectorRepository
from app.application.service_ports.embeddings_service import EmbeddingsService
from app.application.service_ports.llm_service import LLMService

# Result sizing (plan §6): a short ranked list, with room for the reranker.
FINAL_PICKS = 5
SEMANTIC_OVERFETCH = 25


class ConfigSchema(TypedDict):
    """Shape of ``config['configurable']`` the nodes read their deps from.

    ``llm``, ``embeddings`` and ``vector_repo`` are singletons bound at graph
    build; ``book_repo`` is request-scoped and supplied per invoke.
    """

    llm: LLMService
    embeddings: EmbeddingsService
    vector_repo: BookVectorRepository
    book_repo: BookRepository

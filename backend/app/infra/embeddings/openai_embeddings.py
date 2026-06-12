from langchain_openai import OpenAIEmbeddings

from app.application.service_ports.embeddings_service import EmbeddingsService


class OpenAIEmbeddingsService(EmbeddingsService):
    """EmbeddingsService backed by OpenAI embeddings via langchain-openai.

    The same model must be used for ingest and query (configured once).
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._embeddings = OpenAIEmbeddings(model=model, api_key=api_key)

    async def embed(self, text: str) -> list[float]:
        return await self._embeddings.aembed_query(text)

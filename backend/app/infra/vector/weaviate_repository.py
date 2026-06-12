import asyncio
from typing import Sequence

import weaviate
from weaviate.classes.query import Filter

from app.application.repositories.book_vector_repository import BookVectorRepository
from app.domain.entities.book import BookDomain

_RETURN_PROPERTIES = [
    "isbn13",
    "isbn10",
    "title",
    "subtitle",
    "authors",
    "categories",
    "thumbnail",
    "description",
    "published_year",
    "average_rating",
    "num_pages",
    "ratings_count",
]


def _to_domain(props: dict) -> BookDomain:
    return BookDomain(
        isbn13=str(props.get("isbn13") or ""),
        title=str(props.get("title") or ""),
        authors=str(props.get("authors") or ""),
        description=str(props.get("description") or ""),
        subtitle=props.get("subtitle"),
        isbn10=props.get("isbn10"),
        categories=props.get("categories"),
        thumbnail=props.get("thumbnail"),
        published_year=props.get("published_year"),
        average_rating=props.get("average_rating"),
        num_pages=props.get("num_pages"),
        ratings_count=props.get("ratings_count"),
    )


class WeaviateBookRepository(BookVectorRepository):
    """Semantic book search over Weaviate (v4).

    The vector client is synchronous, so queries run in a worker thread to avoid
    blocking the async graph's event loop.
    """

    def __init__(self, client: "weaviate.WeaviateClient", collection: str) -> None:
        self._client = client
        self._collection = collection

    async def search_by_vector(
        self,
        vector: list[float],
        limit: int,
        isbn13_allowlist: Sequence[str] | None = None,
    ) -> Sequence[BookDomain]:
        return await asyncio.to_thread(
            self._search, vector, limit, isbn13_allowlist
        )

    def _search(
        self,
        vector: list[float],
        limit: int,
        isbn13_allowlist: Sequence[str] | None,
    ) -> list[BookDomain]:
        collection = self._client.collections.get(self._collection)
        filters = None
        if isbn13_allowlist:
            # HYBRID: constrain the ANN search to the SQL allowlist.
            filters = Filter.by_property("isbn13").contains_any(list(isbn13_allowlist))
        response = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            filters=filters,
            return_properties=_RETURN_PROPERTIES,
        )
        return [_to_domain(o.properties) for o in response.objects]

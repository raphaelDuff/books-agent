from dataclasses import dataclass
from typing import Any, Self

from app.domain.entities.entity import Entity


@dataclass
class BookDomain(Entity):
    """A book from the catalogue.

    Identity for books is the ``isbn13`` natural key (the dataset primary key);
    the inherited UUID ``id`` is unused for this read-only aggregate.
    """

    isbn13: str
    title: str
    authors: str
    description: str
    subtitle: str | None = None
    isbn10: str | None = None
    categories: str | None = None
    thumbnail: str | None = None
    published_year: int | None = None
    average_rating: float | None = None
    num_pages: int | None = None
    ratings_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict view (constructor fields only, no ``id``).

        Used to keep graph state serializable for the checkpointer.
        """
        return {
            "isbn13": self.isbn13,
            "title": self.title,
            "authors": self.authors,
            "description": self.description,
            "subtitle": self.subtitle,
            "isbn10": self.isbn10,
            "categories": self.categories,
            "thumbnail": self.thumbnail,
            "published_year": self.published_year,
            "average_rating": self.average_rating,
            "num_pages": self.num_pages,
            "ratings_count": self.ratings_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**data)

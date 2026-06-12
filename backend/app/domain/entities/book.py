from dataclasses import dataclass

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

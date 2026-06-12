from dataclasses import dataclass


@dataclass(frozen=True)
class BookPickViewModel:
    """A single recommended book for display."""

    isbn13: str
    title: str
    authors: str
    thumbnail: str | None
    published_year: int | None
    average_rating: float | None
    justification: str


@dataclass(frozen=True)
class BookRecommendationViewModel:
    """View-specific representation of a recommendation answer."""

    intent: str
    thread_id: str
    generated_sql: str | None
    picks: list[BookPickViewModel]

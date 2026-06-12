from typing import Self

from pydantic import BaseModel, Field

from app.application.service_ports.llm_service import RankedPick


class BookQueryRequestModel(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    thread_id: str | None = None


class BookPickModel(BaseModel):
    isbn13: str
    title: str
    authors: str
    thumbnail: str | None = None
    published_year: int | None = None
    average_rating: float | None = None
    justification: str

    @classmethod
    def from_pick(cls, pick: RankedPick) -> Self:
        book = pick.book
        return cls(
            isbn13=book.isbn13,
            title=book.title,
            authors=book.authors,
            thumbnail=book.thumbnail,
            published_year=book.published_year,
            average_rating=book.average_rating,
            justification=pick.justification,
        )


class BookRecommendationResponseModel(BaseModel):
    intent: str
    thread_id: str
    generated_sql: str | None = None
    picks: list[BookPickModel]

    @classmethod
    def from_picks(
        cls,
        intent: str,
        thread_id: str,
        generated_sql: str | None,
        picks: list[RankedPick],
    ) -> Self:
        return cls(
            intent=intent,
            thread_id=thread_id,
            generated_sql=generated_sql,
            picks=[BookPickModel.from_pick(p) for p in picks],
        )

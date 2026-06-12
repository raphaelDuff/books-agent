from typing import Mapping

from app.domain.entities.book import BookDomain
from app.infra.db.models.book_model import BookSQLModel


class BookMapper:
    @staticmethod
    def to_domain(model: BookSQLModel) -> BookDomain:
        return BookDomain(
            isbn13=model.isbn13,
            title=model.title,
            authors=model.authors,
            description=model.description,
            subtitle=model.subtitle,
            isbn10=model.isbn10,
            categories=model.categories,
            thumbnail=model.thumbnail,
            published_year=model.published_year,
            average_rating=model.average_rating,
            num_pages=model.num_pages,
            ratings_count=model.ratings_count,
        )

    @staticmethod
    def to_model(entity: BookDomain) -> BookSQLModel:
        return BookSQLModel(
            isbn13=entity.isbn13,
            isbn10=entity.isbn10,
            title=entity.title,
            subtitle=entity.subtitle,
            authors=entity.authors,
            categories=entity.categories,
            thumbnail=entity.thumbnail,
            description=entity.description,
            published_year=entity.published_year,
            average_rating=entity.average_rating,
            num_pages=entity.num_pages,
            ratings_count=entity.ratings_count,
        )

    @staticmethod
    def from_row(row: Mapping) -> BookDomain:
        """Map a raw SQL result row (text-to-SQL path) to a BookDomain.

        Tolerant of partial column selection: required fields fall back to safe
        defaults so an unusual LLM ``SELECT`` never crashes the mapping.
        """
        return BookDomain(
            isbn13=str(row.get("isbn13") or ""),
            title=str(row.get("title") or ""),
            authors=str(row.get("authors") or ""),
            description=str(row.get("description") or ""),
            subtitle=row.get("subtitle"),
            isbn10=row.get("isbn10"),
            categories=row.get("categories"),
            thumbnail=row.get("thumbnail"),
            published_year=row.get("published_year"),
            average_rating=row.get("average_rating"),
            num_pages=row.get("num_pages"),
            ratings_count=row.get("ratings_count"),
        )

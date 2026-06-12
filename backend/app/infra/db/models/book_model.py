from typing import Optional

from sqlalchemy import Text
from sqlmodel import Column, Field, SQLModel


class BookSQLModel(SQLModel, table=True):
    __tablename__ = "books"  # pyright: ignore[reportAssignmentType]

    isbn13: str = Field(primary_key=True, index=True)
    isbn10: Optional[str] = Field(default=None)
    title: str = Field(index=True)
    subtitle: Optional[str] = Field(default=None)
    authors: str = Field(index=True)
    categories: Optional[str] = Field(default=None, index=True)
    thumbnail: Optional[str] = Field(default=None)
    description: str = Field(sa_column=Column(Text))
    published_year: Optional[int] = Field(default=None, index=True)
    average_rating: Optional[float] = Field(default=None, index=True)
    num_pages: Optional[int] = Field(default=None)
    ratings_count: Optional[int] = Field(default=None)

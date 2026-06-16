from typing import Optional

from app.application.dtos.book_dtos import BookRecommendationResponseModel
from app.interfaces.presenters.book_presenter import BookPresenter
from app.interfaces.view_models.base import ErrorViewModel
from app.interfaces.view_models.book_vm import (
    BookPickViewModel,
    BookRecommendationViewModel,
)


class WebBookPresenter(BookPresenter):
    """Web-specific book-recommendation presenter."""

    def present_recommendation(
        self, response_model: BookRecommendationResponseModel
    ) -> BookRecommendationViewModel:
        return BookRecommendationViewModel(
            intent=response_model.intent,
            thread_id=response_model.thread_id,
            generated_sql=response_model.generated_sql,
            picks=[
                BookPickViewModel(
                    isbn13=p.isbn13,
                    title=p.title,
                    authors=p.authors,
                    thumbnail=p.thumbnail,
                    published_year=p.published_year,
                    average_rating=p.average_rating,
                    justification=p.justification,
                    description=p.description,
                )
                for p in response_model.picks
            ],
        )

    def present_error(
        self, error_msg: str, code: Optional[str] = None
    ) -> ErrorViewModel:
        return ErrorViewModel(message=error_msg, code=code)

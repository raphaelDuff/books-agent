from abc import ABC, abstractmethod
from typing import Optional

from app.application.dtos.book_dtos import BookRecommendationResponseModel
from app.interfaces.view_models.base import ErrorViewModel
from app.interfaces.view_models.book_vm import BookRecommendationViewModel


class BookPresenter(ABC):
    """Abstract presenter for book-recommendation output."""

    @abstractmethod
    def present_recommendation(
        self, response_model: BookRecommendationResponseModel
    ) -> BookRecommendationViewModel:
        """Convert a recommendation response to a view model."""
        raise NotImplementedError

    @abstractmethod
    def present_error(
        self, error_msg: str, code: Optional[str] = None
    ) -> ErrorViewModel:
        """Format an error for display."""
        raise NotImplementedError

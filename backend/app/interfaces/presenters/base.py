from abc import ABC, abstractmethod
from app.application.dtos.user_dtos import UserResponseModel
from app.interfaces.view_models.user_vm import UserViewModel
from app.interfaces.view_models.base import ErrorViewModel
from typing import Optional
from datetime import date


class UserPresenter(ABC):
    """Abstract base presenter for task-related output."""

    @abstractmethod
    def present_user(self, response_model: UserResponseModel) -> UserViewModel:
        """Convert task response to view model."""
        pass

    @abstractmethod
    def present_error(
        self, error_msg: str, code: Optional[str] = None
    ) -> ErrorViewModel:
        """Format error message for display."""
        pass

    def format_birth_date(self, birth_date: date) -> str:
        return birth_date.strftime("%d/%m/%Y")

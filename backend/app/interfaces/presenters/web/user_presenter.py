from typing import Optional

from app.interfaces.presenters.base import UserPresenter
from app.application.dtos.user_dtos import UserResponseModel
from app.interfaces.view_models.user_vm import UserViewModel
from app.interfaces.view_models.base import ErrorViewModel


class WebUserPresenter(UserPresenter):
    """Web-specific user presenter."""

    def present_user(self, response_model: UserResponseModel) -> UserViewModel:
        """Format user for web display."""
        return UserViewModel(
            id=response_model.id,
            name=response_model.name,
            email=response_model.email,
            birth_date=self.format_birth_date(response_model.birth_date),
            role=response_model.role,
        )

    def present_error(
        self, error_msg: str, code: Optional[str] = None
    ) -> ErrorViewModel:
        """Format error for web response."""
        return ErrorViewModel(message=error_msg, code=code)

from typing import Optional

from app.application.dtos.auth_dtos import TokenResponseModel
from app.interfaces.presenters.auth_presenter import AuthPresenter
from app.interfaces.view_models.auth_vm import TokenViewModel
from app.interfaces.view_models.base import ErrorViewModel


class WebAuthPresenter(AuthPresenter):
    def present_token(self, response_model: TokenResponseModel) -> TokenViewModel:
        return TokenViewModel(
            access_token=response_model.access_token,
            token_type=response_model.token_type,
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        return ErrorViewModel(message=error_msg, code=code)

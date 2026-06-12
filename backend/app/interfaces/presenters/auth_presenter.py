from abc import ABC, abstractmethod
from typing import Optional

from app.application.dtos.auth_dtos import TokenResponseModel
from app.interfaces.view_models.auth_vm import TokenViewModel
from app.interfaces.view_models.base import ErrorViewModel


class AuthPresenter(ABC):
    @abstractmethod
    def present_token(self, response_model: TokenResponseModel) -> TokenViewModel:
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        pass

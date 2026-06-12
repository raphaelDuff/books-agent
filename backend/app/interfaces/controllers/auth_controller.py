from dataclasses import dataclass

from app.application.use_cases.auth_use_cases import (
    AuthenticateUserUseCase,
    CreateAccessTokenUseCase,
    GetCurrentUserUseCase,
)
from app.interfaces.presenters.auth_presenter import AuthPresenter
from app.interfaces.presenters.base import UserPresenter
from app.interfaces.view_models.auth_vm import TokenViewModel
from app.interfaces.view_models.base import OperationResult
from app.interfaces.view_models.user_vm import UserViewModel


@dataclass
class AuthController:
    authenticate_use_case: AuthenticateUserUseCase
    create_token_use_case: CreateAccessTokenUseCase
    get_current_user_use_case: GetCurrentUserUseCase
    auth_presenter: AuthPresenter
    user_presenter: UserPresenter

    async def handle_token(
        self, username: str, password: str
    ) -> OperationResult[TokenViewModel]:
        auth_result = await self.authenticate_use_case.execute(username, password)
        if not auth_result.is_success:
            error = auth_result.error
            vm = self.auth_presenter.present_error(error.message, str(error.code.name))
            return OperationResult.fail(vm.message, vm.code)

        user = auth_result.value
        token_result = await self.create_token_use_case.execute(
            subject=user.email, role=user.role
        )
        if not token_result.is_success:
            error = token_result.error
            vm = self.auth_presenter.present_error(error.message, str(error.code.name))
            return OperationResult.fail(vm.message, vm.code)

        token_vm = self.auth_presenter.present_token(token_result.value)
        return OperationResult.succeed(token_vm)

    async def handle_current_user(self, token: str) -> OperationResult[UserViewModel]:
        result = await self.get_current_user_use_case.execute(token)
        if not result.is_success:
            error = result.error
            vm = self.auth_presenter.present_error(error.message, str(error.code.name))
            return OperationResult.fail(vm.message, vm.code)

        user_vm = self.user_presenter.present_user(result.value)
        return OperationResult.succeed(user_vm)

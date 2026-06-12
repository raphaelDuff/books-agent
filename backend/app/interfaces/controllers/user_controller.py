from dataclasses import dataclass
from datetime import date
from app.application.use_cases.user_use_cases import CreateUserUseCase
from app.interfaces.view_models.base import OperationResult
from app.application.dtos.user_dtos import CreateUserRequestModel
from app.interfaces.presenters.base import UserPresenter
from app.interfaces.view_models.user_vm import UserViewModel


@dataclass
class UserController:
    """Controller for user-related operations"""

    create_use_case: CreateUserUseCase
    presenter: UserPresenter

    async def handle_create(
        self,
        name: str,
        email: str,
        password: str,
        birth_date: date,
    ) -> OperationResult[UserViewModel]:
        try:
            request = CreateUserRequestModel(
                name=name,
                email=email,
                password=password,
                birth_date=birth_date,
            )
            result = await self.create_use_case.execute(request)
            if result.is_success:
                # TODO: Create the presenter
                view_model = self.presenter.present_user(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

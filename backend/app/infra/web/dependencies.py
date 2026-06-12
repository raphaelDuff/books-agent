from typing import Callable

from fastapi import Depends, Request

from app.application.uow import UnitOfWork
from app.application.use_cases.auth_use_cases import (
    AuthenticateUserUseCase,
    CreateAccessTokenUseCase,
    GetCurrentUserUseCase,
)
from app.application.use_cases.user_use_cases import CreateUserUseCase, GetUsersUseCase
from app.domain.services.password_hasher import PasswordHasher
from app.domain.services.token_service import TokenService
from app.infra.configuration.container import Application
from app.interfaces.controllers.auth_controller import AuthController
from app.interfaces.controllers.user_controller import UserController
from app.interfaces.presenters.auth_presenter import AuthPresenter
from app.interfaces.presenters.base import UserPresenter


def get_container(request: Request) -> Application:
    return request.app.state.container


def get_user_presenter(
    container: Application = Depends(get_container),
) -> UserPresenter:
    return container.user_presenter


def get_auth_presenter(
    container: Application = Depends(get_container),
) -> AuthPresenter:
    return container.auth_presenter


def get_token_service(
    container: Application = Depends(get_container),
) -> TokenService:
    return container.token_service


def get_password_hasher(
    container: Application = Depends(get_container),
) -> PasswordHasher:
    return container.password_hasher


def get_uow_factory(
    container: Application = Depends(get_container),
) -> Callable[[], UnitOfWork]:
    return container.uow_factory


def get_create_user_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> CreateUserUseCase:
    return CreateUserUseCase(uow=uow_factory())


def get_get_users_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> GetUsersUseCase:
    return GetUsersUseCase(uow=uow_factory())


def get_user_controller(
    create_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    presenter: UserPresenter = Depends(get_user_presenter),
) -> UserController:
    return UserController(
        create_use_case=create_use_case,
        presenter=presenter,
    )


def get_authenticate_user_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(uow=uow_factory(), password_hasher=password_hasher)


def get_create_token_use_case(
    token_service: TokenService = Depends(get_token_service),
) -> CreateAccessTokenUseCase:
    return CreateAccessTokenUseCase(token_service=token_service)


def get_get_current_user_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    token_service: TokenService = Depends(get_token_service),
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(uow=uow_factory(), token_service=token_service)


def get_auth_controller(
    authenticate_use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
    create_token_use_case: CreateAccessTokenUseCase = Depends(get_create_token_use_case),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
    auth_presenter: AuthPresenter = Depends(get_auth_presenter),
    user_presenter: UserPresenter = Depends(get_user_presenter),
) -> AuthController:
    return AuthController(
        authenticate_use_case=authenticate_use_case,
        create_token_use_case=create_token_use_case,
        get_current_user_use_case=get_current_user_use_case,
        auth_presenter=auth_presenter,
        user_presenter=user_presenter,
    )

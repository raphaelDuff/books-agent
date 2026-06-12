from dataclasses import dataclass
from typing import Callable

from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.services.password_hasher import PasswordHasher
from app.domain.services.token_service import TokenService
from app.interfaces.presenters.auth_presenter import AuthPresenter
from app.interfaces.presenters.base import UserPresenter
from app.application.uow import UnitOfWork
from app.infra.repository_factory import create_repositories
from app.infra.uow import SqlAlchemyUnitOfWork


def create_application(
    session_factory: Callable[[], AsyncSession],
    user_presenter: UserPresenter,
    auth_presenter: AuthPresenter,
    token_service: TokenService,
    password_hasher: PasswordHasher,
) -> "Application":
    repo_factories = create_repositories()

    def uow_factory() -> UnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory, repo_factories)

    return Application(
        uow_factory=uow_factory,
        user_presenter=user_presenter,
        auth_presenter=auth_presenter,
        token_service=token_service,
        password_hasher=password_hasher,
    )


@dataclass
class Application:
    uow_factory: Callable[[], UnitOfWork]
    user_presenter: UserPresenter
    auth_presenter: AuthPresenter
    token_service: TokenService
    password_hasher: PasswordHasher

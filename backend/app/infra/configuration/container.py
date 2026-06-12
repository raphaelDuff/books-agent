from dataclasses import dataclass
from typing import Callable

from sqlmodel.ext.asyncio.session import AsyncSession

from app.application.service_ports.book_recommender import BookRecommenderPort
from app.application.service_ports.password_hasher import PasswordHasher
from app.application.service_ports.token_service import TokenService
from app.application.uow import UnitOfWork
from app.infra.repository_factory import create_repositories
from app.infra.uow import SqlAlchemyUnitOfWork
from app.interfaces.presenters.auth_presenter import AuthPresenter
from app.interfaces.presenters.base import UserPresenter
from app.interfaces.presenters.book_presenter import BookPresenter


def create_application(
    session_factory: Callable[[], AsyncSession],
    user_presenter: UserPresenter,
    auth_presenter: AuthPresenter,
    book_presenter: BookPresenter,
    token_service: TokenService,
    password_hasher: PasswordHasher,
    book_recommender: BookRecommenderPort,
) -> "Application":
    repo_factories = create_repositories()

    def uow_factory() -> UnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory, repo_factories)

    return Application(
        uow_factory=uow_factory,
        user_presenter=user_presenter,
        auth_presenter=auth_presenter,
        book_presenter=book_presenter,
        token_service=token_service,
        password_hasher=password_hasher,
        book_recommender=book_recommender,
    )


@dataclass
class Application:
    uow_factory: Callable[[], UnitOfWork]
    user_presenter: UserPresenter
    auth_presenter: AuthPresenter
    book_presenter: BookPresenter
    token_service: TokenService
    password_hasher: PasswordHasher
    book_recommender: BookRecommenderPort

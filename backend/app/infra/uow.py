from typing import Any, Callable, Mapping, Self
from sqlmodel.ext.asyncio.session import AsyncSession

from app.application.repositories.user_repository import UserRepository


RepoFactory = Callable[[AsyncSession], Any]


class SqlAlchemyUnitOfWork:
    users: UserRepository

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        repo_factories: Mapping[str, RepoFactory],
    ):
        self._session_factory = session_factory
        self._repo_factories = repo_factories

    async def __aenter__(self) -> Self:
        self.session = self._session_factory()
        for name, factory in self._repo_factories.items():
            setattr(self, name, factory(self.session))

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

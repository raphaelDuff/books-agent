from enum import StrEnum, auto
import os
from typing import Callable

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


class RepositoryType(StrEnum):
    POSTGRESQL = auto()


class Config:
    """Application configuration."""

    # DEFAULT values
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.POSTGRESQL
    DEFAULT_DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/samizdat"
    )

    _engine: AsyncEngine | None = None

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """Get the configured repository type."""
        repo_type_str = os.getenv(
            "CONFIG_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value
        )
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid repository type: {repo_type_str}")

    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL."""
        return os.getenv("DATABASE_URL", cls.DEFAULT_DATABASE_URL)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Get or create the async database engine (singleton)."""
        if cls._engine is None:
            cls._engine = create_async_engine(
                cls.get_database_url(),
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            )
        return cls._engine

    @classmethod
    def get_session_factory(cls) -> Callable[[], AsyncSession]:
        """Get a factory function that creates new async sessions."""
        engine = cls.get_engine()

        def session_factory() -> AsyncSession:
            return AsyncSession(engine, expire_on_commit=False)

        return session_factory

    @classmethod
    async def dispose_engine(cls) -> None:
        """Dispose of the database engine (for cleanup)."""
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._engine = None

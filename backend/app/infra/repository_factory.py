from typing import Any, Callable

from sqlmodel.ext.asyncio.session import AsyncSession

from app.infra.config import Config
from app.infra.persistence.book_repository import BookPostgreRepository
from app.infra.persistence.postgresql_repository import UserPostgreRepository

REPO_MAP = {
    "postgresql": {
        "users": UserPostgreRepository,
        "books": BookPostgreRepository,
    }
}


def create_repositories() -> dict[str, Callable[[AsyncSession], Any]]:
    """
    Create and configure the appropriate repository implementations based on configuration.

    Returns:
        A tuple of (TaskRepository, ProjectRepository)
    """
    repo_type = Config.get_repository_type()

    return {
        name: lambda s, cls=repo: cls(s) for name, repo in REPO_MAP[repo_type].items()
    }

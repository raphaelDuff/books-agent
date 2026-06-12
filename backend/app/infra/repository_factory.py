from app.application.repositories.user_repository import UserRepository
from app.infra.config import Config
from app.infra.persistence.postgresql_repository import UserPostgreRepository
from typing import Callable
from sqlmodel.ext.asyncio.session import AsyncSession

REPO_MAP = {
    "postgresql": {
        "users": UserPostgreRepository,
    }
}


def create_repositories() -> dict[str, Callable[[AsyncSession], UserRepository]]:
    """
    Create and configure the appropriate repository implementations based on configuration.

    Returns:
        A tuple of (TaskRepository, ProjectRepository)
    """
    repo_type = Config.get_repository_type()

    return {
        name: lambda s, cls=repo: cls(s) for name, repo in REPO_MAP[repo_type].items()
    }

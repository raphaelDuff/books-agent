from uuid import UUID

from app.application.repositories.user_repository import UserRepository
from app.domain.entities.user import UserDomain
from app.domain.exceptions import UserIdNotFoundError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Sequence
from app.infra.guards import guard_not_none
from app.infra.db.models.user_model import UserSQLModel
from app.infra.db.mappers.user_mapper import UserMapper


class UserPostgreRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with async database session.

        Args:
            session: SQLModel async session for database operations
        """
        self._session = session

    async def get_by_id(self, user_id: UUID) -> UserDomain:
        """
        Retrieve a user by ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            User entity

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = await self._session.get(UserSQLModel, user_id)
        if user is None:
            raise UserIdNotFoundError(user_id)
        return UserMapper.to_domain(user)

    async def get_by_email(self, email: str) -> UserDomain | None:
        """
        Retrieve a user by email address.

        Args:
            email: The email address of the user

        Returns:
            User entity

        Raises:
            UserEmailNotFoundError: If user with the email doesn't exist
        """
        statement = select(UserSQLModel).where(UserSQLModel.email == email)
        result = await self._session.exec(statement)
        user = result.one_or_none()
        return UserMapper.to_domain(user) if user else None

    async def get_all(self) -> Sequence[UserDomain]:
        """
        Retrieve all users from the database.

        Returns:
            Sequence of all User entities
        """
        statement = select(UserSQLModel)
        result = await self._session.exec(statement)
        users = result.all()
        return [UserMapper.to_domain(user) for user in users]

    async def save(self, user: UserDomain) -> None:
        """
        Save a user to the database.

        Args:
            user: The User entity to save
        """
        user_db = UserMapper.to_model(user)
        self._session.add(user_db)

    async def update(self, user: UserDomain) -> None:
        """
        Update an existing user in the database.

        Args:
            user: The User entity with updated information

        Raises:
            Exception: If user doesn't exist in the database
        """
        user_db = await self._session.get(UserSQLModel, user.id)
        user_db = guard_not_none(
            user_db, "PostgreSQL Repository Error: Update method - user was not found"
        )
        UserMapper.to_model(user, user_db)

    async def delete(self, user_id: UUID) -> None:
        """
        Delete a user from the database.

        Args:
            user_id: The unique identifier of the user to delete

        Raises:
            UserIdNotFoundError: If user doesn't exist
        """
        user = await self._session.get(UserSQLModel, user_id)
        if user is None:
            raise UserIdNotFoundError(user_id)
        await self._session.delete(user)

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import UserDomain
from typing import Sequence


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserDomain | None:
        """
        Retrieve a user by its ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            The requested User entity

        Raises:
            UserNotFoundError: If no user exists with the given ID
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserDomain | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The unique email address of the user

        Returns:
            The requested User entity if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> Sequence[UserDomain]:
        """
        Retrieve a list of all User.

        Args:
            None

        Returns:
             Retrieve a list of all Users or empty list
        """
        pass

    @abstractmethod
    async def save(self, user: UserDomain) -> None:
        """
        Save a user to the repository.

        Args:
            user: The User entity to save
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """
        Delete a user from the repository.

        Args:
            user_id: The unique identifier of the user to delete
        """
        pass

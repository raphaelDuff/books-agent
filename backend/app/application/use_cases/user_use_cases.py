from dataclasses import dataclass

from app.application.common.result import Error, Result
from app.application.dtos.user_dtos import (
    CreateUserRequestModel,
    UsersListResponseModel,
    UserResponseModel,
)
from app.domain.entities.user import UserDomain
from uuid import uuid4
from app.application.uow import UnitOfWork


@dataclass(frozen=True)
class CreateUserUseCase:
    """
    Use case for registering a new user.
    It orchestrates persistence (Repository) and business rules (Domain Entity)
    """

    uow: UnitOfWork

    async def execute(self, request_model: CreateUserRequestModel) -> Result:
        """Execute the user creation process."""
        async with self.uow:
            if await self.uow.users.get_by_email(request_model.email):
                return Result.failure(
                    Error.business_rule_violation(
                        message=f"Email already registered: {request_model.email}"
                    )
                )

            # TODO: Hash password before creating entity
            new_user = UserDomain(
                name=request_model.name,
                email=request_model.email,
                password_hash=request_model.password,
                birth_date=request_model.birth_date,
            )

            await self.uow.users.save(new_user)
            return Result.success(UserResponseModel.from_entity(new_user))


@dataclass(frozen=True)
class GetUsersUseCase:
    """User case to get all users"""

    uow: UnitOfWork

    # TODO: Create filter / pagination request models
    async def execute(self) -> Result:
        async with self.uow:
            users = await self.uow.users.get_all()
            return Result.success(
                UsersListResponseModel(
                    users=[UserResponseModel.from_entity(user) for user in users]
                )
            )

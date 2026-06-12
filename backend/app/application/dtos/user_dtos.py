from datetime import date, datetime
from typing import Self

from app.domain.entities.user import UserDomain
from pydantic import BaseModel, EmailStr, Field


class CreateUserRequestModel(BaseModel):
    name: str = Field(min_length=4, max_length=255)
    email: EmailStr
    password: str
    birth_date: date


class UserResponseModel(BaseModel):
    id: str
    name: str = Field(min_length=4, max_length=255)
    email: EmailStr
    birth_date: date
    role: str = Field(default="user")
    created_at: datetime
    updated_at: datetime | None = Field(default=None)

    @classmethod
    def from_entity(cls, user: UserDomain) -> Self:
        """Create response from a User entity."""
        return cls(
            id=str(user.id),
            name=user.name,
            email=user.email,
            birth_date=user.birth_date,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UsersListResponseModel(BaseModel):
    users: list[UserResponseModel]

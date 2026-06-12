from dataclasses import dataclass

from app.application.common.result import Error, Result
from app.application.dtos.auth_dtos import TokenResponseModel
from app.application.dtos.user_dtos import UserResponseModel
from app.application.uow import UnitOfWork
from app.domain.services.password_hasher import PasswordHasher
from app.domain.services.token_service import TokenService

@dataclass(frozen=True)
class AuthenticateUserUseCase:
    uow: UnitOfWork
    password_hasher: PasswordHasher

    async def execute(self, username: str, password: str) -> Result:
        async with self.uow:
            user = await self.uow.users.get_by_email(username)
            if user is None:
                return Result.failure(Error.unauthorized("Invalid credentials"))

            if not self.password_hasher.verify_password(password, user.password_hash):
                return Result.failure(Error.unauthorized("Invalid credentials"))

            if not user.is_active:
                return Result.failure(Error.unauthorized("Account is inactive"))

            return Result.success(UserResponseModel.from_entity(user))


@dataclass(frozen=True)
class CreateAccessTokenUseCase:
    token_service: TokenService

    async def execute(self, subject: str, role: str | None = None) -> Result:
        extra: dict = {}
        if role is not None:
            extra["role"] = role
        token = self.token_service.create_access_token(subject=subject, extra_claims=extra or None)
        return Result.success(TokenResponseModel(access_token=token))


@dataclass(frozen=True)
class GetCurrentUserUseCase:
    uow: UnitOfWork
    token_service: TokenService

    async def execute(self, token: str) -> Result:
        try:
            payload = self.token_service.decode_access_token(token)
        except ValueError as exc:
            return Result.failure(Error.unauthorized(str(exc)))

        email: str = payload["sub"]
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if user is None:
                return Result.failure(Error.unauthorized("User not found"))
            if not user.is_active:
                return Result.failure(Error.unauthorized("Account is inactive"))
            return Result.success(UserResponseModel.from_entity(user))

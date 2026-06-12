from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.application.service_ports.token_service import TokenService
from app.infra.security.auth_settings import AuthSettings


class JwtService(TokenService):
    def __init__(self, auth_settings: AuthSettings) -> None:
        self.auth_settings = auth_settings

    def create_access_token(
        self,
        subject: str,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        to_encode: dict[str, Any] = {"sub": subject}
        if extra_claims:
            to_encode.update(extra_claims)
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.auth_settings.access_token_expire_minutes
        )
        to_encode["exp"] = expire
        return jwt.encode(
            to_encode,
            self.auth_settings.secret_key,
            algorithm=self.auth_settings.algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.auth_settings.secret_key,
                algorithms=[self.auth_settings.algorithm],
            )
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Access token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid access token") from exc

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Access token missing required claim: sub")

        return payload

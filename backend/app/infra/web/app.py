from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infra.config import Config
from app.infra.configuration.container import create_application
from app.infra.security.auth_settings import AuthSettings
from app.infra.security.jwt_service import JwtService
from app.infra.security.password_service import PasswordService
from app.infra.web.routes import auth_routes, user_routes
from app.interfaces.presenters.web.auth_presenter import WebAuthPresenter
from app.interfaces.presenters.web.user_presenter import WebUserPresenter


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_factory = Config.get_session_factory()
    auth_settings = AuthSettings()
    app.state.container = create_application(
        session_factory=session_factory,
        user_presenter=WebUserPresenter(),
        auth_presenter=WebAuthPresenter(),
        token_service=JwtService(auth_settings),
        password_hasher=PasswordService(),
    )

    yield

    await Config.dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Samizdat",
        description="FastAPI with Domain Driven Design",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(user_routes.router)
    app.include_router(auth_routes.router)
    return app

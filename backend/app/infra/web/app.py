from contextlib import asynccontextmanager
from urllib.parse import urlparse

import weaviate
from fastapi import FastAPI

from app.agent.recommender import GraphBookRecommender
from app.infra.agent_settings import AgentSettings
from app.infra.config import Config
from app.infra.configuration.container import create_application
from app.infra.embeddings.openai_embeddings import OpenAIEmbeddingsService
from app.infra.llm.openai_llm import OpenAILLMService
from app.infra.security.auth_settings import AuthSettings
from app.infra.security.jwt_service import JwtService
from app.infra.security.password_service import PasswordService
from app.infra.vector.weaviate_repository import WeaviateBookRepository
from app.infra.web.routes import auth_routes, book_routes, user_routes
from app.interfaces.presenters.web.auth_presenter import WebAuthPresenter
from app.interfaces.presenters.web.book_presenter import WebBookPresenter
from app.interfaces.presenters.web.user_presenter import WebUserPresenter


def _connect_weaviate(url: str) -> "weaviate.WeaviateClient":
    parsed = urlparse(url)
    return weaviate.connect_to_local(
        host=parsed.hostname or "localhost",
        port=parsed.port or 8080,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_factory = Config.get_session_factory()
    auth_settings = AuthSettings()  # type: ignore[call-arg]
    agent_settings = AgentSettings()  # type: ignore[call-arg]

    # Long-lived agent dependencies (bound into the compiled graph for its lifetime).
    llm = OpenAILLMService(
        model=agent_settings.openai_chat_model,
        api_key=agent_settings.openai_api_key,
    )
    embeddings = OpenAIEmbeddingsService(
        model=agent_settings.openai_embedding_model,
        api_key=agent_settings.openai_api_key,
    )
    weaviate_client = _connect_weaviate(agent_settings.weaviate_url)
    vector_repo = WeaviateBookRepository(
        weaviate_client, agent_settings.weaviate_collection
    )
    book_recommender = GraphBookRecommender(llm, embeddings, vector_repo)

    app.state.container = create_application(
        session_factory=session_factory,
        user_presenter=WebUserPresenter(),
        auth_presenter=WebAuthPresenter(),
        book_presenter=WebBookPresenter(),
        token_service=JwtService(auth_settings),
        password_hasher=PasswordService(),
        book_recommender=book_recommender,
    )

    yield

    weaviate_client.close()
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
    app.include_router(book_routes.router)
    return app

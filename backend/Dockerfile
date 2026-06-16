# books-agent backend — FastAPI + LangGraph recommender
# Uses the official uv image so the build matches local `uv sync`.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Install dependencies (cached layer) from the lockfile. The project itself is
# run from the source tree (uvicorn main:app), so it is not installed as a package.
# Dev deps are kept: `alembic` (migrations) and `pandas` (data-prep script) live
# in the dev group and are needed by the one-off setup commands.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy the application source.
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

# Production server (no --reload). Migrations + data load are run as one-off
# `docker compose run` commands — see the README "Run with Docker" section.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

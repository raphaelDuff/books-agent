# books-agent backend

FastAPI + Clean Architecture/DDD backend with a LangGraph recommendation agent.
See the [project README](../README.md) for the full overview and setup.

```bash
uv sync
uv run alembic upgrade head
uv run python scripts/prepare_data.py
uv run uvicorn app.main:app --reload
uv run pytest
```

"""One-off, idempotent data preparation for books-agent.

Pipeline: clean ``books.csv`` -> load PostgreSQL ``books`` table -> embed
descriptions with OpenAI -> (re)create the Weaviate ``Book`` collection and
upsert objects with their vectors.

Run from the ``backend/`` directory:

    uv run python scripts/prepare_data.py

Prerequisites: PostgreSQL migrated (``alembic upgrade head``) and Weaviate up
(``docker compose up -d weaviate`` at the repo root). Re-running replaces all
data (TRUNCATE + collection recreate), so it is safe to repeat.
"""

import asyncio
import math

import pandas as pd
import weaviate
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text
from weaviate.classes.config import Configure, DataType, Property

from app.infra.agent_settings import AgentSettings
from app.infra.config import Config
from app.infra.db.models.book_model import BookSQLModel

load_dotenv()

EMBED_BATCH = 200
WEAVIATE_PROPERTIES = [
    Property(name="isbn13", data_type=DataType.TEXT),
    Property(name="isbn10", data_type=DataType.TEXT),
    Property(name="title", data_type=DataType.TEXT),
    Property(name="subtitle", data_type=DataType.TEXT),
    Property(name="authors", data_type=DataType.TEXT),
    Property(name="categories", data_type=DataType.TEXT),
    Property(name="thumbnail", data_type=DataType.TEXT),
    Property(name="description", data_type=DataType.TEXT),
    Property(name="published_year", data_type=DataType.INT),
    Property(name="average_rating", data_type=DataType.NUMBER),
    Property(name="num_pages", data_type=DataType.INT),
    Property(name="ratings_count", data_type=DataType.INT),
]


def _opt_str(value) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text_value = str(value).strip()
    return text_value or None


def _opt_int(value) -> int | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _opt_float(value) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_clean(csv_path: str) -> list[dict]:
    df = pd.read_csv(csv_path)
    before = len(df)
    df = df.dropna(subset=["description", "authors", "isbn13"])
    df = df[df["description"].astype(str).str.strip() != ""]
    df = df[df["authors"].astype(str).str.strip() != ""]
    print(f"Loaded {before} rows; {len(df)} usable after cleaning.")

    records: list[dict] = []
    for row in df.to_dict(orient="records"):
        records.append(
            {
                "isbn13": str(row["isbn13"]).strip(),
                "isbn10": _opt_str(row.get("isbn10")),
                "title": _opt_str(row.get("title")) or "(untitled)",
                "subtitle": _opt_str(row.get("subtitle")),
                "authors": str(row["authors"]).strip(),
                "categories": _opt_str(row.get("categories")),
                "thumbnail": _opt_str(row.get("thumbnail")),
                "description": str(row["description"]).strip(),
                "published_year": _opt_int(row.get("published_year")),
                "average_rating": _opt_float(row.get("average_rating")),
                "num_pages": _opt_int(row.get("num_pages")),
                "ratings_count": _opt_int(row.get("ratings_count")),
            }
        )
    # Drop duplicate isbn13 keys (keep first) so the PK and Weaviate stay consistent.
    seen: set[str] = set()
    unique: list[dict] = []
    for rec in records:
        if rec["isbn13"] not in seen:
            seen.add(rec["isbn13"])
            unique.append(rec)
    return unique


def embed_descriptions(records: list[dict], settings: AgentSettings) -> list[list[float]]:
    embedder = OpenAIEmbeddings(
        model=settings.openai_embedding_model, api_key=settings.openai_api_key
    )
    vectors: list[list[float]] = []
    for start in range(0, len(records), EMBED_BATCH):
        chunk = records[start : start + EMBED_BATCH]
        texts = [r["description"] for r in chunk]
        vectors.extend(embedder.embed_documents(texts))
        print(f"Embedded {min(start + EMBED_BATCH, len(records))}/{len(records)}")
    return vectors


async def load_postgres(records: list[dict]) -> None:
    session_factory = Config.get_session_factory()
    async with session_factory() as session:
        await session.execute(text("TRUNCATE TABLE books"))
        for rec in records:
            session.add(BookSQLModel(**rec))
        await session.commit()
    await Config.dispose_engine()
    print(f"Inserted {len(records)} rows into PostgreSQL 'books'.")


def load_weaviate(
    records: list[dict], vectors: list[list[float]], settings: AgentSettings
) -> None:
    parsed_port = 8080
    if ":" in settings.weaviate_url.split("//", 1)[-1]:
        parsed_port = int(settings.weaviate_url.rsplit(":", 1)[-1])
    client = weaviate.connect_to_local(port=parsed_port)
    try:
        if client.collections.exists(settings.weaviate_collection):
            client.collections.delete(settings.weaviate_collection)
        client.collections.create(
            name=settings.weaviate_collection,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=WEAVIATE_PROPERTIES,
        )
        collection = client.collections.get(settings.weaviate_collection)
        with collection.batch.dynamic() as batch:
            for rec, vec in zip(records, vectors):
                batch.add_object(properties=rec, vector=vec)
        failed = collection.batch.failed_objects
        if failed:
            print(f"WARNING: {len(failed)} objects failed to insert.")
        print(f"Upserted {len(records)} objects into Weaviate '{settings.weaviate_collection}'.")
    finally:
        client.close()


def main() -> None:
    settings = AgentSettings()
    records = load_clean(settings.books_csv_path)
    vectors = embed_descriptions(records, settings)
    asyncio.run(load_postgres(records))
    load_weaviate(records, vectors, settings)
    print("Data preparation complete.")


if __name__ == "__main__":
    main()

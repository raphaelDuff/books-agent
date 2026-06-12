from typing import Literal, Sequence

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.application.service_ports.llm_service import (
    IntentClassification,
    LLMService,
    RankedPick,
)
from app.domain.entities.book import BookDomain
from app.domain.value_objects import Intent

# The schema the SQL router must target. Kept in the adapter, near the prompt.
BOOKS_SCHEMA = """\
Table "books" (PostgreSQL):
  isbn13 TEXT PRIMARY KEY, isbn10 TEXT, title TEXT, subtitle TEXT,
  authors TEXT (one or more, ';'-separated), categories TEXT,
  thumbnail TEXT, description TEXT, published_year INTEGER,
  average_rating DOUBLE PRECISION (0-5), num_pages INTEGER, ratings_count INTEGER
"""

_CLASSIFY_SYSTEM = f"""You route a natural-language book request.

Decide the intent:
- STRUCTURED: answerable purely by hard filters (year/decade, rating, author, category).
- SEMANTIC: answerable purely by meaning/mood/theme of the description.
- HYBRID: needs BOTH a hard filter AND a meaning-based match.

{BOOKS_SCHEMA}

Rules:
- For STRUCTURED or HYBRID, write ONE read-only PostgreSQL query: `SELECT * FROM books WHERE ...`.
  Use ILIKE '%term%' for authors/categories (they are free text). Decades are ranges
  (e.g. 1990s -> published_year BETWEEN 1990 AND 1999). Never write anything but a single SELECT.
  Do NOT add LIMIT. Leave sql empty/null for SEMANTIC.
- For SEMANTIC or HYBRID, write semantic_query: a concise description of the mood/theme/subject
  to embed for vector search. Leave empty for STRUCTURED.
"""

_REPAIR_SYSTEM = f"""A PostgreSQL SELECT against the books table failed. Return a corrected
single read-only `SELECT * FROM books WHERE ...` query. Output SQL only, no commentary.

{BOOKS_SCHEMA}
"""

_RANK_SYSTEM = """You are a book recommender. Given a user's request and a numbered list of
candidate books, pick the best matches (at most the requested count), most relevant first.
For each pick give a single concise sentence (max ~20 words) on why it fits the request.
Only choose from the provided candidates; reference them by their index."""


class _IntentSchema(BaseModel):
    intent: Literal["STRUCTURED", "SEMANTIC", "HYBRID"]
    sql: str | None = Field(default=None, description="single SELECT, or null")
    semantic_query: str = Field(default="")
    reasoning: str = Field(default="")


class _RepairSchema(BaseModel):
    sql: str = Field(description="corrected single SELECT statement")


class _PickSchema(BaseModel):
    index: int = Field(description="index of the chosen candidate")
    justification: str


class _RankingSchema(BaseModel):
    picks: list[_PickSchema]


def _candidate_block(candidates: Sequence[BookDomain]) -> str:
    lines = []
    for i, b in enumerate(candidates):
        desc = (b.description or "")[:300]
        lines.append(
            f"[{i}] {b.title} — {b.authors} ({b.published_year}); "
            f"rating={b.average_rating}; {desc}"
        )
    return "\n".join(lines)


class OpenAILLMService(LLMService):
    """LLMService backed by OpenAI chat models via langchain-openai.

    All structured output is bound here (``with_structured_output``) so nodes
    never touch LangChain types.
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._chat = ChatOpenAI(model=model, api_key=api_key, temperature=0)

    async def classify(self, question: str) -> IntentClassification:
        structured = self._chat.with_structured_output(_IntentSchema)
        result: _IntentSchema = await structured.ainvoke(
            [
                ("system", _CLASSIFY_SYSTEM),
                ("human", question),
            ]
        )
        sql = (result.sql or "").strip() or None
        return IntentClassification(
            intent=Intent(result.intent),
            semantic_query=result.semantic_query or "",
            sql=sql,
            reasoning=result.reasoning or "",
        )

    async def repair_sql(self, sql: str, error: str) -> str:
        structured = self._chat.with_structured_output(_RepairSchema)
        result: _RepairSchema = await structured.ainvoke(
            [
                ("system", _REPAIR_SYSTEM),
                ("human", f"Failed SQL:\n{sql}\n\nError:\n{error}"),
            ]
        )
        return result.sql.strip()

    async def rank_and_justify(
        self, question: str, candidates: Sequence[BookDomain], limit: int
    ) -> list[RankedPick]:
        if not candidates:
            return []
        structured = self._chat.with_structured_output(_RankingSchema)
        result: _RankingSchema = await structured.ainvoke(
            [
                ("system", _RANK_SYSTEM),
                (
                    "human",
                    f"Request: {question}\n\nReturn at most {limit} picks.\n\n"
                    f"Candidates:\n{_candidate_block(candidates)}",
                ),
            ]
        )
        picks: list[RankedPick] = []
        for p in result.picks[:limit]:
            if 0 <= p.index < len(candidates):
                picks.append(
                    RankedPick(book=candidates[p.index], justification=p.justification)
                )
        return picks

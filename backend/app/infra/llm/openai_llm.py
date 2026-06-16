import logging
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
from app.infra.llm.prompts import PromptLibrary

logger = logging.getLogger(__name__)


# Structured-output schemas. ``reasoning`` is listed FIRST in each so the model
# emits its chain-of-thought before the answer fields — the thinking conditions
# the answer rather than rationalising it after the fact.
class _IntentSchema(BaseModel):
    reasoning: str = Field(default="", description="brief reasoning, written first")
    intent: Literal["STRUCTURED", "SEMANTIC", "HYBRID"]
    sql: str | None = Field(default=None, description="single SELECT, or null")
    semantic_query: str = Field(default="")


class _RepairSchema(BaseModel):
    reasoning: str = Field(default="", description="diagnosis of the failure, first")
    sql: str = Field(description="corrected single SELECT statement")


class _PickSchema(BaseModel):
    index: int = Field(description="index of the chosen candidate")
    justification: str


class _RankingSchema(BaseModel):
    reasoning: str = Field(default="", description="overall comparison, written first")
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
    never touch LangChain types. System prompts are loaded from the versioned
    ``prompts.yaml`` via a :class:`PromptLibrary` (injectable for tests).
    """

    def __init__(
        self, model: str, api_key: str, prompts: PromptLibrary | None = None
    ) -> None:
        self._chat = ChatOpenAI(model=model, api_key=api_key, temperature=0)
        self._prompts = prompts or PromptLibrary.from_yaml()
        logger.info("Loaded prompt versions: %s", self._prompts.versions())

    async def classify(self, question: str) -> IntentClassification:
        structured = self._chat.with_structured_output(_IntentSchema)
        result: _IntentSchema = await structured.ainvoke(
            [
                ("system", self._prompts.system("classify_intent")),
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
                ("system", self._prompts.system("repair_sql")),
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
                ("system", self._prompts.system("rank")),
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

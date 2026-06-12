# PROJECT BRIEF — books-agent

## Context

This is a take-home technical challenge for an AI Engineer interview: build a small
full-stack app that uses AI in a meaningful way. Time budget is 6–8 hours; the bar is quality
and clarity, not completeness. Evaluation criteria: problem-solving approach, full-stack
fundamentals, thoughtful use of AI, code quality and structure, ability to explain decisions,
and product/UX thinking. Deliverables: a (recorded) demo, a GitHub repo, and a README covering
overview, tech stack, how AI is used, setup, and trade-offs.

## Product

"Talk to your books" — a natural-language book recommender. The user asks in plain
language (e.g. "90s books about car chases", "something melancholic about memory and loss",
"sci-fi with a strong female lead") and gets a short ranked list with a one-line justification
per pick.

## Why the AI is Meaningful (not a thin wrapper)

Two retrieval modes are combined:
- **Structured filtering** (genre/category, author, year, rating) → SQL over DuckDB.
- **Semantic search** over book descriptions → vector similarity in Weaviate.

An LLM router node (`classify_intent`) decides `STRUCTURED` / `SEMANTIC` / `HYBRID`, and via
structured output extracts the filters plus a rewritten semantic query. `HYBRID` runs both
searches in parallel, merges them, and an LLM reranks and justifies the picks. The point: pure
SQL cannot answer "melancholic about memory", and pure embeddings lose exact filters like decade
or rating — the hybrid is the whole value proposition. The orchestration is a LangGraph graph.

## Dataset

Kaggle "7k-books-with-metadata" (Dylan Castillo), ~6,810 rows. Columns: `isbn13`, `isbn10`,
`title`, `subtitle`, `authors`, `categories`, `thumbnail`, `description`, `published_year`,
`average_rating`, `num_pages`, `ratings_count`. Decisions: there is NO country-of-origin field
(dropped from scope); `description` is used as the synopsis; data prep filters out ~260 rows
with no description and ~70 with no authors.

## Tech Stack

- **Backend:** Python 3.13, FastAPI, Clean Architecture / DDD (the existing `samizdat` template
  under `backend/app`), LangGraph for the agent, DuckDB (structured), Weaviate (semantic),
  an LLM provider (Anthropic), `uv` for dependencies. Optional LangSmith tracing.
- **Frontend:** React, clean minimal UI. The dataset is fixed (no upload): a query box plus
  results showing cover (thumbnail), title, author, and the why-recommended line. Show the
  generated SQL for transparency.
- **Persistence:** read-only over the prepared dataset. Auth is out of scope (optional nice-to-have).

## Architecture Decisions

- **Dependency rule, inward only:** `domain` ← `application` ← `infra`/`interfaces`.
- Capability ports (`LLMService`, embeddings) live in `application/service_ports/`; data-access
  ports (`BookRepository`) in `application/repositories/`; concrete adapters in `infra/<concern>/`
  (`infra/llm/`, `infra/persistence/`).
- LangGraph package in `backend/app/agent/`; nodes depend only on interfaces, with concrete
  dependencies injected via `RunnableConfig` at the composition root (the lifespan in
  `infra/web/app.py`). `langgraph.json` is optional (only for LangGraph Platform deploy).
- `Intent` is a `StrEnum` value object in `domain/value_objects.py`. The use case
  `AnswerBookQuestionUseCase` returns the project's `Result` type.

## Scope Guardrails (protect the 6–8h budget)

- **MUST:** question → `classify_intent` → SQL / semantic / hybrid → merge → LLM rank+justify
  → results in the UI; show the generated SQL; basic error handling (one SQL retry on failure).
- **NICE** (only if time remains): auto-selected chart, follow-up/conversation memory, a light
  semantic cache, deployment, a few node tests.
- **CUT:** multi-user persistent DB, file upload, anything outside the vertical slice above.

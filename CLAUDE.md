# books-agent — project rules

See [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) for full context (read it before planning new features).

## Architecture (non-negotiable)

- **Dependency rule, inward only:** `domain` ← `application` ← `infra`/`interfaces`.
- Capability ports (`LLMService`, embeddings) in `application/service_ports/`; data-access ports (`BookRepository`) in `application/repositories/`; adapters in `infra/<concern>/`.
- LangGraph package in `backend/app/agent/`; nodes depend on interfaces only; deps injected via `RunnableConfig` at the composition root (`infra/web/app.py` lifespan).
- Service ports are ABCs in `application/service_ports/`; never in `domain/`.

## Scope

- **MUST:** question → `classify_intent` → SQL / semantic / hybrid → merge → LLM rank+justify → results in UI; show generated SQL; one SQL retry on failure.
- **NICE** (only if time permits): chart, conversation memory, semantic cache, deployment, node tests.
- **CUT:** multi-user persistent DB, file upload, anything outside the vertical slice.

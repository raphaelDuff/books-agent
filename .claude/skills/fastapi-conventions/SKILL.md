---
name: fastapi-conventions
description: >-
  Use for any code under backend/app following Clean Architecture and DDD
  patterns — FastAPI routes, controllers, use cases, DTOs, repositories,
  domain entities, UoW, presenters, or DI wiring. Triggers on "add endpoint",
  "create use case", "new entity", "add repository method".
---

# FastAPI Conventions — Samizdat Backend

This project is a FastAPI backend built with **Clean Architecture / DDD**. The
dependency rule is strict: dependencies point **inward only**
(`infra`/`interfaces` → `application` → `domain`). The domain knows nothing about
FastAPI, SQLModel, or Pydantic DTOs; the application layer knows nothing about
FastAPI or the database.

Everything below is documented from the actual code in `backend/app`. Where the
code has open `# TODO`s, the preferred pattern to standardize on is called out explicitly.

## Project Structure

All application code lives under `backend/app`. Layers, from innermost to outermost:

| Folder | Architectural role |
| --- | --- |
| `domain/entities/` | Pure domain entities as `@dataclass` (`Entity` base with `id: UUID`, `UserDomain`). No framework imports. Business-derived properties live here (e.g. `UserDomain.age`). |
| `domain/value_objects.py` | Enums and immutable value objects (`UserRole` StrEnum, `Email` frozen dataclass). Entities use these as field types instead of raw primitives. |
| `domain/exceptions.py` | Domain exception hierarchy. `DomainError` base + specific errors (`UserIdNotFoundError`). |
| `application/service_ports/` | Abstract port interfaces for external capabilities needed by use cases (`PasswordHasher`, `TokenService` ABCs). Implementations live under `infra/` in a subfolder matching their concern (e.g. `infra/security/`, `infra/llm/`, `infra/email/`). |
| `application/use_cases/` | Use cases — one orchestration class per operation. Hold business flow; call repositories via the UoW. |
| `application/dtos/` | Pydantic request/response models that cross the application boundary (`CreateUserRequestModel`, `UserResponseModel`). |
| `application/repositories/` | Abstract repository **interfaces** (`UserRepository` ABC). The application depends on these, not on implementations. |
| `application/uow.py` | `UnitOfWork` `Protocol` — transactional boundary exposing repositories (`uow.users`). |
| `application/common/result.py` | `Result[T]` / `Error` / `ErrorCode` — the typed success-or-failure return for use cases. |
| `interfaces/controllers/` | Framework-independent controllers. Orchestrate use case + presenter; convert `Result` → `OperationResult` view-model result. |
| `interfaces/presenters/` | `UserPresenter` ABC (`base.py`) + web implementation (`web/user_presenter.py`). Maps response DTOs → view models. |
| `interfaces/view_models/` | View models for output (`UserViewModel` dataclass) and `OperationResult` / `ErrorViewModel` (`base.py`). |
| `infra/web/` | FastAPI layer: `app.py` (app factory + lifespan/composition root), `routes/` (`APIRouter`s), `dependencies.py` (DI graph), `error_mapping.py` (`ErrorCode` → HTTP status). |
| `infra/configuration/container.py` | `Application` container + `create_application()` factory holding `uow_factory` and presenters. |
| `infra/persistence/` | Concrete repository implementations (`UserPostgreRepository`). |
| `infra/db/models/` | SQLModel table models (`UserSQLModel`). Separate from domain entities. |
| `infra/db/mappers/` | Static mappers between domain entities and SQLModel models (`UserMapper.to_domain` / `to_model`). |
| `infra/uow.py` | `SqlAlchemyUnitOfWork` — concrete UoW implementing the protocol. |
| `infra/security/` | JWT (`JwtService`), password hashing (`PasswordService`), `AuthSettings` (pydantic-settings). |
| `infra/config.py` | `Config` — engine/session factory singletons, env-driven repository type and DB URL. |
| `migrations/` | Alembic migrations (`alembic.ini` at `backend/`). |
| `main.py` | Entrypoint: `load_dotenv()` then `create_app()`; `uvicorn.run` under `__main__`. |

## Conventions

### Naming
- Domain entities are suffixed `Domain` (`UserDomain`); SQLModel tables suffixed `SQLModel` (`UserSQLModel`); view models suffixed `ViewModel`; presenters `Presenter`.
- Request/response DTOs use the `...RequestModel` / `...ResponseModel` suffix.
- Use cases are named `<Verb><Noun>UseCase` (`CreateUserUseCase`, `GetUsersUseCase`).
- Repository interfaces are `<Entity>Repository`; implementations encode the backend, `<Entity><Backend>Repository` (`UserPostgreRepository`).
- DI provider functions in `infra/web/dependencies.py` are `get_<thing>`.

### Async
- Everything on the request path is `async`: route handlers, controller methods, use case `execute`, and all repository methods. `await` repository calls inside use cases.
- DB access uses SQLModel's `AsyncSession`; queries use `select(...)` + `await session.exec(stmt)` then `.one_or_none()` / `.all()` / `await session.get(Model, id)`.

### How routers call services (controllers)
- Routers live in `infra/web/routes/*.py`, each its own `APIRouter(prefix=..., tags=[...])`, registered in `app.py` via `app.include_router(...)`.
- A handler **only**: declares its Pydantic request model + a `Depends`-injected controller, calls a single `controller.handle_*` method, then translates the returned `OperationResult` into either the response model or an `HTTPException`.
- Error translation in the router: map the application `ErrorCode` to an HTTP status via `get_http_status(ErrorCode[error.code])` and raise `HTTPException(status_code=..., detail={"message": ..., "code": ...})`.
- `response_model`, `status_code`, and `responses={...}` (with `ErrorViewModel`) are declared on the decorator.

### How controllers call use cases
- Controllers are `@dataclass`es whose fields are the use case(s) + presenter, all injected.
- They build the request DTO, `await use_case.execute(request)`, inspect `result.is_success`, then use the **presenter** to produce a view model (`present_user`) or error (`present_error`), wrapping the outcome in `OperationResult.succeed(...)` / `OperationResult.fail(...)`.
- Controllers catch `ValueError` (e.g. Pydantic validation) and convert it to a failed `OperationResult` with code `"VALIDATION_ERROR"`. They never raise `HTTPException` — that is the router's job.

### How use cases call repositories
- Use cases are `@dataclass(frozen=True)` holding a `uow: UnitOfWork`.
- They open the transaction with `async with self.uow:` and access repositories as attributes (`self.uow.users`). Commit/rollback is automatic on context exit (`SqlAlchemyUnitOfWork.__aexit__` commits on success, rolls back on exception).
- Business rules return `Result.failure(Error.business_rule_violation(...))`; success returns `Result` wrapping a response DTO built via `ResponseModel.from_entity(entity)`.

### Where validation lives
- **Input shape/format validation:** Pydantic DTOs in `application/dtos` (`Field(min_length=...)`, `EmailStr`, etc.).
- **Business-rule validation:** inside the use case (e.g. duplicate-email check via `uow.users.get_by_email`), returned as a `Result` failure — never raised as HTTP errors from the use case.
- **Persistence-layer existence checks:** raise domain exceptions (`UserIdNotFoundError`) or use `guard_not_none(...)` from `app.infra.guards`.

### Dependency injection
- DI is **plain FastAPI `Depends`**, no third-party container library. The graph is wired explicitly as chained `get_*` functions in `infra/web/dependencies.py`.
- The composition root is the `lifespan` in `infra/web/app.py`: it builds the `Application` container via `create_application(...)`, choosing concrete implementations (e.g. `WebUserPresenter()`), and attaches it to `app.state.container`.
- `get_container` reads `request.app.state.container`; downstream providers pull factories/singletons off it (`get_uow_factory`, `get_user_presenter`).
- **Request scoping:** each request gets a *fresh* UoW (`uow_factory()`), a fresh use case, and a fresh controller. Repository implementation selection is config-driven through `repository_factory.create_repositories()` + `REPO_MAP`.

### Mapping & persistence
- Domain entities and SQLModel models are distinct; convert only through `infra/db/mappers` (`UserMapper.to_domain` / `to_model`). Never leak `*SQLModel` types out of `infra/persistence`, and never persist `*Domain` entities directly.
- `save()` only `session.add(...)`; the actual `commit()` is owned by the UoW, not the repository.

### Error/result model (two layers, by design)
- **Application layer:** `Result[T]` + `Error(code: ErrorCode, message, details)` with factory helpers (`Error.not_found`, `Error.validation_error`, `Error.business_rule_violation`).
- **Interface layer:** `OperationResult[T]` + `ErrorViewModel(message, code)`.
- **Web layer:** `ErrorCode` → HTTP status in `error_mapping.ERROR_CODE_TO_HTTP`, surfaced as `HTTPException`.
- Note: `Result` currently exposes the success factory as the misspelled `Result.sucess(...)`. Existing code calls it that way — match the existing method name when calling, but prefer fixing the typo to `success` if you touch `result.py` (update all call sites together).

## Rules

When generating or editing code under `backend/app`, you MUST:

1. **Respect the dependency rule.** Never import FastAPI, SQLModel, SQLAlchemy, or Pydantic DTOs into `domain/`. Never import FastAPI or `infra` into `application/`. Dependencies point inward only.
2. **No business logic in routers.** A route handler validates input via its DTO, calls exactly one `controller.handle_*`, and translates `OperationResult` → response/`HTTPException`. Nothing else.
3. **Routers are the only place that raises `HTTPException`.** Controllers and use cases return `OperationResult` / `Result`; they never touch HTTP.
4. **Always inject via `Depends()`.** Add new dependencies as `get_*` functions in `infra/web/dependencies.py` and chain them; choose concrete implementations only at the composition root (`app.py` lifespan). Do not instantiate repositories, use cases, sessions, or presenters directly inside handlers, controllers, or use cases.
5. **Use cases own the transaction.** Access the DB only through `async with self.uow:` and `self.uow.<repo>`. Do not open sessions or commit/rollback manually inside a use case or repository — the UoW does it.
6. **Return typed results, not exceptions, for expected failures.** Use `Result.failure(Error.*(...))` in use cases for business-rule/validation failures. Reserve raised exceptions for truly exceptional/persistence cases (domain exceptions, `guard_not_none`).
7. **Keep domain entities and DB models separate.** Convert exclusively through the mappers in `infra/db/mappers`. Never return `*SQLModel` from the application/interface layers, and never hand a `*Domain` entity to the ORM directly.
8. **Map errors to HTTP through `error_mapping`.** Add new statuses to `ERROR_CODE_TO_HTTP` / `ErrorCode` rather than hard-coding status codes in handlers.
9. **Validate input in DTOs, business rules in use cases.** Put `Field`/`EmailStr` constraints on Pydantic DTOs; put rule checks (uniqueness, state) in the use case.
10. **Each request gets fresh request-scoped objects.** Build use cases/controllers with a fresh UoW per request via the factory — never cache a UoW, session, use case, or controller across requests.
11. **Match the naming suffixes** (`...Domain`, `...SQLModel`, `...ViewModel`, `...RequestModel`/`...ResponseModel`, `...UseCase`, `...Repository`, `get_*` providers).
12. **Register new routers** in `create_app()` (`app.include_router(...)`) and new repositories in `REPO_MAP`.
13. **Service ports belong in `application/service_ports/`**, not in `domain/`. When adding a new external capability (LLM, email, storage), define its ABC there and put the concrete implementation under the appropriate `infra/<concern>/` subfolder. Inject via `Depends` the same way as `PasswordHasher`/`TokenService`.

## Examples

### Endpoint (from `infra/web/routes/user_routes.py`)

```python
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserViewModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorViewModel, "description": "Validation error"},
        409: {"model": ErrorViewModel, "description": "Email already registered"},
    },
)
async def create_user(
    request: CreateUserRequestModel,
    controller: Annotated[UserController, Depends(get_user_controller)],
) -> UserViewModel:
    """Create a new user."""
    result = await controller.handle_create(
        name=request.name,
        email=request.email,
        password=request.password,
        birth_date=request.birth_date,
    )

    if not result.is_success:
        error = result.error
        status_code = (
            get_http_status(ErrorCode[error.code])
            if error.code
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail={"message": error.message, "code": error.code},
        )

    return result.success
```

### Use case (from `application/use_cases/user_use_cases.py`)

```python
@dataclass(frozen=True)
class CreateUserUseCase:
    """Orchestrates persistence (Repository) and business rules (Domain Entity)."""

    uow: UnitOfWork

    async def execute(self, request_model: CreateUserRequestModel) -> Result:
        async with self.uow:
            if await self.uow.users.get_by_email(request_model.email):
                return Result.failure(
                    Error.business_rule_violation(
                        message=f"Email already registered: {request_model.email}"
                    )
                )

            new_user = UserDomain(
                name=request_model.name,
                email=request_model.email,
                password_hash=request_model.password,  # TODO: hash before persisting
                birth_date=request_model.birth_date,
            )

            await self.uow.users.save(new_user)
            return Result.sucess(UserResponseModel.from_entity(new_user))
```

### DI provider chain (from `infra/web/dependencies.py`)

```python
def get_uow_factory(container: Application = Depends(get_container)) -> Callable[[], UnitOfWork]:
    return container.uow_factory


def get_create_user_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> CreateUserUseCase:
    # Fresh UoW per request → transaction isolation
    return CreateUserUseCase(uow=uow_factory())


def get_user_controller(
    create_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    presenter: UserPresenter = Depends(get_user_presenter),
) -> UserController:
    return UserController(create_use_case=create_use_case, presenter=presenter)
```

## Known inconsistencies / open TODOs

- There are **no project tests yet** (only `.venv` library tests). When adding tests, the architecture is built for it: inject a fake `UnitOfWork`/repository into use cases and a fake use case/presenter into controllers — no FastAPI or DB needed for unit tests.

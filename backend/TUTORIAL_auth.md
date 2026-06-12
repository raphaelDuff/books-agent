# JWT Auth Implementation Tutorial (Your Project Order)

This guide follows the FastAPI OAuth2 + JWT tutorial, adapted to your architecture (`domain` / `application` / `infra` / `interfaces`).

Base reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#about-jwt

## 1. Confirm runtime dependencies
You already installed runtime deps (`pyjwt`, `pwdlib[argon2]`), which is correct.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#install-pwdlib
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#install-pyjwt

Files:
- `pyproject.toml`

## 2. Define auth environment settings
Create JWT settings loader first, because other modules depend on it.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens

Implement in:
- `app/infra/security/auth_settings.py`
- `.env` (add `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- `.env.example` (mirror required keys)

## 3. Implement password hashing service
Use Argon2 via `pwdlib`.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#password-hashing

Implement in:
- `app/infra/security/password_service.py`
- Optional interface usage: `app/domain/services/password_hasher.py`

## 4. Implement JWT service
Create and decode access tokens with `sub` and `exp`.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#technical-details-about-the-jwt-subject-sub

Implement in:
- `app/infra/security/jwt_service.py`

## 5. Define auth DTOs and response contract
Keep API responses aligned with tutorial (`access_token`, `token_type`).

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#return-the-token

Implement in:
- `app/application/dtos/auth_dtos.py`
- `app/interfaces/view_models/auth_vm.py`

## 6. Implement authentication use cases
Split responsibilities:
- authenticate credentials
- create token

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#authenticate-user
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens

Implement in:
- `app/application/use_cases/auth_use_cases.py`

Also update user registration to hash password instead of storing plain password:
- `app/application/use_cases/user_use_cases.py`

## 7. Implement controller orchestration
Controller should call use cases and return your operation result/view model pattern.

Implement in:
- `app/interfaces/controllers/auth_controller.py`

## 8. Add FastAPI auth dependencies
Add:
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")`
- dependency to decode token and load current user
- dependency to check active user

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#oauth2passwordbearer
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#get-the-current-user
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#get-the-current-active-user

Implement in:
- `app/infra/web/dependencies.py`

## 9. Implement auth routes
Add token endpoint and current-user endpoint.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#the-password-flow
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#use-the-form-data
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#return-the-token
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#check-it

Implement in:
- `app/infra/web/routes/auth_routes.py`

Expected endpoints:
- `POST /auth/token`
- `GET /auth/me`

## 10. Wire modules in container and app
Register and expose auth services/use cases via DI and include the auth router.

Implement in:
- `app/infra/configuration/container.py`
- `app/infra/web/dependencies.py` (add provider functions)
- `app/infra/web/app.py` (include `auth_routes.router`)

## 11. Optional DB/domain adjustments
Ensure your user state supports auth rules:
- `is_active` behavior
- optional roles/scopes claims

Related files:
- `app/domain/entities/user.py`
- `app/infra/db/models/user_model.py`
- `migrations/versions/*.py` (if schema change needed)

## 12. Validate manually in Swagger and curl
Run app:
- `uvicorn main:app --reload`

Manual checks:
1. Create user (`POST /users/`).
2. Login (`POST /auth/token`) using form fields (`username`, `password`).
3. Authorize in Swagger with bearer token.
4. Call `GET /auth/me`.

Reference:
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#check-it

## Implementation order summary
1. `auth_settings.py`
2. `password_service.py`
3. `jwt_service.py`
4. `auth_dtos.py` + `auth_vm.py`
5. `auth_use_cases.py`
6. update `user_use_cases.py` password hashing
7. `auth_controller.py`
8. `dependencies.py` auth dependencies
9. `auth_routes.py`
10. container + app wiring

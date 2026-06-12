from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.application.common.result import ErrorCode
from app.infra.web.dependencies import get_auth_controller
from app.infra.web.error_mapping import get_http_status
from app.interfaces.controllers.auth_controller import AuthController
from app.interfaces.view_models.auth_vm import TokenViewModel
from app.interfaces.view_models.base import ErrorViewModel
from app.interfaces.view_models.user_vm import UserViewModel

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post(
    "/token",
    response_model=TokenViewModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorViewModel, "description": "Invalid credentials"},
    },
)
async def issue_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> TokenViewModel:
    """Issue a JWT access token for valid credentials."""
    result = await controller.handle_token(form_data.username, form_data.password)

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


@router.get(
    "/me",
    response_model=UserViewModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorViewModel, "description": "Invalid or expired token"},
    },
)
async def read_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    controller: Annotated[AuthController, Depends(get_auth_controller)],
) -> UserViewModel:
    """Return the currently authenticated user."""
    result = await controller.handle_current_user(token)

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

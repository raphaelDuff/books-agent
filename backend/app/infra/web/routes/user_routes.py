from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.common.result import ErrorCode
from app.application.dtos.user_dtos import CreateUserRequestModel
from app.infra.web.dependencies import get_user_controller
from app.infra.web.error_mapping import get_http_status
from app.interfaces.controllers.user_controller import UserController
from app.interfaces.view_models.base import ErrorViewModel
from app.interfaces.view_models.user_vm import UserViewModel

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

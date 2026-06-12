from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.common.result import ErrorCode
from app.application.dtos.book_dtos import BookQueryRequestModel
from app.infra.web.dependencies import get_book_controller
from app.infra.web.error_mapping import get_http_status
from app.interfaces.controllers.book_controller import BookController
from app.interfaces.view_models.base import ErrorViewModel
from app.interfaces.view_models.book_vm import BookRecommendationViewModel

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/recommendations",
    response_model=BookRecommendationViewModel,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorViewModel, "description": "Validation error"},
    },
)
async def recommend_books(
    request: BookQueryRequestModel,
    controller: Annotated[BookController, Depends(get_book_controller)],
) -> BookRecommendationViewModel:
    """Answer a natural-language book question with a short ranked list."""
    result = await controller.handle_recommend(
        question=request.question,
        thread_id=request.thread_id,
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

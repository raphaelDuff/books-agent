from dataclasses import dataclass
from uuid import uuid4

from app.application.use_cases.book_use_cases import AnswerBookQuestionUseCase
from app.interfaces.presenters.book_presenter import BookPresenter
from app.interfaces.view_models.base import OperationResult
from app.interfaces.view_models.book_vm import BookRecommendationViewModel


@dataclass
class BookController:
    """Controller for book-recommendation operations."""

    answer_use_case: AnswerBookQuestionUseCase
    presenter: BookPresenter

    async def handle_recommend(
        self, question: str, thread_id: str | None = None
    ) -> OperationResult[BookRecommendationViewModel]:
        try:
            thread = thread_id or str(uuid4())
            result = await self.answer_use_case.execute(question, thread)
            if result.is_success:
                view_model = self.presenter.present_recommendation(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

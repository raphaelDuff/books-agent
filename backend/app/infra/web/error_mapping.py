from fastapi import status

from app.application.common.result import ErrorCode

ERROR_CODE_TO_HTTP: dict[ErrorCode, int] = {
    ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.BUSINESS_RULE_VIOLATION: status.HTTP_409_CONFLICT,
    ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
}


def get_http_status(error_code: ErrorCode) -> int:
    """Map application ErrorCode to HTTP status code."""
    return ERROR_CODE_TO_HTTP.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

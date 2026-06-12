from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Generic, Optional, Self, TypeVar

T = TypeVar("T")


class ErrorCode(StrEnum):
    """Enum of possible error codes in the application layer."""

    NOT_FOUND = auto()
    VALIDATION_ERROR = auto()
    BUSINESS_RULE_VIOLATION = auto()
    UNAUTHORIZED = auto()
    CONFLICT = auto()


@dataclass(frozen=True)
class Error:
    """
    Represents an error that occurred during use case execution

    This class provides a standardized way to represent errors across the application layer.
    including the specific type of error (via ErrorCode) and any additional context.

    Attributes:
        code: The type of error that occurred
        message: A human-readable description of the error
        details: Optional additional context about the error
    """

    code: ErrorCode
    message: str
    details: Optional[dict[str, Any]] = None

    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        """Create a NOT_FOUND error for a specific entity"""
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"{entity} with id {entity_id} not found",
        )

    @classmethod
    def validation_error(cls, message: str) -> Self:
        """Create a VALIDATION_ERROR with the specified message."""
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)

    @classmethod
    def business_rule_violation(cls, message: str) -> Self:
        """Create a BUSINESS_RULE_VIOLATION error with the specified message."""
        return cls(code=ErrorCode.BUSINESS_RULE_VIOLATION, message=message)

    @classmethod
    def unauthorized(cls, message: str) -> Self:
        return cls(code=ErrorCode.UNAUTHORIZED, message=message)

    @classmethod
    def conflict(cls, message: str) -> Self:
        return cls(code=ErrorCode.CONFLICT, message=message)


@dataclass(frozen=True)
class Result(Generic[T]):
    """
    Represents the outcome of a use case execution as an Either Type

    This class encapsulates the result of an operation, which can either be a success
    containing a value of type T, or a failure containing an Error. It enforces that
    only one of these states can exist at a time, providing a clear and type-safe way
    to handle operation results.

    Attributes
        _value: The success value of the operation, if successful.
        _error: The error information, if the operation failed.

    Methods:
        is_success: Returns True if the result is a success, False if it is a failure.
        value: Returns the success value if the result is a success, raises ValueError otherwise.
        error: Returns the error if the result is a failure, raises ValueError otherwise.
        success: Class method to create a successful result.
        failure: Class method to create a failure result.
    """

    _value: Optional[T] = None
    _error: Optional[Error] = None

    def __post_init__(self):
        if (self._value is None and self._error is None) or (
            self._value is not None and self._error is not None
        ):
            raise ValueError("Either value or error must be provided, but not both")

    @property
    def is_success(self) -> bool:
        """Check if the result represents a successful operation."""
        return self._value is not None

    @property
    def value(self) -> T:
        """Get the success value. Raises ValueError if result is an error."""
        if self._value is None:
            raise ValueError("Cannot access value on error result")
        return self._value

    @property
    def error(self) -> Error:
        if self._error is None:
            raise ValueError("Cannot access error on success result")
        return self._error

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        """Create a successful result with the given value"""
        return cls(_value=value)

    @classmethod
    def failure(cls, error: Error) -> "Result[T]":
        """Create a failed result with the given error"""
        return cls(_error=error)

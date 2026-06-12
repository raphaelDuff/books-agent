"""
Utility functions for type guards and runtime checks.
"""

from typing import TypeVar

T = TypeVar("T")


def guard_not_none(value: T | None, message: str = "Value cannot be None") -> T:
    """
    Type guard that ensures a value is not None.

    This is useful for narrowing types when you know a value has been
    initialized but the type system doesn't guarantee it.

    Args:
        value: The value to check
        message: Error message if value is None

    Returns:
        The value with type narrowed to T (non-None)

    Raises:
        ValueError: If value is None

    Example:
        >>> optional_value: str | None = get_value()
        >>> actual_value: str = guard_not_none(optional_value)
    """
    if value is None:
        raise ValueError(message)
    return value

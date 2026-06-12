from dataclasses import dataclass


@dataclass(frozen=True)
class UserViewModel:
    """View-specific representation of a user."""

    id: str
    name: str
    email: str
    birth_date: str
    role: str

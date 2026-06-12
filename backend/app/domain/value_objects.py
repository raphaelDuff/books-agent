from dataclasses import dataclass
from enum import StrEnum, auto


class UserRole(StrEnum):
    USER = auto()
    ADMIN = auto()


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value or "." not in self.value.split("@")[-1]:
            raise ValueError(f"Invalid email address: {self.value!r}")

    def __str__(self) -> str:
        return self.value

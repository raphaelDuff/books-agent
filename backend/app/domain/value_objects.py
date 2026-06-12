from dataclasses import dataclass
from enum import StrEnum, auto


class UserRole(StrEnum):
    USER = auto()
    ADMIN = auto()


class Intent(StrEnum):
    """How a book question should be answered.

    STRUCTURED → SQL filter only; SEMANTIC → vector search only;
    HYBRID → SQL filter narrows the candidate set, semantic search ranks within it.
    """

    STRUCTURED = "STRUCTURED"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value or "." not in self.value.split("@")[-1]:
            raise ValueError(f"Invalid email address: {self.value!r}")

    def __str__(self) -> str:
        return self.value

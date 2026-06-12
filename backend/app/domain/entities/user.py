from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.domain.entities.entity import Entity
from app.domain.value_objects import Email, UserRole


@dataclass
class UserDomain(Entity):
    name: str
    email: Email
    password_hash: str
    birth_date: date
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = field(default=None)

    @property
    def age(self) -> int:
        date_today = date.today()
        return (
            date_today.year
            - self.birth_date.year
            - (
                (date_today.month, date_today.day)
                < (self.birth_date.month, self.birth_date.day)
            )
        )

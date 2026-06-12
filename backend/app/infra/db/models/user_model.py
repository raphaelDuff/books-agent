from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, date, timezone

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Column


class UserSQLModel(SQLModel, table=True):
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str

    birth_date: date

    is_active: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

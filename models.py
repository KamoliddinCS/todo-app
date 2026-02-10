from __future__ import annotations

from datetime import datetime
from enum import Enum

from init_db import db
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Priority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    avatar: Mapped[str] = mapped_column(default="default.png")

    def set_password(self, raw_password: str) -> None:
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(10),
        default=TaskStatus.TODO.value,
        nullable=False,
        index=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=Priority.MEDIUM.value,
        nullable=False,
        index=True,
    )

    due_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    owner: Mapped["User"] = relationship(back_populates="tasks")
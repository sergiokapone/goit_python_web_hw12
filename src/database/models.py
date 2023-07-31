"""
models.py

This module defines the SQLAlchemy ORM models for the contacts and users tables.
"""

from datetime import datetime


from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Date,
    func,
    DateTime,
    MetaData,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Contact(Base):
    """
    Represents a contact in the contacts table.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    birthday: Mapped[datetime] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="contacts", lazy=True)


class User(Base):
    """
    Represents a user in the users table.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", default=func.now(), nullable=True
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(default=False)
    contacts: Mapped["Contact"] = relationship("Contact", back_populates="user")
    reset_token: Mapped[str] = mapped_column(String(255), nullable=True)

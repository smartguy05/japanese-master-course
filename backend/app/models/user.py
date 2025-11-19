"""
User model for authentication and user management.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """
    User model representing a learner in the system.

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        native_language: User's native language code (default: 'en')
        target_proficiency: Target JLPT level (default: 'N3')
        created_at: Account creation timestamp
        last_login: Last login timestamp
        is_active: Account active status (default: True)
        preferences: User preferences stored as JSONB
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Profile Information
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    native_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    target_proficiency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="N3",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Preferences (JSONB for flexible storage)
    preferences: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Relationships
    progress: Mapped[Optional["UserProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    flashcards: Mapped[list["Flashcard"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    conversation_sessions: Mapped[list["ConversationSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    review_history: Mapped[list["ReviewHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lesson_progress: Mapped[list["LessonProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"

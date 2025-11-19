"""
LessonProgress model for tracking user progress on lessons.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LessonProgress(Base):
    """
    User progress tracking for individual lessons.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        lesson_id: Foreign key to Lesson
        is_completed: Whether the lesson is completed
        score: Score achieved (0-100)
        time_spent: Time spent in seconds
        completed_exercises: Number of exercises completed
        total_exercises: Total number of exercises
        first_completed_at: Timestamp of first completion
        last_accessed_at: Timestamp of last access
    """

    __tablename__ = "lesson_progress"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Progress Tracking
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    time_spent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    completed_exercises: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_exercises: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timestamps
    first_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="lesson_progress")
    lesson: Mapped["Lesson"] = relationship(back_populates="progress_records")

    def __repr__(self) -> str:
        """String representation of LessonProgress."""
        return f"<LessonProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.is_completed})>"

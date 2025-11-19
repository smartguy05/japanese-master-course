"""
UserProgress model for tracking learning progress.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProgress(Base):
    """
    User progress tracking model.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        current_level: Current JLPT level (N5, N4, N3, N2, N1)
        total_study_time: Total study time in minutes
        current_streak: Current consecutive study days
        longest_streak: Longest consecutive study days achieved
        last_study_date: Date of last study session
        xp_points: Experience points earned
    """

    __tablename__ = "user_progress"

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
        unique=True,  # One-to-one relationship
        index=True,
    )

    # Progress Tracking
    current_level: Mapped[str] = mapped_column(
        nullable=False,
        default="N5",
    )
    total_study_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    last_study_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    xp_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timestamps
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
    user: Mapped["User"] = relationship(back_populates="progress")

    def __repr__(self) -> str:
        """String representation of UserProgress."""
        return f"<UserProgress(user_id={self.user_id}, level='{self.current_level}', xp={self.xp_points})>"

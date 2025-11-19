"""
Flashcard model for spaced repetition system (SRS).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Flashcard(Base):
    """
    Flashcard model for SRS (Spaced Repetition System).

    Implements the SM-2 algorithm for optimal review scheduling.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        content_type: Type of content (kanji, vocabulary, grammar)
        content_id: ID of the content item
        ease_factor: SM-2 ease factor (default: 2.50)
        interval_days: Current interval between reviews (default: 0)
        repetitions: Number of successful repetitions (default: 0)
        last_reviewed: Timestamp of last review
        next_review: Timestamp of next scheduled review
        correct_count: Total number of correct answers
        incorrect_count: Total number of incorrect answers
    """

    __tablename__ = "flashcards"

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

    # Content Reference
    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # SRS Algorithm Fields (SM-2)
    ease_factor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2.50,
    )
    interval_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    repetitions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Review Timestamps
    last_reviewed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_review: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Statistics
    correct_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    incorrect_count: Mapped[int] = mapped_column(
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

    # Relationships
    user: Mapped["User"] = relationship(back_populates="flashcards")
    review_history: Mapped[list["ReviewHistory"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Flashcard."""
        return (
            f"<Flashcard(user_id={self.user_id}, type='{self.content_type}', "
            f"ease={self.ease_factor}, interval={self.interval_days})>"
        )

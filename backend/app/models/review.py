"""
ReviewHistory model for tracking flashcard review sessions.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReviewHistory(Base):
    """
    Review history model for tracking individual review sessions.

    Attributes:
        id: Unique identifier (UUID)
        flashcard_id: Foreign key to Flashcard
        user_id: Foreign key to User
        quality: Quality rating (0-5, SM-2 algorithm)
        time_spent: Time spent on review in seconds
        reviewed_at: Timestamp of the review
    """

    __tablename__ = "review_history"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign Keys
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Review Data
    quality: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    time_spent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timestamp
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Relationships
    flashcard: Mapped["Flashcard"] = relationship(back_populates="review_history")
    user: Mapped["User"] = relationship(back_populates="review_history")

    def __repr__(self) -> str:
        """String representation of ReviewHistory."""
        return f"<ReviewHistory(flashcard_id={self.flashcard_id}, quality={self.quality})>"

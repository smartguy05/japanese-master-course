"""
Lesson model for learning content.
"""

import uuid
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Lesson(Base):
    """
    Lesson model for structured learning content.

    Attributes:
        id: Unique identifier (UUID)
        title: Lesson title
        lesson_type: Type of lesson (grammar, vocabulary, kanji, conversation)
        jlpt_level: JLPT level (N5, N4, N3, N2, N1)
        order_index: Order within the level
        content: Lesson content (JSONB)
        exercises: Practice exercises (JSONB)
        estimated_duration: Estimated completion time in minutes
        prerequisites: Required previous lessons (JSONB array of lesson IDs)
        is_published: Whether the lesson is published
    """

    __tablename__ = "lessons"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Lesson Metadata
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    lesson_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    jlpt_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Content (JSONB for flexibility)
    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    exercises: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Additional Info
    estimated_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    prerequisites: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Status
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    progress_records: Mapped[list["LessonProgress"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Lesson."""
        return f"<Lesson(title='{self.title}', type='{self.lesson_type}', level='{self.jlpt_level}')>"

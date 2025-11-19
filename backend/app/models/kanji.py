"""
Kanji model for Japanese characters.
"""

import uuid
from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Kanji(Base):
    """
    Kanji character model.

    Attributes:
        id: Unique identifier (UUID)
        character: The kanji character (unique)
        jlpt_level: JLPT level (N5, N4, N3, N2, N1)
        frequency_rank: Frequency rank (lower is more common)
        meanings: List of English meanings (JSONB)
        on_readings: List of on-yomi readings (JSONB)
        kun_readings: List of kun-yomi readings (JSONB)
        radical: Kanji radical
        stroke_count: Number of strokes
        grade: Japanese school grade level
        examples: Example words/compounds (JSONB)
    """

    __tablename__ = "kanji"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Kanji Data
    character: Mapped[str] = mapped_column(
        String(1),
        unique=True,
        nullable=False,
        index=True,
    )
    jlpt_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    frequency_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    # Meanings and Readings (JSONB arrays)
    meanings: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    on_readings: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    kun_readings: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Additional Info
    radical: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    stroke_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    grade: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Examples (JSONB array of objects)
    examples: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    def __repr__(self) -> str:
        """String representation of Kanji."""
        return f"<Kanji(character='{self.character}', jlpt_level='{self.jlpt_level}')>"

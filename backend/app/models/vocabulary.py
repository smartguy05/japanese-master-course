"""
Vocabulary model for Japanese words.
"""

import uuid
from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vocabulary(Base):
    """
    Vocabulary word model.

    Attributes:
        id: Unique identifier (UUID)
        word: The Japanese word
        reading: Hiragana/katakana reading
        jlpt_level: JLPT level (N5, N4, N3, N2, N1)
        meanings: List of English meanings (JSONB)
        part_of_speech: Part of speech (noun, verb, etc.)
        frequency_rank: Frequency rank (lower is more common)
        audio_url: URL to audio pronunciation
        example_sentences: Example sentences with translations (JSONB)
    """

    __tablename__ = "vocabulary"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Vocabulary Data
    word: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    reading: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    jlpt_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    # Meanings (JSONB array)
    meanings: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Grammar
    part_of_speech: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Additional Info
    frequency_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    audio_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Example sentences (JSONB array of objects)
    example_sentences: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    def __repr__(self) -> str:
        """String representation of Vocabulary."""
        return f"<Vocabulary(word='{self.word}', reading='{self.reading}', jlpt_level='{self.jlpt_level}')>"

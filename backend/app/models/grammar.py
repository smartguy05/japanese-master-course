"""
GrammarPoint model for Japanese grammar patterns.
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GrammarPoint(Base):
    """
    Grammar point model.

    Attributes:
        id: Unique identifier (UUID)
        jlpt_level: JLPT level (N5, N4, N3, N2, N1)
        grammar_pattern: The grammar pattern (e.g., "〜てもいい")
        meaning: English explanation of the grammar
        formation: How to form the grammar pattern
        examples: Example sentences (JSONB)
        notes: Additional notes or tips
        common_mistakes: Common learner mistakes (JSONB)
    """

    __tablename__ = "grammar_points"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Grammar Data
    jlpt_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    grammar_pattern: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    meaning: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    formation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Examples (JSONB array of objects)
    examples: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Additional Info
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    common_mistakes: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    def __repr__(self) -> str:
        """String representation of GrammarPoint."""
        return f"<GrammarPoint(pattern='{self.grammar_pattern}', jlpt_level='{self.jlpt_level}')>"

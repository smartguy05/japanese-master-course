"""
Conversation models for AI conversation practice.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationSession(Base):
    """
    Conversation session model for AI practice sessions.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        scenario: Conversation scenario (business, casual, etc.)
        difficulty_level: JLPT level or difficulty
        started_at: Session start timestamp
        ended_at: Session end timestamp
        message_count: Number of messages exchanged
        corrections_count: Number of corrections made
        duration_seconds: Total session duration in seconds
    """

    __tablename__ = "conversation_sessions"

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

    # Session Metadata
    scenario: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    difficulty_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Statistics
    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    corrections_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="conversation_sessions")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of ConversationSession."""
        return (
            f"<ConversationSession(user_id={self.user_id}, scenario='{self.scenario}', "
            f"messages={self.message_count})>"
        )


class ConversationMessage(Base):
    """
    Individual message in a conversation session.

    Attributes:
        id: Unique identifier (UUID)
        session_id: Foreign key to ConversationSession
        role: Message role (user or assistant)
        content: Message content
        has_correction: Whether this message contains a correction
        correction_data: Correction details (JSONB)
        created_at: Message timestamp
    """

    __tablename__ = "conversation_messages"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign Keys
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message Data
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Correction Data
    has_correction: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    correction_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Relationships
    session: Mapped["ConversationSession"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        """String representation of ConversationMessage."""
        return f"<ConversationMessage(session_id={self.session_id}, role='{self.role}')>"

"""
Conversation service for managing conversation sessions and messages.

This service handles:
- Creating and managing conversation sessions
- Adding messages to sessions
- Retrieving conversation history
- Calculating session statistics
- Context management for long conversations
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import ConversationMessage, ConversationSession


class ConversationError(Exception):
    """Custom exception for conversation service errors."""

    pass


class ConversationService:
    """
    Service for conversation session management.

    Handles all conversation-related business logic including
    session creation, message management, and statistics.
    """

    # Valid scenarios for conversation practice
    VALID_SCENARIOS = [
        "general",
        "restaurant",
        "shopping",
        "directions",
        "business",
        "interview",
        "introduction",
    ]

    # Valid JLPT difficulty levels
    VALID_LEVELS = ["N5", "N4", "N3", "N2", "N1"]

    def __init__(self, db: AsyncSession):
        """
        Initialize conversation service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_session(
        self,
        user_id: uuid.UUID,
        scenario: str,
        difficulty_level: str,
    ) -> ConversationSession:
        """
        Create a new conversation session.

        Args:
            user_id: ID of the user
            scenario: Conversation scenario
            difficulty_level: JLPT level

        Returns:
            Created ConversationSession

        Raises:
            ConversationError: If validation fails
        """
        # Validate inputs
        self.validate_scenario(scenario)
        self.validate_difficulty_level(difficulty_level)

        # Create session
        session = ConversationSession(
            user_id=user_id,
            scenario=scenario,
            difficulty_level=difficulty_level,
            started_at=datetime.utcnow(),
            message_count=0,
            corrections_count=0,
            duration_seconds=0,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        correction_data: Optional[dict] = None,
    ) -> ConversationMessage:
        """
        Add a message to a conversation session.

        Args:
            session_id: ID of the conversation session
            role: Message role ("user" or "assistant")
            content: Message content
            correction_data: Optional correction information

        Returns:
            Created ConversationMessage

        Raises:
            ConversationError: If session not found
        """
        # Validate role
        if role not in ["user", "assistant"]:
            raise ConversationError(f"Invalid role: {role}")

        # Create message
        has_correction = correction_data is not None
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            has_correction=has_correction,
            correction_data=correction_data,
            created_at=datetime.utcnow(),
        )

        self.db.add(message)

        # Update session statistics
        await self.increment_message_count(session_id)
        if has_correction:
            await self.increment_corrections_count(session_id)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_session(self, session_id: uuid.UUID) -> ConversationSession:
        """
        Get conversation session with all messages.

        Args:
            session_id: ID of the session

        Returns:
            ConversationSession with messages loaded

        Raises:
            ConversationError: If session not found
        """
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.id == session_id)
            .options(selectinload(ConversationSession.messages))
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ConversationError(f"Conversation session {session_id} not found")

        return session

    async def get_user_sessions(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ConversationSession]:
        """
        Get list of user's conversation sessions.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip

        Returns:
            List of ConversationSession objects
        """
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.user_id == user_id)
            .order_by(ConversationSession.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        sessions = result.scalars().all()
        return list(sessions)

    async def end_session(self, session_id: uuid.UUID) -> ConversationSession:
        """
        End a conversation session and calculate final statistics.

        Args:
            session_id: ID of the session to end

        Returns:
            Updated ConversationSession

        Raises:
            ConversationError: If session not found or already ended
        """
        session = await self.get_session(session_id)

        if session.ended_at is not None:
            raise ConversationError("Conversation session already ended")

        # Calculate duration
        ended_at = datetime.utcnow()
        duration = (ended_at - session.started_at).total_seconds()

        # Update session
        session.ended_at = ended_at
        session.duration_seconds = int(duration)

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def get_conversation_context(
        self,
        session_id: uuid.UUID,
        max_messages: int = 20,
    ) -> list[dict]:
        """
        Get conversation context for AI prompt.

        Returns recent messages formatted for prompt inclusion.
        If conversation exceeds max_messages, older messages are summarized.

        Args:
            session_id: ID of the session
            max_messages: Maximum number of messages to include

        Returns:
            List of message dictionaries for prompt context
        """
        session = await self.get_session(session_id)

        # Get most recent messages
        messages = sorted(session.messages, key=lambda m: m.created_at)

        # Take only recent messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        # Format for prompt
        context = [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in recent_messages
        ]

        return context

    async def summarize_conversation(self, messages: list[dict]) -> str:
        """
        Create a summary of conversation messages.

        This is used when conversation history becomes too long
        to fit in the AI context window.

        Args:
            messages: List of message dictionaries

        Returns:
            Summary string
        """
        # Simple summarization - in production, you might use AI for this
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]

        summary = (
            f"Previous conversation ({len(messages)} messages): "
            f"Student sent {len(user_messages)} messages, "
            f"received {len(assistant_messages)} responses. "
        )

        # Include first few messages as context
        if len(messages) > 0:
            summary += f"Started with: {messages[0]['content'][:50]}..."

        return summary

    async def increment_message_count(self, session_id: uuid.UUID) -> None:
        """
        Increment the message count for a session.

        Args:
            session_id: ID of the session
        """
        result = await self.db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.message_count += 1
            # Note: commit happens in the calling method

    async def increment_corrections_count(self, session_id: uuid.UUID) -> None:
        """
        Increment the corrections count for a session.

        Args:
            session_id: ID of the session
        """
        result = await self.db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session:
            session.corrections_count += 1
            # Note: commit happens in the calling method

    def validate_scenario(self, scenario: str) -> None:
        """
        Validate conversation scenario.

        Args:
            scenario: Scenario to validate

        Raises:
            ConversationError: If scenario is invalid
        """
        if scenario not in self.VALID_SCENARIOS:
            raise ConversationError(
                f"Invalid scenario: {scenario}. Must be one of {self.VALID_SCENARIOS}"
            )

    def validate_difficulty_level(self, level: str) -> None:
        """
        Validate difficulty level.

        Args:
            level: JLPT level to validate

        Raises:
            ConversationError: If level is invalid
        """
        if level not in self.VALID_LEVELS:
            raise ConversationError(
                f"Invalid difficulty level: {level}. Must be one of {self.VALID_LEVELS}"
            )


def get_conversation_service(db: AsyncSession) -> ConversationService:
    """
    Dependency for getting conversation service instance.

    Args:
        db: Database session

    Returns:
        ConversationService instance
    """
    return ConversationService(db=db)

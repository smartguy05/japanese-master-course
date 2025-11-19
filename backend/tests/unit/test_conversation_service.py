"""
Unit tests for conversation service.

Following TDD principles - tests written FIRST before implementation.
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.conversation_service import ConversationService, ConversationError


class TestConversationService:
    """Test suite for conversation service."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.add = Mock()
        return session

    @pytest.fixture
    def conversation_service(self, mock_db_session):
        """Create conversation service with mocked dependencies."""
        return ConversationService(db=mock_db_session)

    @pytest.mark.asyncio
    async def test_create_session(self, conversation_service, mock_db_session):
        """Test creating a new conversation session."""
        # Arrange
        user_id = uuid.uuid4()
        scenario = "restaurant"
        difficulty_level = "N4"

        # Act
        session = await conversation_service.create_session(
            user_id=user_id,
            scenario=scenario,
            difficulty_level=difficulty_level
        )

        # Assert
        assert session.user_id == user_id
        assert session.scenario == scenario
        assert session.difficulty_level == difficulty_level
        assert session.message_count == 0
        assert session.corrections_count == 0
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_user(self, conversation_service, mock_db_session):
        """Test adding a user message to session."""
        # Arrange
        session_id = uuid.uuid4()
        content = "こんにちは"
        role = "user"

        # Act
        message = await conversation_service.add_message(
            session_id=session_id,
            role=role,
            content=content,
            correction_data=None
        )

        # Assert
        assert message.session_id == session_id
        assert message.role == role
        assert message.content == content
        assert message.has_correction is False
        mock_db_session.add.assert_called()

    @pytest.mark.asyncio
    async def test_add_message_with_correction(
        self, conversation_service, mock_db_session
    ):
        """Test adding assistant message with correction."""
        # Arrange
        session_id = uuid.uuid4()
        content = "いいですね！"
        correction_data = {
            "original": "私が好きです",
            "corrected": "私は好きです",
            "explanation": "Use は for topic marker"
        }

        # Act
        message = await conversation_service.add_message(
            session_id=session_id,
            role="assistant",
            content=content,
            correction_data=correction_data
        )

        # Assert
        assert message.has_correction is True
        assert message.correction_data == correction_data
        mock_db_session.add.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_with_messages(
        self, conversation_service, mock_db_session
    ):
        """Test retrieving session with all messages."""
        # Arrange
        session_id = uuid.uuid4()
        mock_session = Mock()
        mock_session.id = session_id
        mock_session.messages = [
            Mock(role="user", content="こんにちは"),
            Mock(role="assistant", content="こんにちは！")
        ]

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await conversation_service.get_session(session_id)

        # Assert
        assert result.id == session_id
        assert len(result.messages) == 2
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_not_found(
        self, conversation_service, mock_db_session
    ):
        """Test retrieving non-existent session."""
        # Arrange
        session_id = uuid.uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ConversationError, match="not found"):
            await conversation_service.get_session(session_id)

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, conversation_service, mock_db_session):
        """Test listing user's conversation sessions."""
        # Arrange
        user_id = uuid.uuid4()
        mock_sessions = [
            Mock(id=uuid.uuid4(), scenario="restaurant"),
            Mock(id=uuid.uuid4(), scenario="shopping")
        ]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_sessions
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await conversation_service.get_user_sessions(
            user_id=user_id,
            limit=10
        )

        # Assert
        assert len(result) == 2
        assert result[0].scenario == "restaurant"
        assert result[1].scenario == "shopping"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_session(self, conversation_service, mock_db_session):
        """Test ending a conversation session with statistics."""
        # Arrange
        session_id = uuid.uuid4()
        started_at = datetime.utcnow() - timedelta(minutes=10)

        mock_session = Mock()
        mock_session.id = session_id
        mock_session.started_at = started_at
        mock_session.ended_at = None
        mock_session.message_count = 10
        mock_session.corrections_count = 3
        mock_session.messages = [
            Mock(has_correction=False),
            Mock(has_correction=True),
            Mock(has_correction=False),
        ]

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await conversation_service.end_session(session_id)

        # Assert
        assert result.ended_at is not None
        assert result.duration_seconds > 0
        assert result.message_count == 10
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_end_session_already_ended(
        self, conversation_service, mock_db_session
    ):
        """Test ending a session that's already ended."""
        # Arrange
        session_id = uuid.uuid4()
        mock_session = Mock()
        mock_session.ended_at = datetime.utcnow()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ConversationError, match="already ended"):
            await conversation_service.end_session(session_id)

    @pytest.mark.asyncio
    async def test_summarize_conversation(self, conversation_service):
        """Test summarizing long conversation for context management."""
        # Arrange
        messages = [
            {"role": "user", "content": "こんにちは"},
            {"role": "assistant", "content": "こんにちは！元気ですか？"},
            {"role": "user", "content": "元気です"},
            {"role": "assistant", "content": "それはよかったです"},
        ] * 10  # Create long conversation

        # Act
        summary = await conversation_service.summarize_conversation(messages)

        # Assert
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) < sum(len(m["content"]) for m in messages)

    @pytest.mark.asyncio
    async def test_get_conversation_context(
        self, conversation_service, mock_db_session
    ):
        """Test getting conversation context with message limit."""
        # Arrange
        session_id = uuid.uuid4()
        messages = [
            Mock(role="user", content=f"Message {i}", created_at=datetime.utcnow())
            for i in range(30)
        ]
        mock_session = Mock()
        mock_session.messages = messages

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act
        context = await conversation_service.get_conversation_context(
            session_id=session_id,
            max_messages=20
        )

        # Assert
        assert len(context) <= 20
        # Should return most recent messages
        assert context[-1]["content"] == "Message 29"

    @pytest.mark.asyncio
    async def test_increment_message_count(
        self, conversation_service, mock_db_session
    ):
        """Test incrementing message count on session."""
        # Arrange
        session_id = uuid.uuid4()
        mock_session = Mock()
        mock_session.message_count = 5

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act
        await conversation_service.increment_message_count(session_id)

        # Assert
        assert mock_session.message_count == 6
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_increment_corrections_count(
        self, conversation_service, mock_db_session
    ):
        """Test incrementing corrections count on session."""
        # Arrange
        session_id = uuid.uuid4()
        mock_session = Mock()
        mock_session.corrections_count = 2

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db_session.execute.return_value = mock_result

        # Act
        await conversation_service.increment_corrections_count(session_id)

        # Assert
        assert mock_session.corrections_count == 3
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_validate_scenario(self, conversation_service):
        """Test scenario validation."""
        # Arrange
        valid_scenarios = [
            "general", "restaurant", "shopping", "directions",
            "business", "interview", "introduction"
        ]

        # Act & Assert
        for scenario in valid_scenarios:
            # Should not raise
            conversation_service.validate_scenario(scenario)

        with pytest.raises(ConversationError, match="Invalid scenario"):
            conversation_service.validate_scenario("invalid_scenario")

    @pytest.mark.asyncio
    async def test_validate_difficulty_level(self, conversation_service):
        """Test difficulty level validation."""
        # Arrange
        valid_levels = ["N5", "N4", "N3", "N2", "N1"]

        # Act & Assert
        for level in valid_levels:
            # Should not raise
            conversation_service.validate_difficulty_level(level)

        with pytest.raises(ConversationError, match="Invalid difficulty"):
            conversation_service.validate_difficulty_level("N6")

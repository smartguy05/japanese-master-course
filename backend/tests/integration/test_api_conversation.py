"""
Integration tests for conversation API endpoints.

Following TDD principles - tests written FIRST before implementation.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.conversation import ConversationMessage, ConversationSession
from app.models.user import User


@pytest.mark.asyncio
class TestConversationAPI:
    """Integration tests for conversation API endpoints."""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Create a test user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            target_proficiency="N3"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def auth_headers(self, test_user):
        """Create authentication headers for test user."""
        # Mock JWT token creation
        return {"Authorization": f"Bearer test-token-{test_user.id}"}

    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service for testing."""
        with patch("app.api.conversation.get_ai_service") as mock:
            service = AsyncMock()
            service.get_conversation_response = AsyncMock()
            mock.return_value = service
            yield service

    async def test_create_conversation_session(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test POST /api/conversation/sessions - create new session."""
        # Arrange
        payload = {
            "scenario": "restaurant",
            "difficulty_level": "N4"
        }

        # Act
        response = await client.post(
            "/api/conversation/sessions",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["scenario"] == "restaurant"
        assert data["difficulty_level"] == "N4"
        assert data["user_id"] == str(test_user.id)
        assert data["message_count"] == 0
        assert data["corrections_count"] == 0
        assert "id" in data
        assert "started_at" in data

        # Verify in database
        result = await db_session.execute(
            select(ConversationSession).where(
                ConversationSession.id == uuid.UUID(data["id"])
            )
        )
        session = result.scalar_one_or_none()
        assert session is not None
        assert session.scenario == "restaurant"

    async def test_create_conversation_session_invalid_scenario(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating session with invalid scenario."""
        # Arrange
        payload = {
            "scenario": "invalid_scenario",
            "difficulty_level": "N4"
        }

        # Act
        response = await client.post(
            "/api/conversation/sessions",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "scenario" in response.json()["detail"].lower()

    async def test_create_conversation_session_invalid_level(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating session with invalid difficulty level."""
        # Arrange
        payload = {
            "scenario": "restaurant",
            "difficulty_level": "N6"
        }

        # Act
        response = await client.post(
            "/api/conversation/sessions",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "difficulty" in response.json()["detail"].lower()

    async def test_send_message_and_get_response(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
        mock_ai_service
    ):
        """Test POST /api/conversation/sessions/{id}/messages - send message."""
        # Arrange - create session first
        session = ConversationSession(
            user_id=test_user.id,
            scenario="restaurant",
            difficulty_level="N4"
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Mock AI response
        from app.services.ai_service import AIResponse, CorrectionData
        mock_ai_response = AIResponse(
            response="はい、何になさいますか？",
            correction=CorrectionData(
                original="メニューを見せてください",
                corrected="メニューを見せていただけますか",
                explanation="Using ていただけますか is more polite"
            ),
            encouragement="Great attempt at being polite!"
        )
        mock_ai_service.get_conversation_response.return_value = mock_ai_response

        payload = {
            "content": "メニューを見せてください"
        }

        # Act
        response = await client.post(
            f"/api/conversation/sessions/{session.id}/messages",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "はい、何になさいますか？"
        assert data["correction"] is not None
        assert data["correction"]["original"] == "メニューを見せてください"
        assert data["correction"]["corrected"] == "メニューを見せていただけますか"
        assert data["encouragement"] == "Great attempt at being polite!"

        # Verify messages saved in database
        result = await db_session.execute(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session.id)
            .order_by(ConversationMessage.created_at)
        )
        messages = result.scalars().all()
        assert len(messages) == 2  # User message + AI response
        assert messages[0].role == "user"
        assert messages[0].content == "メニューを見せてください"
        assert messages[1].role == "assistant"
        assert messages[1].has_correction is True

    async def test_send_message_to_nonexistent_session(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test sending message to non-existent session."""
        # Arrange
        fake_id = uuid.uuid4()
        payload = {"content": "こんにちは"}

        # Act
        response = await client.post(
            f"/api/conversation/sessions/{fake_id}/messages",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 404

    async def test_get_conversation_session(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test GET /api/conversation/sessions/{id} - get session details."""
        # Arrange - create session with messages
        session = ConversationSession(
            user_id=test_user.id,
            scenario="shopping",
            difficulty_level="N3",
            message_count=2,
            corrections_count=1
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        message1 = ConversationMessage(
            session_id=session.id,
            role="user",
            content="いくらですか？"
        )
        message2 = ConversationMessage(
            session_id=session.id,
            role="assistant",
            content="500円です",
            has_correction=False
        )
        db_session.add_all([message1, message2])
        await db_session.commit()

        # Act
        response = await client.get(
            f"/api/conversation/sessions/{session.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(session.id)
        assert data["scenario"] == "shopping"
        assert data["message_count"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "いくらですか？"
        assert data["messages"][1]["content"] == "500円です"

    async def test_get_conversation_session_unauthorized(
        self,
        client: AsyncClient,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test getting session without proper authorization."""
        # Arrange - create session
        session = ConversationSession(
            user_id=test_user.id,
            scenario="general",
            difficulty_level="N5"
        )
        db_session.add(session)
        await db_session.commit()

        # Act - no auth headers
        response = await client.get(
            f"/api/conversation/sessions/{session.id}"
        )

        # Assert
        assert response.status_code == 401

    async def test_list_user_conversations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test GET /api/conversation/sessions - list user's sessions."""
        # Arrange - create multiple sessions
        sessions = [
            ConversationSession(
                user_id=test_user.id,
                scenario=f"scenario_{i}",
                difficulty_level="N4"
            )
            for i in range(5)
        ]
        db_session.add_all(sessions)
        await db_session.commit()

        # Act
        response = await client.get(
            "/api/conversation/sessions",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("scenario" in session for session in data)
        assert all("started_at" in session for session in data)

    async def test_list_user_conversations_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test pagination of conversation list."""
        # Arrange - create many sessions
        sessions = [
            ConversationSession(
                user_id=test_user.id,
                scenario="general",
                difficulty_level="N4"
            )
            for _ in range(15)
        ]
        db_session.add_all(sessions)
        await db_session.commit()

        # Act
        response = await client.get(
            "/api/conversation/sessions?limit=10",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

    async def test_end_conversation_session(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test DELETE /api/conversation/sessions/{id} - end session."""
        # Arrange
        session = ConversationSession(
            user_id=test_user.id,
            scenario="business",
            difficulty_level="N3",
            message_count=10,
            corrections_count=3
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # Act
        response = await client.delete(
            f"/api/conversation/sessions/{session.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["ended_at"] is not None
        assert data["duration_seconds"] > 0
        assert data["message_count"] == 10
        assert data["corrections_count"] == 3

        # Verify in database
        await db_session.refresh(session)
        assert session.ended_at is not None

    async def test_end_conversation_session_already_ended(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """Test ending a session that's already ended."""
        # Arrange
        session = ConversationSession(
            user_id=test_user.id,
            scenario="general",
            difficulty_level="N5",
            ended_at=datetime.utcnow()
        )
        db_session.add(session)
        await db_session.commit()

        # Act
        response = await client.delete(
            f"/api/conversation/sessions/{session.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "already ended" in response.json()["detail"]

    async def test_complete_conversation_flow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
        mock_ai_service
    ):
        """Test complete conversation flow from start to end."""
        from app.services.ai_service import AIResponse

        # Step 1: Create session
        create_response = await client.post(
            "/api/conversation/sessions",
            json={"scenario": "introduction", "difficulty_level": "N5"},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        # Step 2: Exchange multiple messages
        mock_ai_service.get_conversation_response.return_value = AIResponse(
            response="よろしくお願いします",
            correction=None,
            encouragement="Perfect!"
        )

        for i, message in enumerate(["こんにちは", "私は太郎です", "よろしく"]):
            msg_response = await client.post(
                f"/api/conversation/sessions/{session_id}/messages",
                json={"content": message},
                headers=auth_headers
            )
            assert msg_response.status_code == 200

        # Step 3: Get session details
        get_response = await client.get(
            f"/api/conversation/sessions/{session_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["message_count"] >= 6  # 3 user + 3 AI

        # Step 4: End session
        end_response = await client.delete(
            f"/api/conversation/sessions/{session_id}",
            headers=auth_headers
        )
        assert end_response.status_code == 200
        assert end_response.json()["ended_at"] is not None

    async def test_conversation_with_different_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        mock_ai_service
    ):
        """Test conversations work with all supported scenarios."""
        from app.services.ai_service import AIResponse

        scenarios = [
            "general", "restaurant", "shopping", "directions",
            "business", "interview", "introduction"
        ]

        mock_ai_service.get_conversation_response.return_value = AIResponse(
            response="はい",
            correction=None,
            encouragement="Good!"
        )

        for scenario in scenarios:
            # Create session for each scenario
            response = await client.post(
                "/api/conversation/sessions",
                json={"scenario": scenario, "difficulty_level": "N4"},
                headers=auth_headers
            )
            assert response.status_code == 201

            # Send a test message
            session_id = response.json()["id"]
            msg_response = await client.post(
                f"/api/conversation/sessions/{session_id}/messages",
                json={"content": "テスト"},
                headers=auth_headers
            )
            assert msg_response.status_code == 200

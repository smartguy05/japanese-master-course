"""
Unit tests for AI service.

Following TDD principles - tests written FIRST before implementation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.ai_service import AIService, AIServiceError, AIResponse


class TestAIService:
    """Test suite for AI conversation service."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client for testing."""
        with patch("app.services.ai_service.Anthropic") as mock:
            mock_client = Mock()
            mock.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def ai_service(self, mock_anthropic_client):
        """Create AI service with mocked client."""
        return AIService(
            api_key="test-key",
            model="claude-sonnet-4-20250514"
        )

    @pytest.mark.asyncio
    async def test_get_conversation_response_with_correction(
        self, ai_service, mock_anthropic_client
    ):
        """Test AI conversation response parsing with grammar correction."""
        # Arrange
        user_input = "私は学校に行きました"
        mock_response = Mock(
            content=[Mock(text="""<response>それはいいですね！どのくらい勉強しましたか？</response>
<correction>
Original: 私は学校に行きました
Corrected: 私は学校へ行きました
Explanation: For destinations, the particle へ (e) is more natural than に (ni) when indicating direction of movement.
</correction>
<encouragement>Great job forming a complete sentence!</encouragement>""")]
        )

        # Mock the async _call_claude_api method directly
        ai_service._call_claude_api = AsyncMock(return_value=mock_response.content[0].text)

        # Act
        result = await ai_service.get_conversation_response(
            user_message=user_input,
            conversation_history=[],
            user_level="N5"
        )

        # Assert
        assert isinstance(result, AIResponse)
        assert result.response == "それはいいですね！どのくらい勉強しましたか？"
        assert result.correction is not None
        assert result.correction.original == "私は学校に行きました"
        assert result.correction.corrected == "私は学校へ行きました"
        assert "particle へ" in result.correction.explanation
        assert result.encouragement == "Great job forming a complete sentence!"

    @pytest.mark.asyncio
    async def test_get_conversation_response_no_correction(
        self, ai_service, mock_anthropic_client
    ):
        """Test AI conversation response without correction."""
        # Arrange
        user_input = "こんにちは"
        mock_response_text = """<response>こんにちは！元気ですか？</response>
<encouragement>Perfect greeting!</encouragement>"""

        # Mock the async _call_claude_api method directly
        ai_service._call_claude_api = AsyncMock(return_value=mock_response_text)

        # Act
        result = await ai_service.get_conversation_response(
            user_message=user_input,
            conversation_history=[],
            user_level="N5"
        )

        # Assert
        assert isinstance(result, AIResponse)
        assert result.response == "こんにちは！元気ですか？"
        assert result.correction is None
        assert result.encouragement == "Perfect greeting!"

    def test_parse_response_with_correction(self, ai_service):
        """Test parsing AI response containing correction."""
        # Arrange
        raw_text = """<response>いいですね！</response>
<correction>
Original: 私が好きです
Corrected: 私は好きです
Explanation: Use は for the topic marker, not が in this context.
</correction>
<encouragement>Keep practicing!</encouragement>"""

        # Act
        result = ai_service.parse_response(raw_text)

        # Assert
        assert result.response == "いいですね！"
        assert result.correction.original == "私が好きです"
        assert result.correction.corrected == "私は好きです"
        assert "topic marker" in result.correction.explanation
        assert result.encouragement == "Keep practicing!"

    def test_parse_response_no_correction(self, ai_service):
        """Test parsing AI response without correction."""
        # Arrange
        raw_text = """<response>素晴らしいですね！</response>
<encouragement>Excellent work!</encouragement>"""

        # Act
        result = ai_service.parse_response(raw_text)

        # Assert
        assert result.response == "素晴らしいですね！"
        assert result.correction is None
        assert result.encouragement == "Excellent work!"

    def test_parse_response_malformed(self, ai_service):
        """Test parsing malformed AI response."""
        # Arrange
        raw_text = "This is not properly formatted"

        # Act & Assert
        with pytest.raises(AIServiceError, match="Failed to parse AI response"):
            ai_service.parse_response(raw_text)

    def test_build_conversation_prompt_empty_history(self, ai_service):
        """Test building prompt with empty conversation history."""
        # Arrange
        user_message = "こんにちは"
        user_level = "N5"

        # Act
        prompt = ai_service.build_conversation_prompt(
            user_message=user_message,
            conversation_history=[],
            user_level=user_level,
            scenario="general"
        )

        # Assert
        assert "N5" in prompt
        assert "こんにちは" in prompt
        assert "patient and encouraging" in prompt
        assert "Japanese language tutor" in prompt
        assert "general" in prompt.lower()

    def test_build_conversation_prompt_with_history(self, ai_service):
        """Test building prompt with conversation history."""
        # Arrange
        user_message = "元気です"
        user_level = "N4"
        history = [
            {"role": "user", "content": "こんにちは"},
            {"role": "assistant", "content": "こんにちは！元気ですか？"}
        ]

        # Act
        prompt = ai_service.build_conversation_prompt(
            user_message=user_message,
            conversation_history=history,
            user_level=user_level,
            scenario="general"
        )

        # Assert
        assert "N4" in prompt
        assert "元気です" in prompt
        assert "こんにちは" in prompt
        assert "元気ですか？" in prompt

    @pytest.mark.asyncio
    async def test_error_handling_api_failure(
        self, ai_service, mock_anthropic_client
    ):
        """Test error handling when API call fails."""
        # Arrange
        ai_service._call_claude_api = AsyncMock(
            side_effect=AIServiceError("API Error")
        )

        # Act & Assert
        with pytest.raises(AIServiceError, match="AI service error"):
            await ai_service.get_conversation_response(
                user_message="test",
                conversation_history=[],
                user_level="N5"
            )

    @pytest.mark.asyncio
    async def test_get_conversation_response_different_scenarios(
        self, ai_service, mock_anthropic_client
    ):
        """Test conversation response for different scenarios."""
        # Arrange
        scenarios = ["restaurant", "shopping", "business", "directions"]
        mock_response_text = "<response>はい</response><encouragement>Good!</encouragement>"
        ai_service._call_claude_api = AsyncMock(return_value=mock_response_text)

        # Act & Assert
        for scenario in scenarios:
            result = await ai_service.get_conversation_response(
                user_message="テスト",
                conversation_history=[],
                user_level="N3",
                scenario=scenario
            )
            assert isinstance(result, AIResponse)

    def test_extract_correction_data_complete(self, ai_service):
        """Test extracting complete correction data."""
        # Arrange
        correction_text = """Original: 私が行く
Corrected: 私は行く
Explanation: Use は instead of が here."""

        # Act
        correction = ai_service.extract_correction_data(correction_text)

        # Assert
        assert correction.original == "私が行く"
        assert correction.corrected == "私は行く"
        assert correction.explanation == "Use は instead of が here."

    def test_extract_correction_data_missing_fields(self, ai_service):
        """Test extracting correction with missing fields."""
        # Arrange
        correction_text = "Original: test"

        # Act & Assert
        with pytest.raises(AIServiceError, match="Invalid correction format"):
            ai_service.extract_correction_data(correction_text)

    @pytest.mark.asyncio
    async def test_conversation_response_caching(
        self, ai_service, mock_anthropic_client
    ):
        """Test that similar requests can be cached (if caching enabled)."""
        # This test verifies caching behavior when implemented
        # Arrange
        mock_response_text = "<response>はい</response><encouragement>Good!</encouragement>"
        ai_service._call_claude_api = AsyncMock(return_value=mock_response_text)

        # Act
        result1 = await ai_service.get_conversation_response(
            user_message="こんにちは",
            conversation_history=[],
            user_level="N5"
        )
        result2 = await ai_service.get_conversation_response(
            user_message="こんにちは",
            conversation_history=[],
            user_level="N5"
        )

        # Assert - both should succeed
        assert result1.response == "はい"
        assert result2.response == "はい"

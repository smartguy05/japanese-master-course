"""
AI service for conversation practice using Claude API.

This service handles all interactions with the Claude AI model,
including sending conversation prompts and parsing structured responses.
"""

import re
from typing import Optional

from anthropic import Anthropic
from pydantic import BaseModel

from app.config import settings
from app.prompts.conversation_prompts import build_conversation_prompt


class AIServiceError(Exception):
    """Custom exception for AI service errors."""

    pass


class CorrectionData(BaseModel):
    """Data structure for grammar/usage corrections."""

    original: str
    corrected: str
    explanation: str


class AIResponse(BaseModel):
    """Structured AI response from conversation."""

    response: str
    correction: Optional[CorrectionData] = None
    encouragement: str


class AIService:
    """
    Service for interacting with Claude AI for conversation practice.

    This service:
    - Sends conversation prompts to Claude
    - Parses structured responses (response, corrections, encouragement)
    - Handles errors and retries
    - Can cache responses for efficiency (if enabled)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
    ):
        """
        Initialize AI service.

        Args:
            api_key: Anthropic API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
            max_tokens: Maximum tokens for response
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise AIServiceError("Anthropic API key not configured")

        self.model = model or settings.ai_conversation_model
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=self.api_key)

    async def get_conversation_response(
        self,
        user_message: str,
        conversation_history: list[dict],
        user_level: str,
        scenario: str = "general",
    ) -> AIResponse:
        """
        Get AI conversation response with corrections.

        Args:
            user_message: User's message in Japanese
            conversation_history: Previous messages
            user_level: JLPT level (N5-N1)
            scenario: Conversation scenario

        Returns:
            AIResponse with response, corrections, and encouragement

        Raises:
            AIServiceError: If API call fails or response is malformed
        """
        try:
            # Build the prompt
            prompt = build_conversation_prompt(
                user_message=user_message,
                conversation_history=conversation_history,
                user_level=user_level,
                scenario=scenario,
            )

            # Call Claude API
            response = await self._call_claude_api(prompt)

            # Parse and return structured response
            return self.parse_response(response)

        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}") from e

    async def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API with the prompt.

        Args:
            prompt: Complete prompt to send

        Returns:
            Raw text response from Claude

        Raises:
            AIServiceError: If API call fails
        """
        try:
            # Note: anthropic library doesn't have native async support yet
            # We wrap the sync call - in production, consider using httpx for true async
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text

            raise AIServiceError("Empty response from Claude API")

        except Exception as e:
            raise AIServiceError(f"Claude API call failed: {str(e)}") from e

    def parse_response(self, raw_text: str) -> AIResponse:
        """
        Parse structured response from Claude.

        Expected format:
        <response>Japanese text here</response>
        <correction>
        Original: ...
        Corrected: ...
        Explanation: ...
        </correction>
        <encouragement>English encouragement</encouragement>

        Args:
            raw_text: Raw response text from Claude

        Returns:
            Structured AIResponse object

        Raises:
            AIServiceError: If response format is invalid
        """
        try:
            # Extract response
            response_match = re.search(
                r"<response>(.*?)</response>",
                raw_text,
                re.DOTALL | re.IGNORECASE,
            )
            if not response_match:
                raise AIServiceError("Failed to parse AI response: missing <response> tag")

            response_text = response_match.group(1).strip()

            # Extract encouragement
            encouragement_match = re.search(
                r"<encouragement>(.*?)</encouragement>",
                raw_text,
                re.DOTALL | re.IGNORECASE,
            )
            if not encouragement_match:
                raise AIServiceError("Failed to parse AI response: missing <encouragement> tag")

            encouragement_text = encouragement_match.group(1).strip()

            # Extract correction (optional)
            correction_data = None
            correction_match = re.search(
                r"<correction>(.*?)</correction>",
                raw_text,
                re.DOTALL | re.IGNORECASE,
            )

            if correction_match:
                correction_text = correction_match.group(1).strip()
                correction_data = self.extract_correction_data(correction_text)

            return AIResponse(
                response=response_text,
                correction=correction_data,
                encouragement=encouragement_text,
            )

        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError(f"Failed to parse AI response: {str(e)}") from e

    def extract_correction_data(self, correction_text: str) -> CorrectionData:
        """
        Extract correction data from correction text block.

        Expected format:
        Original: [original text]
        Corrected: [corrected text]
        Explanation: [explanation]

        Args:
            correction_text: Text from <correction> tag

        Returns:
            CorrectionData object

        Raises:
            AIServiceError: If correction format is invalid
        """
        try:
            # Extract original
            original_match = re.search(
                r"Original:\s*(.+?)(?:\n|$)",
                correction_text,
                re.IGNORECASE,
            )
            if not original_match:
                raise AIServiceError("Invalid correction format: missing 'Original' field")

            original = original_match.group(1).strip()

            # Extract corrected
            corrected_match = re.search(
                r"Corrected:\s*(.+?)(?:\n|$)",
                correction_text,
                re.IGNORECASE,
            )
            if not corrected_match:
                raise AIServiceError("Invalid correction format: missing 'Corrected' field")

            corrected = corrected_match.group(1).strip()

            # Extract explanation
            explanation_match = re.search(
                r"Explanation:\s*(.+)",
                correction_text,
                re.DOTALL | re.IGNORECASE,
            )
            if not explanation_match:
                raise AIServiceError("Invalid correction format: missing 'Explanation' field")

            explanation = explanation_match.group(1).strip()

            return CorrectionData(
                original=original,
                corrected=corrected,
                explanation=explanation,
            )

        except AIServiceError:
            raise
        except Exception as e:
            raise AIServiceError(f"Failed to extract correction data: {str(e)}") from e

    def build_conversation_prompt(
        self,
        user_message: str,
        conversation_history: list[dict],
        user_level: str,
        scenario: str = "general",
    ) -> str:
        """
        Build conversation prompt (delegates to prompts module).

        Args:
            user_message: User's latest message
            conversation_history: Previous messages
            user_level: JLPT level
            scenario: Conversation scenario

        Returns:
            Complete prompt string
        """
        return build_conversation_prompt(
            user_message=user_message,
            conversation_history=conversation_history,
            user_level=user_level,
            scenario=scenario,
        )


def get_ai_service() -> AIService:
    """
    Dependency for getting AI service instance.

    Returns:
        AIService instance configured with settings
    """
    return AIService()

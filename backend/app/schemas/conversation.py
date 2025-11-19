"""
Pydantic schemas for conversation API.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CorrectionData(BaseModel):
    """Correction information from AI response."""

    original: str = Field(..., description="Original incorrect phrase")
    corrected: str = Field(..., description="Corrected phrase")
    explanation: str = Field(..., description="Explanation of the correction")

    class Config:
        json_schema_extra = {
            "example": {
                "original": "私は学校に行きました",
                "corrected": "私は学校へ行きました",
                "explanation": "For destinations, use へ instead of に"
            }
        }


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1, max_length=2000, description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "こんにちは！元気ですか？"
            }
        }


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: uuid.UUID
    session_id: uuid.UUID
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    has_correction: bool = Field(default=False, description="Whether message contains correction")
    correction_data: Optional[CorrectionData] = Field(None, description="Correction details if applicable")
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "assistant",
                "content": "はい、何になさいますか？",
                "has_correction": True,
                "correction_data": {
                    "original": "メニューを見せてください",
                    "corrected": "メニューを見せていただけますか",
                    "explanation": "Using ていただけますか is more polite"
                },
                "created_at": "2025-11-19T12:00:00Z"
            }
        }


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation session."""

    scenario: str = Field(
        ...,
        description="Conversation scenario",
        pattern="^(general|restaurant|shopping|directions|business|interview|introduction)$"
    )
    difficulty_level: str = Field(
        ...,
        description="JLPT difficulty level",
        pattern="^(N5|N4|N3|N2|N1)$"
    )

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        """Validate scenario is supported."""
        valid_scenarios = [
            "general", "restaurant", "shopping", "directions",
            "business", "interview", "introduction"
        ]
        if v not in valid_scenarios:
            raise ValueError(f"Scenario must be one of {valid_scenarios}")
        return v

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = ["N5", "N4", "N3", "N2", "N1"]
        if v not in valid_levels:
            raise ValueError(f"Difficulty level must be one of {valid_levels}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "restaurant",
                "difficulty_level": "N4"
            }
        }


class ConversationResponse(BaseModel):
    """Schema for conversation session response."""

    id: uuid.UUID
    user_id: uuid.UUID
    scenario: str
    difficulty_level: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int = Field(default=0, description="Total messages in conversation")
    corrections_count: int = Field(default=0, description="Number of corrections made")
    duration_seconds: int = Field(default=0, description="Session duration in seconds")
    messages: list[MessageResponse] = Field(default_factory=list, description="Conversation messages")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "scenario": "restaurant",
                "difficulty_level": "N4",
                "started_at": "2025-11-19T12:00:00Z",
                "ended_at": None,
                "message_count": 4,
                "corrections_count": 1,
                "duration_seconds": 120,
                "messages": []
            }
        }


class ConversationStats(BaseModel):
    """Statistics for a conversation session."""

    message_count: int
    corrections_count: int
    duration_seconds: int
    topics_covered: list[str] = Field(default_factory=list)
    user_message_count: int
    assistant_message_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "message_count": 10,
                "corrections_count": 3,
                "duration_seconds": 300,
                "topics_covered": ["greetings", "ordering food", "politeness"],
                "user_message_count": 5,
                "assistant_message_count": 5
            }
        }


class AIMessageResponse(BaseModel):
    """Response schema for sending a message and getting AI reply."""

    response: str = Field(..., description="AI response in Japanese")
    correction: Optional[CorrectionData] = Field(None, description="Correction if applicable")
    encouragement: str = Field(..., description="Encouraging feedback")
    user_message_id: uuid.UUID = Field(..., description="ID of the user's message")
    assistant_message_id: uuid.UUID = Field(..., description="ID of the assistant's message")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "それはいいですね！どのくらい勉強しましたか？",
                "correction": {
                    "original": "私は学校に行きました",
                    "corrected": "私は学校へ行きました",
                    "explanation": "For destinations, use へ"
                },
                "encouragement": "Great sentence structure!",
                "user_message_id": "123e4567-e89b-12d3-a456-426614174000",
                "assistant_message_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


class ConversationListResponse(BaseModel):
    """Schema for listing conversation sessions."""

    id: uuid.UUID
    scenario: str
    difficulty_level: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int
    corrections_count: int
    duration_seconds: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "scenario": "restaurant",
                "difficulty_level": "N4",
                "started_at": "2025-11-19T12:00:00Z",
                "ended_at": "2025-11-19T12:15:00Z",
                "message_count": 8,
                "corrections_count": 2,
                "duration_seconds": 900
            }
        }

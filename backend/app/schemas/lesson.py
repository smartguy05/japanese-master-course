"""
Pydantic schemas for lesson-related operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Exercise Schemas
# ============================================================================


class ExerciseSubmission(BaseModel):
    """Schema for submitting an exercise answer."""

    answer: str = Field(..., description="User's answer to the exercise")


class ExerciseResult(BaseModel):
    """Schema for exercise validation result."""

    correct: bool = Field(..., description="Whether the answer is correct")
    correct_answer: Optional[str] = Field(
        None, description="The correct answer (if answer was incorrect)"
    )
    explanation: str = Field(..., description="Explanation of the correct answer")


# ============================================================================
# Lesson Progress Schemas
# ============================================================================


class LessonProgressCreate(BaseModel):
    """Schema for creating/updating lesson progress."""

    lesson_id: UUID = Field(..., description="Lesson ID")
    score: Optional[int] = Field(
        None, ge=0, le=100, description="Score achieved (0-100)"
    )
    time_spent: int = Field(0, ge=0, description="Time spent in seconds")


class LessonProgressResponse(BaseModel):
    """Schema for lesson progress response."""

    id: UUID
    user_id: UUID
    lesson_id: UUID
    is_completed: bool
    score: Optional[int] = None
    time_spent: int
    completed_exercises: int
    total_exercises: int
    first_completed_at: Optional[datetime] = None
    last_accessed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Lesson Schemas
# ============================================================================


class LessonBase(BaseModel):
    """Base schema for lesson data."""

    title: str = Field(..., min_length=1, max_length=255, description="Lesson title")
    lesson_type: str = Field(
        ...,
        description="Type of lesson (hiragana, katakana, kanji, vocabulary, grammar, conversation)",
    )
    jlpt_level: str = Field(..., description="JLPT level (N5, N4, N3, N2, N1)")
    order_index: int = Field(0, ge=0, description="Order within the level")
    content: Dict[str, Any] = Field(
        default_factory=dict, description="Lesson content (JSONB)"
    )
    exercises: List[Dict[str, Any]] = Field(
        default_factory=list, description="Practice exercises (JSONB)"
    )
    estimated_duration: Optional[int] = Field(
        None, ge=1, description="Estimated duration in minutes"
    )
    prerequisites: List[str] = Field(
        default_factory=list, description="Required previous lesson IDs"
    )
    is_published: bool = Field(False, description="Whether the lesson is published")

    @field_validator("lesson_type")
    @classmethod
    def validate_lesson_type(cls, v: str) -> str:
        """Validate lesson type."""
        valid_types = {
            "hiragana",
            "katakana",
            "kanji",
            "vocabulary",
            "grammar",
            "conversation",
        }
        if v not in valid_types:
            raise ValueError(f"lesson_type must be one of {valid_types}")
        return v

    @field_validator("jlpt_level")
    @classmethod
    def validate_jlpt_level(cls, v: str) -> str:
        """Validate JLPT level."""
        valid_levels = {"N5", "N4", "N3", "N2", "N1"}
        if v not in valid_levels:
            raise ValueError(f"jlpt_level must be one of {valid_levels}")
        return v


class LessonCreate(LessonBase):
    """Schema for creating a new lesson."""

    pass


class LessonUpdate(BaseModel):
    """Schema for updating a lesson (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    lesson_type: Optional[str] = None
    jlpt_level: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    content: Optional[Dict[str, Any]] = None
    exercises: Optional[List[Dict[str, Any]]] = None
    estimated_duration: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[str]] = None
    is_published: Optional[bool] = None

    @field_validator("lesson_type")
    @classmethod
    def validate_lesson_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate lesson type if provided."""
        if v is None:
            return v
        valid_types = {
            "hiragana",
            "katakana",
            "kanji",
            "vocabulary",
            "grammar",
            "conversation",
        }
        if v not in valid_types:
            raise ValueError(f"lesson_type must be one of {valid_types}")
        return v

    @field_validator("jlpt_level")
    @classmethod
    def validate_jlpt_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate JLPT level if provided."""
        if v is None:
            return v
        valid_levels = {"N5", "N4", "N3", "N2", "N1"}
        if v not in valid_levels:
            raise ValueError(f"jlpt_level must be one of {valid_levels}")
        return v


class LessonResponse(LessonBase):
    """Schema for lesson response."""

    id: UUID
    user_progress: Optional[LessonProgressResponse] = Field(
        None, description="User's progress on this lesson (if authenticated)"
    )

    class Config:
        from_attributes = True


class LessonListItem(BaseModel):
    """Schema for lesson in list view (minimal data)."""

    id: UUID
    title: str
    lesson_type: str
    jlpt_level: str
    order_index: int
    estimated_duration: Optional[int] = None
    is_completed: bool = Field(
        False, description="Whether user has completed this lesson"
    )
    user_score: Optional[int] = Field(
        None, description="User's score on this lesson (if completed)"
    )

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """Schema for paginated lesson list response."""

    items: List[LessonListItem] = Field(..., description="List of lessons")
    total: int = Field(..., description="Total number of lessons matching filter")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


# ============================================================================
# Lesson Completion Schemas
# ============================================================================


class LessonCompleteRequest(BaseModel):
    """Schema for marking a lesson as complete."""

    score: int = Field(..., ge=0, le=100, description="Score achieved (0-100)")
    time_spent: int = Field(..., ge=0, description="Time spent in seconds")


class LessonCompleteResponse(BaseModel):
    """Schema for lesson completion response."""

    lesson_id: UUID
    is_completed: bool
    score: int
    time_spent: int
    xp_earned: int = Field(..., description="XP points earned for completion")
    total_xp: int = Field(..., description="User's total XP after completion")

    class Config:
        from_attributes = True

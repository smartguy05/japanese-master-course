"""
Pydantic schemas for flashcard and review operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FlashcardCreate(BaseModel):
    """Schema for creating a new flashcard."""

    content_type: str = Field(
        ...,
        description="Type of content (kanji, vocabulary, grammar)",
        pattern="^(kanji|vocabulary|grammar)$"
    )
    content_id: UUID = Field(
        ...,
        description="ID of the content item (references kanji, vocabulary, or grammar table)"
    )

    model_config = {"from_attributes": True}


class FlashcardBase(BaseModel):
    """Base flashcard schema with common fields."""

    id: UUID
    user_id: UUID
    content_type: str
    content_id: UUID

    # SRS Parameters
    ease_factor: float = Field(..., ge=1.3, description="SM-2 ease factor (min 1.3)")
    interval_days: int = Field(..., ge=0, description="Days until next review")
    repetitions: int = Field(..., ge=0, description="Consecutive successful reviews")

    # Timestamps
    last_reviewed: Optional[datetime] = None
    next_review: datetime
    created_at: datetime

    # Statistics
    correct_count: int = Field(..., ge=0)
    incorrect_count: int = Field(..., ge=0)

    model_config = {"from_attributes": True}


class FlashcardResponse(FlashcardBase):
    """Schema for flashcard responses with computed fields."""

    @property
    def total_reviews(self) -> int:
        """Total number of reviews."""
        return self.correct_count + self.incorrect_count

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage (0.0 to 1.0)."""
        total = self.total_reviews
        if total == 0:
            return 0.0
        return round(self.correct_count / total, 3)

    @property
    def is_new(self) -> bool:
        """Check if card has never been reviewed."""
        return self.repetitions == 0 and self.last_reviewed is None

    @property
    def is_learning(self) -> bool:
        """Check if card is in learning phase (repetitions < 3)."""
        return 0 < self.repetitions < 3

    @property
    def is_review(self) -> bool:
        """Check if card is in review phase (repetitions >= 3)."""
        return self.repetitions >= 3

    model_config = {"from_attributes": True}


class FlashcardWithContent(FlashcardResponse):
    """Schema for flashcard with joined content data."""

    content: dict = Field(
        ...,
        description="Content data from kanji/vocabulary/grammar table"
    )

    model_config = {"from_attributes": True}


class ReviewRequest(BaseModel):
    """Schema for submitting a flashcard review."""

    quality: int = Field(
        ...,
        ge=0,
        le=5,
        description="Quality rating (0-5): 0=blackout, 1-2=incorrect, 3-5=correct"
    )
    time_spent: int = Field(
        default=0,
        ge=0,
        description="Time spent reviewing in seconds"
    )

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, v: int) -> int:
        """Validate quality is in range 0-5."""
        if not 0 <= v <= 5:
            raise ValueError("Quality must be between 0 and 5")
        return v

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    """Schema for review response with updated SRS parameters."""

    flashcard_id: UUID
    quality: int
    time_spent: int
    reviewed_at: datetime

    # Updated SRS parameters
    new_ease_factor: float = Field(..., ge=1.3)
    new_interval_days: int = Field(..., ge=0)
    new_repetitions: int = Field(..., ge=0)
    next_review_date: datetime

    # Status
    is_correct: bool

    @property
    def quality_label(self) -> str:
        """Get human-readable quality label."""
        labels = {
            0: "Complete blackout",
            1: "Incorrect with some recall",
            2: "Incorrect but easy to recall",
            3: "Correct with serious difficulty",
            4: "Correct with hesitation",
            5: "Perfect response"
        }
        return labels.get(self.quality, "Unknown")

    model_config = {"from_attributes": True}


class FlashcardStats(BaseModel):
    """Schema for flashcard statistics."""

    # Card counts by status
    total_cards: int = Field(..., ge=0)
    new_cards: int = Field(..., ge=0)
    learning_cards: int = Field(..., ge=0)
    review_cards: int = Field(..., ge=0)
    cards_due_today: int = Field(..., ge=0)

    # Review statistics
    total_reviews: int = Field(..., ge=0)
    correct_reviews: int = Field(..., ge=0)
    accuracy: float = Field(..., ge=0.0, le=1.0)
    avg_quality: float = Field(..., ge=0.0, le=5.0)

    # Period
    period_days: int = Field(..., ge=1)

    model_config = {"from_attributes": True}


class ReviewHistoryItem(BaseModel):
    """Schema for individual review history entry."""

    id: UUID
    flashcard_id: UUID
    user_id: UUID
    quality: int = Field(..., ge=0, le=5)
    time_spent: int = Field(..., ge=0)
    reviewed_at: datetime

    @property
    def is_correct(self) -> bool:
        """Check if review was correct (quality >= 3)."""
        return self.quality >= 3

    model_config = {"from_attributes": True}


class FlashcardListParams(BaseModel):
    """Query parameters for listing flashcards."""

    content_type: Optional[str] = Field(
        None,
        pattern="^(kanji|vocabulary|grammar)$",
        description="Filter by content type"
    )
    due_status: Optional[str] = Field(
        None,
        pattern="^(new|learning|review|due|all)$",
        description="Filter by due status"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip"
    )

    model_config = {"from_attributes": True}


class FlashcardListResponse(BaseModel):
    """Schema for paginated flashcard list response."""

    flashcards: list[FlashcardResponse]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    has_more: bool

    model_config = {"from_attributes": True}

"""
Flashcard API endpoints for spaced repetition system.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.flashcard import Flashcard
from app.models.kanji import Kanji
from app.models.vocabulary import Vocabulary
from app.models.grammar import GrammarPoint
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardListResponse,
    ReviewRequest,
    ReviewResponse,
    FlashcardStats,
)
from app.services.srs_service import SRSService


router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.post("", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    flashcard_data: FlashcardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new flashcard for the current user.

    If a flashcard already exists for this content, returns the existing flashcard.

    Args:
        flashcard_data: Flashcard creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        FlashcardResponse: Created or existing flashcard

    Raises:
        HTTPException: If content_id is invalid
    """
    # Check if flashcard already exists
    query = select(Flashcard).where(
        and_(
            Flashcard.user_id == current_user.id,
            Flashcard.content_type == flashcard_data.content_type,
            Flashcard.content_id == flashcard_data.content_id
        )
    )
    result = await db.execute(query)
    existing_flashcard = result.scalar_one_or_none()

    if existing_flashcard:
        # Return existing flashcard
        return FlashcardResponse.model_validate(existing_flashcard)

    # Verify content exists
    content_model_map = {
        "kanji": Kanji,
        "vocabulary": Vocabulary,
        "grammar": GrammarPoint
    }
    content_model = content_model_map.get(flashcard_data.content_type)
    if not content_model:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content_type: {flashcard_data.content_type}"
        )

    query = select(content_model).where(content_model.id == flashcard_data.content_id)
    result = await db.execute(query)
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content not found: {flashcard_data.content_id}"
        )

    # Create new flashcard
    flashcard = Flashcard(
        user_id=current_user.id,
        content_type=flashcard_data.content_type,
        content_id=flashcard_data.content_id,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        next_review=datetime.utcnow(),
        correct_count=0,
        incorrect_count=0
    )

    db.add(flashcard)
    await db.commit()
    await db.refresh(flashcard)

    return FlashcardResponse.model_validate(flashcard)


@router.get("/due", response_model=list[FlashcardResponse])
async def get_due_flashcards(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of cards to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get flashcards due for review.

    Args:
        limit: Maximum number of cards to return
        db: Database session
        current_user: Authenticated user

    Returns:
        list[FlashcardResponse]: List of due flashcards, sorted by next_review

    Example:
        GET /api/flashcards/due?limit=10
    """
    srs_service = SRSService()
    due_cards = await srs_service.get_due_cards(
        db=db,
        user_id=current_user.id,
        limit=limit,
        current_time=datetime.utcnow()
    )

    # Convert to response models
    flashcards = []
    for card_dict in due_cards:
        # Get flashcard from database to ensure fresh data
        query = select(Flashcard).where(Flashcard.id == UUID(card_dict["id"]))
        result = await db.execute(query)
        flashcard = result.scalar_one()
        flashcards.append(FlashcardResponse.model_validate(flashcard))

    return flashcards


@router.post("/{flashcard_id}/review", response_model=ReviewResponse)
async def record_flashcard_review(
    flashcard_id: UUID,
    review_data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a flashcard review and update SRS parameters.

    Args:
        flashcard_id: Flashcard ID
        review_data: Review quality and time spent
        db: Database session
        current_user: Authenticated user

    Returns:
        ReviewResponse: Updated SRS parameters and next review date

    Raises:
        HTTPException: If flashcard not found or doesn't belong to user

    Example:
        POST /api/flashcards/{id}/review
        {
            "quality": 4,
            "time_spent": 15
        }
    """
    # Record review using SRS service
    srs_service = SRSService()

    try:
        next_review = await srs_service.record_review(
            db=db,
            flashcard_id=flashcard_id,
            user_id=current_user.id,
            quality=review_data.quality,
            time_spent=review_data.time_spent,
            review_time=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    # Return review response
    return ReviewResponse(
        flashcard_id=flashcard_id,
        quality=review_data.quality,
        time_spent=review_data.time_spent,
        reviewed_at=datetime.utcnow(),
        new_ease_factor=next_review.ease_factor,
        new_interval_days=next_review.interval_days,
        new_repetitions=next_review.repetitions,
        next_review_date=next_review.next_review_date,
        is_correct=review_data.quality >= 3
    )


@router.get("/stats", response_model=FlashcardStats)
async def get_flashcard_stats(
    period_days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get flashcard statistics for the current user.

    Args:
        period_days: Number of days to analyze
        db: Database session
        current_user: Authenticated user

    Returns:
        FlashcardStats: User's flashcard statistics

    Example:
        GET /api/flashcards/stats?period_days=7
    """
    srs_service = SRSService()
    stats = await srs_service.get_review_stats(
        db=db,
        user_id=current_user.id,
        period_days=period_days
    )

    # Count cards by status
    current_time = datetime.utcnow()

    # New cards (repetitions = 0, never reviewed)
    query = select(func.count(Flashcard.id)).where(
        and_(
            Flashcard.user_id == current_user.id,
            Flashcard.repetitions == 0,
            Flashcard.last_reviewed.is_(None)
        )
    )
    result = await db.execute(query)
    new_cards = result.scalar_one() or 0

    # Learning cards (0 < repetitions < 3)
    query = select(func.count(Flashcard.id)).where(
        and_(
            Flashcard.user_id == current_user.id,
            Flashcard.repetitions > 0,
            Flashcard.repetitions < 3
        )
    )
    result = await db.execute(query)
    learning_cards = result.scalar_one() or 0

    # Review cards (repetitions >= 3)
    query = select(func.count(Flashcard.id)).where(
        and_(
            Flashcard.user_id == current_user.id,
            Flashcard.repetitions >= 3
        )
    )
    result = await db.execute(query)
    review_cards = result.scalar_one() or 0

    return FlashcardStats(
        total_cards=stats["total_cards"],
        new_cards=new_cards,
        learning_cards=learning_cards,
        review_cards=review_cards,
        cards_due_today=stats["cards_due_today"],
        total_reviews=stats["total_reviews"],
        correct_reviews=stats["correct_reviews"],
        accuracy=stats["accuracy"],
        avg_quality=stats["avg_quality"],
        period_days=period_days
    )


@router.get("", response_model=FlashcardListResponse)
async def list_flashcards(
    content_type: Optional[str] = Query(None, pattern="^(kanji|vocabulary|grammar)$"),
    due_status: Optional[str] = Query(None, pattern="^(new|learning|review|due|all)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List flashcards with optional filtering and pagination.

    Args:
        content_type: Filter by content type (kanji, vocabulary, grammar)
        due_status: Filter by status (new, learning, review, due, all)
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database session
        current_user: Authenticated user

    Returns:
        FlashcardListResponse: Paginated list of flashcards

    Example:
        GET /api/flashcards?content_type=kanji&limit=10&offset=0
    """
    # Build query
    query = select(Flashcard).where(Flashcard.user_id == current_user.id)

    # Apply filters
    if content_type:
        query = query.where(Flashcard.content_type == content_type)

    if due_status:
        current_time = datetime.utcnow()
        if due_status == "new":
            query = query.where(
                and_(
                    Flashcard.repetitions == 0,
                    Flashcard.last_reviewed.is_(None)
                )
            )
        elif due_status == "learning":
            query = query.where(
                and_(
                    Flashcard.repetitions > 0,
                    Flashcard.repetitions < 3
                )
            )
        elif due_status == "review":
            query = query.where(Flashcard.repetitions >= 3)
        elif due_status == "due":
            query = query.where(Flashcard.next_review <= current_time)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()

    # Apply pagination
    query = query.limit(limit).offset(offset).order_by(Flashcard.created_at.desc())

    # Execute query
    result = await db.execute(query)
    flashcards = result.scalars().all()

    # Convert to response models
    flashcard_responses = [
        FlashcardResponse.model_validate(fc) for fc in flashcards
    ]

    return FlashcardListResponse(
        flashcards=flashcard_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(flashcards)) < total
    )

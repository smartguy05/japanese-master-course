"""
Lesson API endpoints.
"""

import math
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.lesson import (
    ExerciseResult,
    ExerciseSubmission,
    LessonCompleteRequest,
    LessonCompleteResponse,
    LessonListItem,
    LessonListResponse,
    LessonProgressResponse,
    LessonResponse,
)
from app.services.lesson_service import LessonService

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.get("", response_model=LessonListResponse)
async def list_lessons(
    jlpt_level: Optional[str] = Query(None, description="Filter by JLPT level"),
    lesson_type: Optional[str] = Query(None, description="Filter by lesson type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> LessonListResponse:
    """
    Get list of lessons with optional filtering and pagination.

    - **jlpt_level**: Filter by JLPT level (N5, N4, N3, N2, N1)
    - **lesson_type**: Filter by type (hiragana, katakana, kanji, vocabulary, grammar)
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 20, max: 100)

    Returns paginated list of lessons with user progress if authenticated.
    """
    service = LessonService(db)

    # Calculate pagination
    skip = (page - 1) * size

    # Get lessons and total count
    lessons = await service.get_lessons(
        jlpt_level=jlpt_level,
        lesson_type=lesson_type,
        skip=skip,
        limit=size,
        user_id=current_user.id if current_user else None,
    )
    total = await service.get_lessons_count(
        jlpt_level=jlpt_level, lesson_type=lesson_type
    )

    # Get user progress for lessons if authenticated
    lesson_items = []
    for lesson in lessons:
        is_completed = False
        user_score = None

        if current_user:
            progress = await service.get_user_progress(current_user.id, lesson.id)
            if progress:
                is_completed = progress.is_completed
                user_score = progress.score

        lesson_items.append(
            LessonListItem(
                id=lesson.id,
                title=lesson.title,
                lesson_type=lesson.lesson_type,
                jlpt_level=lesson.jlpt_level,
                order_index=lesson.order_index,
                estimated_duration=lesson.estimated_duration,
                is_completed=is_completed,
                user_score=user_score,
            )
        )

    pages = math.ceil(total / size) if total > 0 else 0

    return LessonListResponse(
        items=lesson_items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> LessonResponse:
    """
    Get detailed information about a specific lesson.

    - **lesson_id**: UUID of the lesson

    Returns lesson details including content, exercises, and user progress if authenticated.
    """
    service = LessonService(db)
    lesson = await service.get_lesson(lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    # Get user progress if authenticated
    user_progress = None
    if current_user:
        progress = await service.get_user_progress(current_user.id, lesson_id)
        if progress:
            user_progress = LessonProgressResponse.model_validate(progress)

    response_data = {
        "id": lesson.id,
        "title": lesson.title,
        "lesson_type": lesson.lesson_type,
        "jlpt_level": lesson.jlpt_level,
        "order_index": lesson.order_index,
        "content": lesson.content,
        "exercises": lesson.exercises,
        "estimated_duration": lesson.estimated_duration,
        "prerequisites": lesson.prerequisites,
        "is_published": lesson.is_published,
        "user_progress": user_progress,
    }

    return LessonResponse(**response_data)


@router.post("/{lesson_id}/complete", response_model=LessonCompleteResponse)
async def complete_lesson(
    lesson_id: UUID,
    request: LessonCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonCompleteResponse:
    """
    Mark a lesson as completed and record the score.

    - **lesson_id**: UUID of the lesson
    - **score**: Score achieved (0-100)
    - **time_spent**: Time spent in seconds

    Requires authentication. Awards XP points based on score.
    """
    service = LessonService(db)

    # Verify lesson exists
    lesson = await service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    # Record completion
    progress = await service.record_completion(
        user_id=current_user.id,
        lesson_id=lesson_id,
        score=request.score,
        time_spent=request.time_spent,
    )

    # Calculate XP earned
    xp_earned = 100 + request.score

    # Get user's total XP
    from app.models.progress import UserProgress
    from sqlalchemy import select

    query = select(UserProgress).where(UserProgress.user_id == current_user.id)
    result = await db.execute(query)
    user_progress = result.scalar_one_or_none()
    total_xp = user_progress.xp_points if user_progress else 0

    return LessonCompleteResponse(
        lesson_id=lesson_id,
        is_completed=progress.is_completed,
        score=progress.score or 0,
        time_spent=progress.time_spent,
        xp_earned=xp_earned,
        total_xp=total_xp,
    )


@router.post(
    "/{lesson_id}/exercises/{exercise_id}/submit", response_model=ExerciseResult
)
async def submit_exercise_answer(
    lesson_id: UUID,
    exercise_id: str,
    submission: ExerciseSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExerciseResult:
    """
    Submit an answer for a specific exercise.

    - **lesson_id**: UUID of the lesson
    - **exercise_id**: ID of the exercise within the lesson
    - **answer**: User's answer to the exercise

    Requires authentication. Returns whether the answer is correct with explanation.
    """
    service = LessonService(db)

    # Get lesson
    lesson = await service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    # Find exercise
    exercise = None
    for ex in lesson.exercises:
        if ex.get("id") == exercise_id:
            exercise = ex
            break

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    # Validate answer
    result = service.validate_exercise_answer(exercise, submission.answer)

    return ExerciseResult(**result)


@router.get("/recommended", response_model=List[LessonResponse])
async def get_recommended_lessons(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[LessonResponse]:
    """
    Get recommended lessons for the current user.

    - **limit**: Maximum number of recommendations (default: 10, max: 50)

    Requires authentication. Returns lessons at the user's current level
    that they haven't completed yet.
    """
    service = LessonService(db)
    recommendations = await service.get_recommended_lessons(
        user_id=current_user.id, limit=limit
    )

    # Convert to response models
    response_lessons = []
    for lesson in recommendations:
        # Get user progress
        progress = await service.get_user_progress(current_user.id, lesson.id)
        user_progress = None
        if progress:
            user_progress = LessonProgressResponse.model_validate(progress)

        response_data = {
            "id": lesson.id,
            "title": lesson.title,
            "lesson_type": lesson.lesson_type,
            "jlpt_level": lesson.jlpt_level,
            "order_index": lesson.order_index,
            "content": lesson.content,
            "exercises": lesson.exercises,
            "estimated_duration": lesson.estimated_duration,
            "prerequisites": lesson.prerequisites,
            "is_published": lesson.is_published,
            "user_progress": user_progress,
        }
        response_lessons.append(LessonResponse(**response_data))

    return response_lessons

"""
Lesson service for managing lessons and user progress.
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.progress import UserProgress


class LessonService:
    """Service for lesson operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize lesson service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_lessons(
        self,
        jlpt_level: Optional[str] = None,
        lesson_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
    ) -> List[Lesson]:
        """
        Get list of lessons with optional filtering.

        Args:
            jlpt_level: Filter by JLPT level (N5, N4, N3, N2, N1)
            lesson_type: Filter by lesson type
            skip: Number of lessons to skip (pagination)
            limit: Maximum number of lessons to return
            user_id: Optional user ID to include progress

        Returns:
            List of lessons
        """
        query = select(Lesson).where(Lesson.is_published == True)

        # Apply filters
        if jlpt_level:
            query = query.where(Lesson.jlpt_level == jlpt_level)
        if lesson_type:
            query = query.where(Lesson.lesson_type == lesson_type)

        # Order by JLPT level and order index
        query = query.order_by(Lesson.jlpt_level.desc(), Lesson.order_index.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        lessons = list(result.scalars().all())

        return lessons

    async def get_lessons_count(
        self,
        jlpt_level: Optional[str] = None,
        lesson_type: Optional[str] = None,
    ) -> int:
        """
        Get total count of lessons matching filters.

        Args:
            jlpt_level: Filter by JLPT level
            lesson_type: Filter by lesson type

        Returns:
            Total count of lessons
        """
        query = select(func.count(Lesson.id)).where(Lesson.is_published == True)

        if jlpt_level:
            query = query.where(Lesson.jlpt_level == jlpt_level)
        if lesson_type:
            query = query.where(Lesson.lesson_type == lesson_type)

        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count

    async def get_lesson(self, lesson_id: UUID) -> Optional[Lesson]:
        """
        Get a single lesson by ID.

        Args:
            lesson_id: Lesson UUID

        Returns:
            Lesson if found, None otherwise
        """
        query = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(query)
        lesson = result.scalar_one_or_none()
        return lesson

    async def create_lesson(self, lesson_data: Dict[str, Any]) -> Lesson:
        """
        Create a new lesson.

        Args:
            lesson_data: Dictionary containing lesson data

        Returns:
            Created lesson
        """
        lesson = Lesson(**lesson_data)
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def update_lesson(
        self, lesson_id: UUID, lesson_data: Dict[str, Any]
    ) -> Optional[Lesson]:
        """
        Update an existing lesson.

        Args:
            lesson_id: Lesson UUID
            lesson_data: Dictionary containing fields to update

        Returns:
            Updated lesson if found, None otherwise
        """
        lesson = await self.get_lesson(lesson_id)
        if not lesson:
            return None

        for key, value in lesson_data.items():
            if hasattr(lesson, key) and value is not None:
                setattr(lesson, key, value)

        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def get_user_progress(
        self, user_id: UUID, lesson_id: UUID
    ) -> Optional[LessonProgress]:
        """
        Get user's progress on a specific lesson.

        Args:
            user_id: User UUID
            lesson_id: Lesson UUID

        Returns:
            LessonProgress if exists, None otherwise
        """
        query = select(LessonProgress).where(
            and_(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()
        return progress

    async def record_completion(
        self,
        user_id: UUID,
        lesson_id: UUID,
        score: int,
        time_spent: int = 0,
    ) -> LessonProgress:
        """
        Record lesson completion for a user.

        Args:
            user_id: User UUID
            lesson_id: Lesson UUID
            score: Score achieved (0-100)
            time_spent: Time spent in seconds

        Returns:
            Updated or created LessonProgress
        """
        # Get or create lesson progress
        progress = await self.get_user_progress(user_id, lesson_id)

        if progress:
            # Update existing progress
            progress.is_completed = True
            progress.score = score
            progress.time_spent += time_spent
            if not progress.first_completed_at:
                progress.first_completed_at = datetime.utcnow()
            progress.last_accessed_at = datetime.utcnow()
        else:
            # Create new progress record
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                score=score,
                time_spent=time_spent,
                first_completed_at=datetime.utcnow(),
                last_accessed_at=datetime.utcnow(),
            )
            self.db.add(progress)

        await self.db.commit()
        await self.db.refresh(progress)

        # Update user's overall progress and award XP
        await self._update_user_xp(user_id, score)

        return progress

    async def _update_user_xp(self, user_id: UUID, score: int) -> None:
        """
        Update user's XP based on lesson completion.

        Args:
            user_id: User UUID
            score: Score achieved (0-100)
        """
        # Calculate XP: base 100 XP + score bonus
        xp_earned = 100 + score

        # Get or create user progress
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.db.execute(query)
        user_progress = result.scalar_one_or_none()

        if user_progress:
            user_progress.xp_points += xp_earned
        else:
            user_progress = UserProgress(
                user_id=user_id,
                xp_points=xp_earned,
            )
            self.db.add(user_progress)

        await self.db.commit()

    def validate_exercise_answer(
        self, exercise: Dict[str, Any], user_answer: str
    ) -> Dict[str, Any]:
        """
        Validate user's answer to an exercise.

        Args:
            exercise: Exercise data dictionary
            user_answer: User's submitted answer

        Returns:
            Dictionary with validation result
        """
        correct_answer = exercise.get("correct_answer", "")
        is_correct = user_answer.strip() == correct_answer.strip()

        result = {
            "correct": is_correct,
            "explanation": exercise.get("explanation", ""),
        }

        if not is_correct:
            result["correct_answer"] = correct_answer

        return result

    async def get_recommended_lessons(
        self, user_id: UUID, limit: int = 10
    ) -> List[Lesson]:
        """
        Get recommended lessons for a user based on their progress.

        Args:
            user_id: User UUID
            limit: Maximum number of recommendations

        Returns:
            List of recommended lessons
        """
        # Get user's current level
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.db.execute(query)
        user_progress = result.scalar_one_or_none()

        if user_progress:
            target_level = user_progress.current_level
        else:
            target_level = "N5"  # Default for new users

        # Get completed lesson IDs
        completed_query = select(LessonProgress.lesson_id).where(
            and_(
                LessonProgress.user_id == user_id,
                LessonProgress.is_completed == True,
            )
        )
        completed_result = await self.db.execute(completed_query)
        completed_ids = [row[0] for row in completed_result.fetchall()]

        # Get recommended lessons: published, at user's level, not completed
        recommendations_query = (
            select(Lesson)
            .where(
                and_(
                    Lesson.is_published == True,
                    Lesson.jlpt_level == target_level,
                    Lesson.id.not_in(completed_ids) if completed_ids else True,
                )
            )
            .order_by(Lesson.order_index.asc())
            .limit(limit)
        )

        recommendations_result = await self.db.execute(recommendations_query)
        recommendations = list(recommendations_result.scalars().all())

        return recommendations

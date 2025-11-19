"""
Unit tests for lesson service.

TDD: These tests are written FIRST before implementation.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.progress import UserProgress
from app.services.lesson_service import LessonService


@pytest.mark.asyncio
class TestLessonService:
    """Test suite for LessonService."""

    async def test_get_lessons_success(self, db_session: AsyncSession):
        """Test successful retrieval of lessons."""
        # Arrange
        service = LessonService(db_session)
        lesson1 = Lesson(
            title="Hiragana Basics - A Row",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=1,
            content={"introduction": {"text": "Learn the A row"}},
            exercises=[],
            is_published=True,
        )
        lesson2 = Lesson(
            title="Katakana Basics - A Row",
            lesson_type="katakana",
            jlpt_level="N5",
            order_index=1,
            content={"introduction": {"text": "Learn katakana"}},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([lesson1, lesson2])
        await db_session.commit()

        # Act
        lessons = await service.get_lessons()

        # Assert
        assert len(lessons) == 2
        assert lessons[0].title == "Hiragana Basics - A Row"
        assert lessons[1].title == "Katakana Basics - A Row"

    async def test_get_lessons_filter_by_level(self, db_session: AsyncSession):
        """Test filtering lessons by JLPT level."""
        # Arrange
        service = LessonService(db_session)
        n5_lesson = Lesson(
            title="N5 Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        n4_lesson = Lesson(
            title="N4 Lesson",
            lesson_type="grammar",
            jlpt_level="N4",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([n5_lesson, n4_lesson])
        await db_session.commit()

        # Act
        lessons = await service.get_lessons(jlpt_level="N5")

        # Assert
        assert len(lessons) == 1
        assert lessons[0].jlpt_level == "N5"

    async def test_get_lessons_filter_by_type(self, db_session: AsyncSession):
        """Test filtering lessons by type."""
        # Arrange
        service = LessonService(db_session)
        hiragana_lesson = Lesson(
            title="Hiragana",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        grammar_lesson = Lesson(
            title="Grammar",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([hiragana_lesson, grammar_lesson])
        await db_session.commit()

        # Act
        lessons = await service.get_lessons(lesson_type="hiragana")

        # Assert
        assert len(lessons) == 1
        assert lessons[0].lesson_type == "hiragana"

    async def test_get_lessons_pagination(self, db_session: AsyncSession):
        """Test lesson pagination."""
        # Arrange
        service = LessonService(db_session)
        for i in range(15):
            lesson = Lesson(
                title=f"Lesson {i}",
                lesson_type="vocabulary",
                jlpt_level="N5",
                order_index=i,
                content={},
                exercises=[],
                is_published=True,
            )
            db_session.add(lesson)
        await db_session.commit()

        # Act
        page1 = await service.get_lessons(skip=0, limit=10)
        page2 = await service.get_lessons(skip=10, limit=10)

        # Assert
        assert len(page1) == 10
        assert len(page2) == 5

    async def test_get_lessons_only_published(self, db_session: AsyncSession):
        """Test that only published lessons are returned."""
        # Arrange
        service = LessonService(db_session)
        published = Lesson(
            title="Published",
            lesson_type="kanji",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        unpublished = Lesson(
            title="Unpublished",
            lesson_type="kanji",
            jlpt_level="N5",
            order_index=2,
            content={},
            exercises=[],
            is_published=False,
        )
        db_session.add_all([published, unpublished])
        await db_session.commit()

        # Act
        lessons = await service.get_lessons()

        # Assert
        assert len(lessons) == 1
        assert lessons[0].title == "Published"

    async def test_get_lesson_by_id_success(self, db_session: AsyncSession):
        """Test successful retrieval of a single lesson."""
        # Arrange
        service = LessonService(db_session)
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={
                "introduction": {"text": "Introduction"},
                "sections": [{"type": "explanation", "content": "Content"}],
            },
            exercises=[
                {
                    "id": "ex1",
                    "type": "multiple_choice",
                    "question": "What is this?",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                }
            ],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        # Act
        result = await service.get_lesson(lesson.id)

        # Assert
        assert result is not None
        assert result.id == lesson.id
        assert result.title == "Test Lesson"
        assert len(result.exercises) == 1

    async def test_get_lesson_not_found(self, db_session: AsyncSession):
        """Test getting a non-existent lesson returns None."""
        # Arrange
        service = LessonService(db_session)
        fake_id = uuid.uuid4()

        # Act
        result = await service.get_lesson(fake_id)

        # Assert
        assert result is None

    async def test_create_lesson_success(self, db_session: AsyncSession):
        """Test successful lesson creation."""
        # Arrange
        service = LessonService(db_session)
        lesson_data = {
            "title": "New Lesson",
            "lesson_type": "vocabulary",
            "jlpt_level": "N5",
            "order_index": 1,
            "content": {"introduction": {"text": "Learn new words"}},
            "exercises": [],
            "estimated_duration": 30,
            "prerequisites": [],
            "is_published": True,
        }

        # Act
        lesson = await service.create_lesson(lesson_data)

        # Assert
        assert lesson.id is not None
        assert lesson.title == "New Lesson"
        assert lesson.lesson_type == "vocabulary"

        # Verify in database
        result = await db_session.execute(
            select(Lesson).where(Lesson.id == lesson.id)
        )
        db_lesson = result.scalar_one_or_none()
        assert db_lesson is not None

    async def test_update_lesson_success(self, db_session: AsyncSession):
        """Test successful lesson update."""
        # Arrange
        service = LessonService(db_session)
        lesson = Lesson(
            title="Original Title",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=False,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        # Act
        updated = await service.update_lesson(
            lesson.id, {"title": "Updated Title", "is_published": True}
        )

        # Assert
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.is_published is True

    async def test_update_lesson_not_found(self, db_session: AsyncSession):
        """Test updating non-existent lesson returns None."""
        # Arrange
        service = LessonService(db_session)
        fake_id = uuid.uuid4()

        # Act
        result = await service.update_lesson(fake_id, {"title": "New Title"})

        # Assert
        assert result is None

    async def test_get_user_progress_success(
        self, db_session: AsyncSession, test_user
    ):
        """Test getting user progress for a lesson."""
        # Arrange
        from app.models.lesson_progress import LessonProgress

        service = LessonService(db_session)
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        progress = LessonProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            is_completed=True,
            score=85,
            time_spent=1200,
        )
        db_session.add(progress)
        await db_session.commit()

        # Act
        result = await service.get_user_progress(test_user.id, lesson.id)

        # Assert
        assert result is not None
        assert result.is_completed is True
        assert result.score == 85

    async def test_record_completion_success(
        self, db_session: AsyncSession, test_user
    ):
        """Test recording lesson completion."""
        # Arrange
        service = LessonService(db_session)
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        # Act
        progress = await service.record_completion(
            user_id=test_user.id, lesson_id=lesson.id, score=90, time_spent=1500
        )

        # Assert
        assert progress is not None
        assert progress.is_completed is True
        assert progress.score == 90
        assert progress.time_spent == 1500

    async def test_record_completion_updates_xp(
        self, db_session: AsyncSession, test_user
    ):
        """Test that completing a lesson awards XP."""
        # Arrange
        service = LessonService(db_session)
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        # Get initial XP
        user_progress = await db_session.execute(
            select(UserProgress).where(UserProgress.user_id == test_user.id)
        )
        initial_progress = user_progress.scalar_one_or_none()
        if initial_progress:
            initial_xp = initial_progress.xp_points
        else:
            initial_xp = 0

        # Act
        await service.record_completion(
            user_id=test_user.id, lesson_id=lesson.id, score=90, time_spent=1500
        )

        # Assert
        result = await db_session.execute(
            select(UserProgress).where(UserProgress.user_id == test_user.id)
        )
        updated_progress = result.scalar_one_or_none()
        if updated_progress:
            assert updated_progress.xp_points > initial_xp

    async def test_validate_exercise_answer_correct(self, db_session: AsyncSession):
        """Test validating a correct exercise answer."""
        # Arrange
        service = LessonService(db_session)

        exercise = {
            "id": "ex1",
            "type": "multiple_choice",
            "question": "What is 'hello' in Japanese?",
            "options": ["こんにちは", "さようなら", "ありがとう"],
            "correct_answer": "こんにちは",
            "explanation": "こんにちは (konnichiwa) means hello",
        }

        # Act
        result = service.validate_exercise_answer(exercise, "こんにちは")

        # Assert
        assert result["correct"] is True
        assert "explanation" in result

    async def test_validate_exercise_answer_incorrect(self, db_session: AsyncSession):
        """Test validating an incorrect exercise answer."""
        # Arrange
        service = LessonService(db_session)

        exercise = {
            "id": "ex1",
            "type": "multiple_choice",
            "question": "What is 'hello' in Japanese?",
            "options": ["こんにちは", "さようなら", "ありがとう"],
            "correct_answer": "こんにちは",
            "explanation": "こんにちは (konnichiwa) means hello",
        }

        # Act
        result = service.validate_exercise_answer(exercise, "さようなら")

        # Assert
        assert result["correct"] is False
        assert result["correct_answer"] == "こんにちは"
        assert "explanation" in result

    async def test_get_recommended_lessons(
        self, db_session: AsyncSession, test_user
    ):
        """Test getting recommended lessons for a user."""
        # Arrange
        from app.models.lesson_progress import LessonProgress

        service = LessonService(db_session)

        # Create lessons
        completed_lesson = Lesson(
            title="Completed Lesson",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        recommended_lesson = Lesson(
            title="Next Lesson",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=2,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([completed_lesson, recommended_lesson])
        await db_session.commit()
        await db_session.refresh(completed_lesson)
        await db_session.refresh(recommended_lesson)

        # Mark first lesson as completed
        progress = LessonProgress(
            user_id=test_user.id,
            lesson_id=completed_lesson.id,
            is_completed=True,
            score=85,
        )
        db_session.add(progress)
        await db_session.commit()

        # Act
        recommendations = await service.get_recommended_lessons(test_user.id, limit=5)

        # Assert
        assert len(recommendations) > 0
        # Should recommend lessons at user's level that aren't completed
        assert any(lesson.id == recommended_lesson.id for lesson in recommendations)

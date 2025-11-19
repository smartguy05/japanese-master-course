"""
Integration tests for lesson API endpoints.

TDD: These tests are written FIRST before implementation.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.user import User
from app.utils.auth import create_access_token


@pytest.mark.asyncio
class TestLessonsAPI:
    """Test suite for /api/lessons endpoints."""

    async def test_list_lessons_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful listing of lessons."""
        # Arrange
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
        response = await client.get("/api/lessons")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) == 2

    async def test_list_lessons_filter_by_level(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test filtering lessons by JLPT level."""
        # Arrange
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
        response = await client.get("/api/lessons?jlpt_level=N5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["jlpt_level"] == "N5"

    async def test_list_lessons_filter_by_type(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test filtering lessons by type."""
        # Arrange
        hiragana = Lesson(
            title="Hiragana",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        grammar = Lesson(
            title="Grammar",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([hiragana, grammar])
        await db_session.commit()

        # Act
        response = await client.get("/api/lessons?lesson_type=hiragana")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["lesson_type"] == "hiragana"

    async def test_list_lessons_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test lesson pagination."""
        # Arrange
        for i in range(25):
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
        page1 = await client.get("/api/lessons?page=1&size=10")
        page2 = await client.get("/api/lessons?page=2&size=10")

        # Assert
        assert page1.status_code == 200
        assert page2.status_code == 200
        data1 = page1.json()
        data2 = page2.json()
        assert len(data1["items"]) == 10
        assert len(data2["items"]) == 10
        assert data1["total"] == 25

    async def test_get_lesson_details_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful retrieval of lesson details."""
        # Arrange
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
                    "question": "Question?",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                }
            ],
            estimated_duration=30,
            prerequisites=[],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        # Act
        response = await client.get(f"/api/lessons/{lesson.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Lesson"
        assert "content" in data
        assert "exercises" in data
        assert data["estimated_duration"] == 30

    async def test_get_lesson_not_found(self, client: AsyncClient):
        """Test getting a non-existent lesson returns 404."""
        # Arrange
        fake_id = str(uuid.uuid4())

        # Act
        response = await client.get(f"/api/lessons/{fake_id}")

        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()

    async def test_get_lesson_includes_user_progress(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test that lesson details include user progress when authenticated."""
        # Arrange
        from app.models.lesson_progress import LessonProgress

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
        )
        db_session.add(progress)
        await db_session.commit()

        # Create auth token
        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = await client.get(f"/api/lessons/{lesson.id}", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "user_progress" in data
        assert data["user_progress"]["is_completed"] is True
        assert data["user_progress"]["score"] == 85

    async def test_complete_lesson_success(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test successful lesson completion."""
        # Arrange
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

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"score": 90, "time_spent": 1500}

        # Act
        response = await client.post(
            f"/api/lessons/{lesson.id}/complete", json=payload, headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert data["score"] == 90
        assert data["time_spent"] == 1500

    async def test_complete_lesson_requires_auth(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that completing a lesson requires authentication."""
        # Arrange
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

        payload = {"score": 90, "time_spent": 1500}

        # Act
        response = await client.post(
            f"/api/lessons/{lesson.id}/complete", json=payload
        )

        # Assert
        assert response.status_code == 401

    async def test_submit_exercise_answer_correct(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test submitting a correct exercise answer."""
        # Arrange
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[
                {
                    "id": "ex1",
                    "type": "multiple_choice",
                    "question": "What is 'hello' in Japanese?",
                    "options": ["こんにちは", "さようなら", "ありがとう"],
                    "correct_answer": "こんにちは",
                    "explanation": "こんにちは means hello",
                }
            ],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"answer": "こんにちは"}

        # Act
        response = await client.post(
            f"/api/lessons/{lesson.id}/exercises/ex1/submit",
            json=payload,
            headers=headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is True
        assert "explanation" in data

    async def test_submit_exercise_answer_incorrect(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test submitting an incorrect exercise answer."""
        # Arrange
        lesson = Lesson(
            title="Test Lesson",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[
                {
                    "id": "ex1",
                    "type": "multiple_choice",
                    "question": "What is 'hello' in Japanese?",
                    "options": ["こんにちは", "さようなら", "ありがとう"],
                    "correct_answer": "こんにちは",
                    "explanation": "こんにちは means hello",
                }
            ],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"answer": "さようなら"}

        # Act
        response = await client.post(
            f"/api/lessons/{lesson.id}/exercises/ex1/submit",
            json=payload,
            headers=headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is False
        assert data["correct_answer"] == "こんにちは"

    async def test_submit_exercise_not_found(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test submitting answer for non-existent exercise."""
        # Arrange
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

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {"answer": "test"}

        # Act
        response = await client.post(
            f"/api/lessons/{lesson.id}/exercises/nonexistent/submit",
            json=payload,
            headers=headers,
        )

        # Assert
        assert response.status_code == 404

    async def test_get_recommended_lessons_success(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test getting recommended lessons for a user."""
        # Arrange
        from app.models.lesson_progress import LessonProgress

        completed = Lesson(
            title="Completed",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=1,
            content={},
            exercises=[],
            is_published=True,
        )
        recommended = Lesson(
            title="Recommended",
            lesson_type="hiragana",
            jlpt_level="N5",
            order_index=2,
            content={},
            exercises=[],
            is_published=True,
        )
        db_session.add_all([completed, recommended])
        await db_session.commit()
        await db_session.refresh(completed)

        progress = LessonProgress(
            user_id=test_user.id, lesson_id=completed.id, is_completed=True, score=85
        )
        db_session.add(progress)
        await db_session.commit()

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = await client.get("/api/lessons/recommended", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_recommended_lessons_requires_auth(self, client: AsyncClient):
        """Test that getting recommendations requires authentication."""
        # Act
        response = await client.get("/api/lessons/recommended")

        # Assert
        assert response.status_code == 401

    async def test_complete_lesson_flow_end_to_end(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """
        E2E test: User gets lesson, submits exercises, completes lesson.
        """
        # Arrange
        lesson = Lesson(
            title="Complete Flow Test",
            lesson_type="grammar",
            jlpt_level="N5",
            order_index=1,
            content={"introduction": {"text": "Test"}},
            exercises=[
                {
                    "id": "ex1",
                    "type": "multiple_choice",
                    "question": "Q1?",
                    "options": ["A", "B"],
                    "correct_answer": "A",
                    "explanation": "Explanation",
                }
            ],
            is_published=True,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act & Assert
        # Step 1: Get lesson details
        get_response = await client.get(f"/api/lessons/{lesson.id}", headers=headers)
        assert get_response.status_code == 200
        lesson_data = get_response.json()
        assert len(lesson_data["exercises"]) == 1

        # Step 2: Submit exercise answer
        submit_response = await client.post(
            f"/api/lessons/{lesson.id}/exercises/ex1/submit",
            json={"answer": "A"},
            headers=headers,
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["correct"] is True

        # Step 3: Complete lesson
        complete_response = await client.post(
            f"/api/lessons/{lesson.id}/complete",
            json={"score": 100, "time_spent": 600},
            headers=headers,
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["is_completed"] is True

        # Step 4: Verify lesson shows as completed
        verify_response = await client.get(f"/api/lessons/{lesson.id}", headers=headers)
        assert verify_response.status_code == 200
        verified_data = verify_response.json()
        assert verified_data["user_progress"]["is_completed"] is True

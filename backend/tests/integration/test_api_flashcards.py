"""
Integration tests for flashcard API endpoints.

These tests MUST be written BEFORE endpoint implementation (TDD).
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy import select

from app.models.flashcard import Flashcard
from app.models.review import ReviewHistory
from app.models.kanji import Kanji


@pytest.mark.asyncio
class TestFlashcardCreation:
    """Test flashcard creation endpoints."""

    async def test_create_flashcard_success(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji: Kanji,
        db_session
    ):
        """Test successful flashcard creation."""
        # Arrange
        payload = {
            "content_type": "kanji",
            "content_id": str(test_kanji.id)
        }

        # Act
        response = await authenticated_client.post("/api/flashcards", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["content_type"] == "kanji"
        assert data["content_id"] == str(test_kanji.id)
        assert data["ease_factor"] == 2.5
        assert data["interval_days"] == 0
        assert data["repetitions"] == 0
        assert data["correct_count"] == 0
        assert data["incorrect_count"] == 0

        # Verify in database
        query = select(Flashcard).where(Flashcard.id == data["id"])
        result = await db_session.execute(query)
        flashcard = result.scalar_one()
        assert flashcard is not None

    async def test_create_flashcard_duplicate(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji: Kanji,
        db_session
    ):
        """Test creating duplicate flashcard returns existing."""
        # Arrange - Create first flashcard
        flashcard = Flashcard(
            user_id=test_user_id,
            content_type="kanji",
            content_id=test_kanji.id,
            next_review=datetime.utcnow()
        )
        db_session.add(flashcard)
        await db_session.commit()

        payload = {
            "content_type": "kanji",
            "content_id": str(test_kanji.id)
        }

        # Act
        response = await authenticated_client.post("/api/flashcards", json=payload)

        # Assert
        assert response.status_code == 200  # Returns existing
        data = response.json()
        assert data["id"] == str(flashcard.id)

    async def test_create_flashcard_invalid_content_type(
        self,
        authenticated_client: AsyncClient
    ):
        """Test creating flashcard with invalid content type."""
        # Arrange
        payload = {
            "content_type": "invalid",
            "content_id": str(uuid4())
        }

        # Act
        response = await authenticated_client.post("/api/flashcards", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_create_flashcard_unauthenticated(self, client: AsyncClient):
        """Test creating flashcard without authentication."""
        # Arrange
        payload = {
            "content_type": "kanji",
            "content_id": str(uuid4())
        }

        # Act
        response = await client.post("/api/flashcards", json=payload)

        # Assert
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetDueCards:
    """Test retrieving due flashcards."""

    async def test_get_due_cards_empty(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str
    ):
        """Test getting due cards when none are due."""
        # Act
        response = await authenticated_client.get("/api/flashcards/due")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_due_cards_multiple(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test getting multiple due cards."""
        # Arrange - Create 5 due flashcards
        now = datetime.utcnow()
        for i, kanji in enumerate(test_kanji_list[:5]):
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type="kanji",
                content_id=kanji.id,
                next_review=now - timedelta(hours=i)  # All due
            )
            db_session.add(flashcard)
        await db_session.commit()

        # Act
        response = await authenticated_client.get("/api/flashcards/due?limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        # Should be sorted by next_review (oldest first)
        for i in range(len(data) - 1):
            assert data[i]["next_review"] <= data[i + 1]["next_review"]

    async def test_get_due_cards_with_limit(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test getting due cards with limit."""
        # Arrange - Create 10 due flashcards
        now = datetime.utcnow()
        for kanji in test_kanji_list[:10]:
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type="kanji",
                content_id=kanji.id,
                next_review=now - timedelta(hours=1)
            )
            db_session.add(flashcard)
        await db_session.commit()

        # Act
        response = await authenticated_client.get("/api/flashcards/due?limit=5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    async def test_get_due_cards_excludes_future(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji: Kanji,
        db_session
    ):
        """Test that future cards are excluded from due cards."""
        # Arrange - Create flashcard due tomorrow
        future_time = datetime.utcnow() + timedelta(days=1)
        flashcard = Flashcard(
            user_id=test_user_id,
            content_type="kanji",
            content_id=test_kanji.id,
            next_review=future_time
        )
        db_session.add(flashcard)
        await db_session.commit()

        # Act
        response = await authenticated_client.get("/api/flashcards/due")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


@pytest.mark.asyncio
class TestRecordReview:
    """Test recording flashcard reviews."""

    async def test_record_review_correct(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_flashcard: Flashcard,
        db_session
    ):
        """Test recording a correct review."""
        # Arrange
        flashcard_id = str(test_flashcard.id)
        payload = {
            "quality": 4,
            "time_spent": 15
        }

        # Act
        response = await authenticated_client.post(
            f"/api/flashcards/{flashcard_id}/review",
            json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quality"] == 4
        assert data["time_spent"] == 15
        assert data["is_correct"] is True
        assert data["new_repetitions"] == 1
        assert data["new_interval_days"] == 1
        assert "next_review_date" in data

        # Verify flashcard updated in database
        await db_session.refresh(test_flashcard)
        assert test_flashcard.repetitions == 1
        assert test_flashcard.interval_days == 1
        assert test_flashcard.correct_count == 1
        assert test_flashcard.last_reviewed is not None

        # Verify review history created
        query = select(ReviewHistory).where(
            ReviewHistory.flashcard_id == test_flashcard.id
        )
        result = await db_session.execute(query)
        review = result.scalar_one()
        assert review.quality == 4
        assert review.time_spent == 15

    async def test_record_review_incorrect(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_flashcard: Flashcard,
        db_session
    ):
        """Test recording an incorrect review."""
        # Arrange
        # Set flashcard to have some progress
        test_flashcard.repetitions = 3
        test_flashcard.interval_days = 15
        test_flashcard.ease_factor = 2.5
        await db_session.commit()

        flashcard_id = str(test_flashcard.id)
        payload = {
            "quality": 2,  # Incorrect
            "time_spent": 20
        }

        # Act
        response = await authenticated_client.post(
            f"/api/flashcards/{flashcard_id}/review",
            json=payload
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["quality"] == 2
        assert data["is_correct"] is False
        assert data["new_repetitions"] == 0  # Reset
        assert data["new_interval_days"] == 1  # Reset to 1 day

        # Verify flashcard reset in database
        await db_session.refresh(test_flashcard)
        assert test_flashcard.repetitions == 0
        assert test_flashcard.interval_days == 1
        assert test_flashcard.incorrect_count == 1

    async def test_record_review_invalid_quality(
        self,
        authenticated_client: AsyncClient,
        test_flashcard: Flashcard
    ):
        """Test recording review with invalid quality."""
        # Arrange
        flashcard_id = str(test_flashcard.id)
        payload = {
            "quality": 6,  # Invalid (max is 5)
            "time_spent": 10
        }

        # Act
        response = await authenticated_client.post(
            f"/api/flashcards/{flashcard_id}/review",
            json=payload
        )

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_record_review_nonexistent_flashcard(
        self,
        authenticated_client: AsyncClient
    ):
        """Test recording review for non-existent flashcard."""
        # Arrange
        fake_id = str(uuid4())
        payload = {
            "quality": 4,
            "time_spent": 10
        }

        # Act
        response = await authenticated_client.post(
            f"/api/flashcards/{fake_id}/review",
            json=payload
        )

        # Assert
        assert response.status_code == 404

    async def test_record_review_other_user_flashcard(
        self,
        authenticated_client: AsyncClient,
        other_user_flashcard: Flashcard
    ):
        """Test recording review for another user's flashcard."""
        # Arrange
        flashcard_id = str(other_user_flashcard.id)
        payload = {
            "quality": 4,
            "time_spent": 10
        }

        # Act
        response = await authenticated_client.post(
            f"/api/flashcards/{flashcard_id}/review",
            json=payload
        )

        # Assert
        assert response.status_code == 404  # Not found (user doesn't own it)


@pytest.mark.asyncio
class TestFlashcardStats:
    """Test flashcard statistics endpoint."""

    async def test_get_stats_no_data(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str
    ):
        """Test getting stats when user has no flashcards."""
        # Act
        response = await authenticated_client.get("/api/flashcards/stats")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_cards"] == 0
        assert data["cards_due_today"] == 0
        assert data["total_reviews"] == 0
        assert data["accuracy"] == 0.0

    async def test_get_stats_with_data(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test getting stats with flashcards and reviews."""
        # Arrange - Create flashcards
        now = datetime.utcnow()
        flashcards = []
        for i, kanji in enumerate(test_kanji_list[:5]):
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type="kanji",
                content_id=kanji.id,
                next_review=now - timedelta(hours=1) if i < 3 else now + timedelta(days=1),
                repetitions=i,
                correct_count=i * 2,
                incorrect_count=i
            )
            db_session.add(flashcard)
            flashcards.append(flashcard)
        await db_session.commit()

        # Create some review history
        for flashcard in flashcards[:3]:
            for quality in [4, 5]:
                review = ReviewHistory(
                    flashcard_id=flashcard.id,
                    user_id=test_user_id,
                    quality=quality,
                    time_spent=10,
                    reviewed_at=now - timedelta(hours=1)
                )
                db_session.add(review)
        await db_session.commit()

        # Act
        response = await authenticated_client.get("/api/flashcards/stats?period_days=7")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_cards"] == 5
        assert data["cards_due_today"] == 3
        assert data["total_reviews"] == 6
        assert data["correct_reviews"] == 6  # All quality 4 and 5
        assert data["accuracy"] == 1.0
        assert data["avg_quality"] > 4.0


@pytest.mark.asyncio
class TestFlashcardList:
    """Test flashcard listing endpoint."""

    async def test_list_flashcards_empty(
        self,
        authenticated_client: AsyncClient
    ):
        """Test listing flashcards when none exist."""
        # Act
        response = await authenticated_client.get("/api/flashcards")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["flashcards"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    async def test_list_flashcards_with_pagination(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test listing flashcards with pagination."""
        # Arrange - Create 25 flashcards
        for kanji in test_kanji_list[:25]:
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type="kanji",
                content_id=kanji.id,
                next_review=datetime.utcnow()
            )
            db_session.add(flashcard)
        await db_session.commit()

        # Act - Get first page
        response = await authenticated_client.get("/api/flashcards?limit=10&offset=0")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["flashcards"]) == 10
        assert data["total"] == 25
        assert data["limit"] == 10
        assert data["offset"] == 0
        assert data["has_more"] is True

        # Act - Get second page
        response = await authenticated_client.get("/api/flashcards?limit=10&offset=10")
        data = response.json()
        assert len(data["flashcards"]) == 10
        assert data["has_more"] is True

        # Act - Get third page
        response = await authenticated_client.get("/api/flashcards?limit=10&offset=20")
        data = response.json()
        assert len(data["flashcards"]) == 5
        assert data["has_more"] is False

    async def test_list_flashcards_filter_by_content_type(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test filtering flashcards by content type."""
        # Arrange - Create kanji and vocabulary flashcards
        for i, kanji in enumerate(test_kanji_list[:5]):
            content_type = "kanji" if i < 3 else "vocabulary"
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type=content_type,
                content_id=kanji.id,
                next_review=datetime.utcnow()
            )
            db_session.add(flashcard)
        await db_session.commit()

        # Act
        response = await authenticated_client.get("/api/flashcards?content_type=kanji")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["flashcards"]) == 3
        assert all(f["content_type"] == "kanji" for f in data["flashcards"])


@pytest.mark.asyncio
class TestCompleteReviewSession:
    """End-to-end test for complete review session."""

    async def test_complete_review_session(
        self,
        authenticated_client: AsyncClient,
        test_user_id: str,
        test_kanji_list: list[Kanji],
        db_session
    ):
        """Test complete review session from due cards to completion."""
        # Arrange - Create 5 due flashcards
        now = datetime.utcnow()
        for kanji in test_kanji_list[:5]:
            flashcard = Flashcard(
                user_id=test_user_id,
                content_type="kanji",
                content_id=kanji.id,
                next_review=now - timedelta(hours=1)
            )
            db_session.add(flashcard)
        await db_session.commit()

        # Step 1: Get due cards
        response = await authenticated_client.get("/api/flashcards/due?limit=5")
        assert response.status_code == 200
        due_cards = response.json()
        assert len(due_cards) == 5

        # Step 2: Review each card
        reviewed_count = 0
        for card in due_cards:
            review_payload = {
                "quality": 4,  # Good
                "time_spent": 10
            }
            response = await authenticated_client.post(
                f"/api/flashcards/{card['id']}/review",
                json=review_payload
            )
            assert response.status_code == 200
            reviewed_count += 1

        # Step 3: Verify no more due cards
        response = await authenticated_client.get("/api/flashcards/due")
        assert response.status_code == 200
        remaining_due = response.json()
        assert len(remaining_due) == 0

        # Step 4: Check stats
        response = await authenticated_client.get("/api/flashcards/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_reviews"] == 5
        assert stats["correct_reviews"] == 5
        assert stats["accuracy"] == 1.0

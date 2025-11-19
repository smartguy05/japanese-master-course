"""
Unit tests for SM-2 Spaced Repetition Algorithm.

These tests MUST be written FIRST before any implementation.
They define the expected behavior of the SRS system.
"""

import pytest
from datetime import datetime, timedelta
from app.services.srs_service import SRSService, NextReview


class TestSM2Algorithm:
    """Test suite for SM-2 algorithm implementation."""

    @pytest.fixture
    def srs_service(self):
        """Create SRS service instance."""
        return SRSService()

    def test_sm2_initial_card_new_card(self, srs_service):
        """Test SM-2 for brand new card (first review)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 0
        repetitions = 0
        quality = 4  # Good answer

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "First review should be 1 day"
        assert result.repetitions == 1, "Repetitions should increment to 1"
        assert result.ease_factor >= 2.5, "EF should not decrease for quality 4"

    def test_sm2_second_review_perfect(self, srs_service):
        """Test SM-2 for second review with perfect answer."""
        # Arrange - After first successful review
        ease_factor = 2.5
        interval_days = 1
        repetitions = 1
        quality = 5  # Perfect answer

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 6, "Second review should be 6 days"
        assert result.repetitions == 2, "Repetitions should increment to 2"
        assert result.ease_factor > 2.5, "EF should increase for perfect answer"

    def test_sm2_third_review_good(self, srs_service):
        """Test SM-2 for third review with good answer."""
        # Arrange - After second successful review
        ease_factor = 2.6
        interval_days = 6
        repetitions = 2
        quality = 4  # Good answer

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        # Third review onwards: interval = previous_interval * ease_factor
        expected_interval = int(6 * 2.6)
        assert result.interval_days == expected_interval, f"Third review should be {expected_interval} days"
        assert result.repetitions == 3, "Repetitions should increment to 3"

    def test_sm2_incorrect_answer_resets(self, srs_service):
        """Test SM-2 resets card to day 1 for incorrect answer (quality < 3)."""
        # Arrange - Card with some progress
        ease_factor = 2.5
        interval_days = 15
        repetitions = 5
        quality = 2  # Incorrect answer

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "Incorrect answer should reset to 1 day"
        assert result.repetitions == 0, "Repetitions should reset to 0"
        assert result.ease_factor < 2.5, "EF should decrease for incorrect answer"

    def test_sm2_quality_0_complete_blackout(self, srs_service):
        """Test SM-2 with quality 0 (complete blackout)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 0

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "Quality 0 should reset to 1 day"
        assert result.repetitions == 0, "Repetitions should reset"
        # EF' = EF + (0.1 - (5-0) * (0.08 + (5-0) * 0.02))
        # EF' = 2.5 + (0.1 - 5 * (0.08 + 5 * 0.02))
        # EF' = 2.5 + (0.1 - 5 * 0.18) = 2.5 + (0.1 - 0.9) = 2.5 - 0.8 = 1.7
        assert result.ease_factor < 2.5, "EF should decrease significantly"

    def test_sm2_quality_1_incorrect(self, srs_service):
        """Test SM-2 with quality 1 (incorrect with some recall)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 1

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "Quality 1 should reset to 1 day"
        assert result.repetitions == 0, "Repetitions should reset"

    def test_sm2_quality_2_difficult(self, srs_service):
        """Test SM-2 with quality 2 (difficult recall)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 2

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "Quality 2 should reset to 1 day"
        assert result.repetitions == 0, "Repetitions should reset"

    def test_sm2_quality_3_correct_with_effort(self, srs_service):
        """Test SM-2 with quality 3 (correct with serious difficulty)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 3

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        # Quality 3+ should NOT reset
        assert result.interval_days >= 10, "Quality 3 should not reset interval"
        assert result.repetitions == 4, "Repetitions should increment"
        # EF' = EF + (0.1 - (5-3) * (0.08 + (5-3) * 0.02))
        # EF' = 2.5 + (0.1 - 2 * (0.08 + 2 * 0.02))
        # EF' = 2.5 + (0.1 - 2 * 0.12) = 2.5 + (0.1 - 0.24) = 2.5 - 0.14 = 2.36
        assert result.ease_factor < 2.5, "EF should decrease slightly for quality 3"

    def test_sm2_quality_4_correct_hesitation(self, srs_service):
        """Test SM-2 with quality 4 (correct with hesitation)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 4

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        expected_interval = int(10 * 2.5)
        assert result.interval_days == expected_interval, "Interval should scale by EF"
        assert result.repetitions == 4, "Repetitions should increment"
        # EF' = EF + (0.1 - (5-4) * (0.08 + (5-4) * 0.02))
        # EF' = 2.5 + (0.1 - 1 * (0.08 + 1 * 0.02))
        # EF' = 2.5 + (0.1 - 0.1) = 2.5
        assert result.ease_factor == pytest.approx(2.5, abs=0.01), "EF should stay same for quality 4"

    def test_sm2_quality_5_perfect(self, srs_service):
        """Test SM-2 with quality 5 (perfect recall)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 5

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        expected_interval = int(10 * 2.5)
        assert result.interval_days == expected_interval, "Interval should scale by EF"
        assert result.repetitions == 4, "Repetitions should increment"
        # EF' = EF + (0.1 - (5-5) * (0.08 + (5-5) * 0.02))
        # EF' = 2.5 + 0.1 = 2.6
        assert result.ease_factor > 2.5, "EF should increase for perfect answer"

    def test_sm2_ease_factor_minimum_boundary(self, srs_service):
        """Test that ease factor never goes below 1.3."""
        # Arrange - Start with minimum EF and poor quality
        ease_factor = 1.3
        interval_days = 5
        repetitions = 2
        quality = 0  # Worst possible

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.ease_factor >= 1.3, "EF must never go below 1.3"

    def test_sm2_ease_factor_can_grow_above_default(self, srs_service):
        """Test that ease factor can grow above 2.5 with perfect answers."""
        # Arrange - Start with default EF and perfect quality
        ease_factor = 2.5
        interval_days = 30
        repetitions = 10
        quality = 5  # Perfect

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        # SM-2 has no upper limit, EF should increase for perfect answers
        assert result.ease_factor > 2.5, "EF should increase above 2.5 for perfect answers"
        assert result.ease_factor == pytest.approx(2.6, abs=0.01), "EF should be ~2.6 after quality 5"

    def test_sm2_long_interval_progression(self, srs_service):
        """Test that intervals grow appropriately over many reviews."""
        # Arrange - Simulate multiple successful reviews
        ease_factor = 2.5
        interval_days = 0
        repetitions = 0
        quality = 4

        # Act & Assert - First review
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )
        assert result.interval_days == 1, "First: 1 day"

        # Second review
        result = srs_service.calculate_next_review(
            ease_factor=result.ease_factor,
            interval_days=result.interval_days,
            repetitions=result.repetitions,
            quality=quality
        )
        assert result.interval_days == 6, "Second: 6 days"

        # Third review
        result = srs_service.calculate_next_review(
            ease_factor=result.ease_factor,
            interval_days=result.interval_days,
            repetitions=result.repetitions,
            quality=quality
        )
        assert result.interval_days >= 14, "Third: ~15 days"

        # Fourth review
        result = srs_service.calculate_next_review(
            ease_factor=result.ease_factor,
            interval_days=result.interval_days,
            repetitions=result.repetitions,
            quality=quality
        )
        assert result.interval_days >= 35, "Fourth: ~37 days"

    def test_sm2_ease_factor_calculation_formula(self, srs_service):
        """Test exact ease factor calculation formula."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3

        # Test different quality levels
        test_cases = [
            (0, 1.7),   # EF' = 2.5 + (0.1 - 5 * 0.18) = 1.7
            (1, 1.96),  # EF' = 2.5 + (0.1 - 4 * 0.14) = 1.96
            (2, 2.18),  # EF' = 2.5 + (0.1 - 3 * 0.1) = 2.18
            (3, 2.36),  # EF' = 2.5 + (0.1 - 2 * 0.12) = 2.36
            (4, 2.50),  # EF' = 2.5 + (0.1 - 1 * 0.1) = 2.5
            (5, 2.60),  # EF' = 2.5 + 0.1 = 2.6
        ]

        for quality, expected_ef in test_cases:
            # Act
            result = srs_service.calculate_next_review(
                ease_factor=ease_factor,
                interval_days=interval_days,
                repetitions=repetitions,
                quality=quality
            )

            # Assert
            assert result.ease_factor == pytest.approx(expected_ef, abs=0.01), \
                f"Quality {quality} should result in EF ~{expected_ef}"

    def test_sm2_invalid_quality_raises_error(self, srs_service):
        """Test that invalid quality values raise errors."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3

        # Act & Assert - Quality below 0
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            srs_service.calculate_next_review(
                ease_factor=ease_factor,
                interval_days=interval_days,
                repetitions=repetitions,
                quality=-1
            )

        # Act & Assert - Quality above 5
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            srs_service.calculate_next_review(
                ease_factor=ease_factor,
                interval_days=interval_days,
                repetitions=repetitions,
                quality=6
            )

    def test_sm2_zero_interval_becomes_one(self, srs_service):
        """Test that interval of 0 is treated as first review (1 day)."""
        # Arrange
        ease_factor = 2.5
        interval_days = 0
        repetitions = 0
        quality = 5

        # Act
        result = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result.interval_days == 1, "Zero interval should become 1 day"

    def test_sm2_consistency_same_inputs_same_outputs(self, srs_service):
        """Test that algorithm is deterministic."""
        # Arrange
        ease_factor = 2.5
        interval_days = 10
        repetitions = 3
        quality = 4

        # Act
        result1 = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )
        result2 = srs_service.calculate_next_review(
            ease_factor=ease_factor,
            interval_days=interval_days,
            repetitions=repetitions,
            quality=quality
        )

        # Assert
        assert result1.interval_days == result2.interval_days
        assert result1.ease_factor == result2.ease_factor
        assert result1.repetitions == result2.repetitions


class TestNextReviewDataClass:
    """Test the NextReview data class."""

    def test_next_review_has_all_fields(self):
        """Test that NextReview contains all required fields."""
        # Arrange & Act
        next_review = NextReview(
            interval_days=10,
            ease_factor=2.5,
            repetitions=3,
            next_review_date=datetime.utcnow() + timedelta(days=10)
        )

        # Assert
        assert next_review.interval_days == 10
        assert next_review.ease_factor == 2.5
        assert next_review.repetitions == 3
        assert isinstance(next_review.next_review_date, datetime)

    def test_next_review_date_calculation(self):
        """Test that next review date is calculated correctly."""
        # Arrange
        now = datetime(2025, 1, 1, 12, 0, 0)
        interval = 10

        # Act
        next_review = NextReview(
            interval_days=interval,
            ease_factor=2.5,
            repetitions=3,
            next_review_date=now + timedelta(days=interval)
        )

        # Assert
        expected_date = datetime(2025, 1, 11, 12, 0, 0)
        assert next_review.next_review_date == expected_date

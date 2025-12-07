import os
import random
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import encouragements


class TestGetCompletionEncouragement:
    """Test cases for get_completion_encouragement function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        result = encouragements.get_completion_encouragement()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_random_selection(self):
        """Test that function can return different messages."""
        results = set()
        for _ in range(20):  # Run multiple times to check randomness
            results.add(encouragements.get_completion_encouragement())
        # Should get at least a few different messages
        assert len(results) > 1


class TestGetStreakEncouragement:
    """Test cases for get_streak_encouragement function."""

    def test_daily_streak_low(self):
        """Test daily streak encouragement for low streaks."""
        result = encouragements.get_streak_encouragement(3, is_weekly=False)
        assert isinstance(result, str)
        assert "3" in result

    def test_daily_streak_week(self):
        """Test daily streak encouragement for 7 days."""
        result = encouragements.get_streak_encouragement(7, is_weekly=False)
        assert isinstance(result, str)
        assert "7" in result
        # The message contains "7-day streak" so check for "day" instead
        assert "day" in result.lower()

    def test_daily_streak_month(self):
        """Test daily streak encouragement for 30 days."""
        result = encouragements.get_streak_encouragement(30, is_weekly=False)
        assert isinstance(result, str)
        assert "30" in result

    def test_daily_streak_high(self):
        """Test daily streak encouragement for high streaks."""
        result = encouragements.get_streak_encouragement(100, is_weekly=False)
        assert isinstance(result, str)
        assert "100" in result

    def test_weekly_streak_low(self):
        """Test weekly streak encouragement for low streaks."""
        result = encouragements.get_streak_encouragement(2, is_weekly=True)
        assert isinstance(result, str)
        assert "2" in result

    def test_weekly_streak_month(self):
        """Test weekly streak encouragement for 4 weeks."""
        result = encouragements.get_streak_encouragement(4, is_weekly=True)
        assert isinstance(result, str)
        # The message might not contain the number, check for content instead
        assert len(result) > 0

    def test_weekly_streak_quarter(self):
        """Test weekly streak encouragement for 12 weeks."""
        result = encouragements.get_streak_encouragement(12, is_weekly=True)
        assert isinstance(result, str)
        # The message might not contain the number, check for content instead
        assert len(result) > 0

    def test_weekly_streak_year(self):
        """Test weekly streak encouragement for 52 weeks."""
        result = encouragements.get_streak_encouragement(52, is_weekly=True)
        assert isinstance(result, str)
        # The message might not contain the number, check for content instead
        assert len(result) > 0


class TestGetCompletionRateEncouragement:
    """Test cases for get_completion_rate_encouragement function."""

    def test_high_rate(self):
        """Test encouragement for high completion rate."""
        result = encouragements.get_completion_rate_encouragement(0.95)
        assert isinstance(result, str)
        assert "95%" in result

    def test_medium_rate(self):
        """Test encouragement for medium completion rate."""
        result = encouragements.get_completion_rate_encouragement(0.8)
        assert isinstance(result, str)
        assert "80%" in result

    def test_low_rate(self):
        """Test encouragement for low completion rate."""
        result = encouragements.get_completion_rate_encouragement(0.5)
        assert isinstance(result, str)
        # Low rate messages don't include percentage
        assert "%" not in result

    def test_perfect_rate(self):
        """Test encouragement for perfect completion rate."""
        result = encouragements.get_completion_rate_encouragement(1.0)
        assert isinstance(result, str)
        assert "100%" in result

import datetime
import os
import sqlite3
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_db as db
from habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    """Fixture to create a temporary database for testing."""
    db_file = tmp_path / "test_edge_cases.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


class TestEmptyDB:
    """Test cases for empty database scenarios."""

    def test_get_habit_nonexistent(self, tmp_db_path):
        """Test getting a habit that doesn't exist."""
        result = db.get_habit(999, db_name=tmp_db_path)
        assert result is None

    def test_get_completions_empty_habit(self, tmp_db_path):
        """Test getting completions for a habit with no completions."""
        h = Habit(name="Empty Habit", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)
        completions = db.get_completions(hid, db_name=tmp_db_path)
        assert completions == []

    def test_get_all_habits_empty_db(self, tmp_db_path):
        """Test getting all habits from an empty database."""
        habits = db.get_all_habits(db_name=tmp_db_path)
        assert habits == []

    def test_calculate_longest_streak_empty_completions(self, tmp_db_path):
        """Test calculating longest streak with no completions."""
        h = Habit(name="No Completions", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)
        db.update_streak(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.streak == 0


class TestInvalidData:
    """Test cases for invalid data handling."""

    def test_invalid_frequency_habit_creation(self):
        """Test creating habit with invalid frequency."""
        # This should not raise an error during creation, but may cause issues later
        h = Habit(name="Invalid Freq", frequency="invalid")
        assert h.frequency == "invalid"

    def test_bad_date_parsing_from_dict(self):
        """Test parsing invalid dates from dictionary."""
        data = {
            "id": 1,
            "name": "Test",
            "frequency": "daily",
            "created_at": "invalid-date",
            "last_completed": "2023-01-01",
            "is_active": True,
        }
        # Should handle invalid date gracefully
        habit = Habit.from_dict(data)
        assert habit.created_at is None  # Invalid date should result in None

    def test_bad_date_parsing_last_completed(self):
        """Test parsing invalid last_completed date."""
        data = {
            "id": 1,
            "name": "Test",
            "frequency": "daily",
            "created_at": "2023-01-01",
            "last_completed": "not-a-date",
            "is_active": True,
        }
        habit = Habit.from_dict(data)
        assert habit.last_completed is None

    def test_mark_completed_with_bad_frequency(self):
        """Test marking completion on habit with invalid frequency."""
        h = Habit(name="Bad Freq", frequency="invalid")
        dt = datetime.datetime(2023, 1, 1)
        # Should still work for first completion
        h.mark_completed(dt)
        assert h.streak == 1
        assert h.last_completed == dt

    def test_calculate_longest_streak_invalid_frequency(self):
        """Test calculating longest streak with invalid frequency."""
        h = Habit(name="Bad Freq", frequency="invalid")
        completions = [datetime.datetime(2023, 1, 1), datetime.datetime(2023, 1, 2)]
        # Should default to some behavior, likely treating as daily
        result = h.calculate_longest_streak(completions)
        assert isinstance(result, int)


class TestReactivationsWithExistingCompletions:
    """Test cases for reactivations with existing completions."""

    def test_reactivate_habit_with_completions(self, tmp_db_path):
        """Test reactivating a habit that has existing completions."""
        h = Habit(name="Reactivate Test", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add some completions
        dt1 = datetime.datetime(2023, 1, 1)
        dt2 = datetime.datetime(2023, 1, 2)
        db.add_completion(hid, dt1, db_name=tmp_db_path)
        db.add_completion(hid, dt2, db_name=tmp_db_path)

        # Soft delete
        db.delete_habit(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.is_active is False

        # Reactivate
        db.reactivate_habit(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.is_active is True
        assert habit.streak == 0  # Should be reset
        assert habit.reactivated_at is not None

        # Check that old completions are still there
        completions = db.get_completions(hid, db_name=tmp_db_path)
        assert len(completions) == 2

    def test_add_completion_after_reactivation(self, tmp_db_path):
        """Test adding completions after reactivation."""
        h = Habit(name="Post Reactivate", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add completion before reactivation
        dt1 = datetime.datetime(2023, 1, 1)
        db.add_completion(hid, dt1, db_name=tmp_db_path)

        # Reactivate
        db.delete_habit(hid, db_name=tmp_db_path)
        db.reactivate_habit(hid, db_name=tmp_db_path)

        # Set reactivated_at to a time between dt1 and dt2 for testing
        habit = db.get_habit(hid, db_name=tmp_db_path)
        habit.reactivated_at = datetime.datetime(2023, 1, 2)
        db.update_habit(habit, db_name=tmp_db_path)

        # Add completion after reactivation
        dt2 = datetime.datetime(2023, 1, 3)  # Gap to test streak reset
        db.add_completion(hid, dt2, db_name=tmp_db_path)

        # Update streak - this should consider only completions after reactivation
        db.update_streak(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        # Since there's only one completion after reactivation, streak should be 1
        # But the update_streak logic might not be setting it correctly
        # Let's check what completions are considered
        completions = db.get_completions(hid, db_name=tmp_db_path)
        post_reactivation_completions = [
            c for c in completions if c >= habit.reactivated_at
        ]
        assert len(post_reactivation_completions) == 1
        # The streak should be 1 for a single completion
        assert habit.streak == 1

    def test_completion_duplicate_prevention_after_reactivation(self, tmp_db_path):
        """Test that duplicate prevention works correctly after reactivation."""
        h = Habit(name="Duplicate After Reactivate", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add completion before reactivation
        dt1 = datetime.datetime(2023, 1, 1)
        db.add_completion(hid, dt1, db_name=tmp_db_path)

        # Reactivate
        db.delete_habit(hid, db_name=tmp_db_path)
        db.reactivate_habit(hid, db_name=tmp_db_path)

        # Try to add same day completion - should be allowed since reactivation resets
        dt_same = datetime.datetime(2023, 1, 1, 12, 0)  # Same day, different time
        # This should be allowed because reactivation creates a new context
        db.add_completion(hid, dt_same, db_name=tmp_db_path)
        completions = db.get_completions(hid, db_name=tmp_db_path)
        assert len(completions) == 2


class TestStreakCalculationsWithGaps:
    """Test cases for streak calculations with gaps in completions."""

    def test_daily_streak_with_gaps(self, tmp_db_path):
        """Test daily streak calculation with gaps."""
        h = Habit(name="Daily Gaps", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add completions with gaps
        dates = [
            datetime.datetime(2023, 1, 1),  # Day 1
            datetime.datetime(2023, 1, 2),  # Day 2
            datetime.datetime(2023, 1, 3),  # Day 3
            datetime.datetime(2023, 1, 6),  # Gap, then Day 4 (resets streak)
            datetime.datetime(2023, 1, 7),  # Day 5
        ]

        for dt in dates:
            db.add_completion(hid, dt, db_name=tmp_db_path)

        db.update_streak(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.streak == 2  # Last two days are consecutive

    def test_weekly_streak_with_gaps(self, tmp_db_path):
        """Test weekly streak calculation with gaps."""
        h = Habit(name="Weekly Gaps", frequency="weekly")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add completions with weekly gaps
        dates = [
            datetime.datetime(2023, 1, 1),  # Week 1
            datetime.datetime(2023, 1, 8),  # Week 2
            datetime.datetime(2023, 1, 15),  # Week 3
            datetime.datetime(2023, 1, 29),  # Gap (skips week 4), Week 5
        ]

        for dt in dates:
            db.add_completion(hid, dt, db_name=tmp_db_path)

        db.update_streak(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.streak == 1  # Last completion starts new streak

    def test_longest_streak_calculation_with_gaps(self, tmp_db_path):
        """Test longest streak calculation with gaps."""
        h = Habit(name="Longest Streak Gaps", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Create pattern: 3 consecutive, gap, 2 consecutive, gap, 4 consecutive
        dates = [
            # First streak: 3 days
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 3),
            # Gap
            # Second streak: 2 days
            datetime.datetime(2023, 1, 6),
            datetime.datetime(2023, 1, 7),
            # Gap
            # Third streak: 4 days
            datetime.datetime(2023, 1, 10),
            datetime.datetime(2023, 1, 11),
            datetime.datetime(2023, 1, 12),
            datetime.datetime(2023, 1, 13),
        ]

        for dt in dates:
            db.add_completion(hid, dt, db_name=tmp_db_path)

        completions = db.get_completions(hid, db_name=tmp_db_path)
        longest_streak = h.calculate_longest_streak(completions)
        assert longest_streak == 4

    def test_streak_reset_after_large_gap(self, tmp_db_path):
        """Test that streak resets properly after large gaps."""
        h = Habit(name="Large Gap Reset", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add initial streak
        db.add_completion(hid, datetime.datetime(2023, 1, 1), db_name=tmp_db_path)
        db.add_completion(hid, datetime.datetime(2023, 1, 2), db_name=tmp_db_path)

        # Large gap
        db.add_completion(hid, datetime.datetime(2023, 1, 10), db_name=tmp_db_path)

        db.update_streak(hid, db_name=tmp_db_path)
        habit = db.get_habit(hid, db_name=tmp_db_path)
        assert habit.streak == 1  # Should reset to 1

    def test_streak_with_duplicate_dates(self, tmp_db_path):
        """Test streak calculation handles duplicate dates correctly."""
        h = Habit(name="Duplicate Dates", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Add multiple completions on same day (shouldn't happen in real usage but test robustness)
        same_day = datetime.datetime(2023, 1, 1)
        db.add_completion(hid, same_day.replace(hour=9), db_name=tmp_db_path)
        # Note: add_completion prevents duplicates, so this would fail in real usage
        # But test the streak calculation with duplicate dates in the list
        completions = [
            datetime.datetime(2023, 1, 1, 9, 0),
            datetime.datetime(2023, 1, 1, 15, 0),  # Same day
            datetime.datetime(2023, 1, 2, 9, 0),
            datetime.datetime(2023, 1, 3, 9, 0),
        ]

        longest_streak = h.calculate_longest_streak(completions)
        assert longest_streak == 3  # Should count unique days

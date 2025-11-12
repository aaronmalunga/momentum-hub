import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from habit import Habit

@pytest.fixture
def sample_habit():
    """Fixture to create a sample Habit instance for testing."""
    return Habit(
        id=1,
        name="Test Habit",
        frequency="daily",
        notes="Test notes",
        reminder_time="08:00",
        evening_reminder_time="20:00",
        streak=0,
        created_at=datetime.datetime(2023, 1, 1),
        last_completed=None,
        is_active=True
    )

class TestHabitEdit:
    def test_edit_habit_name(self, sample_habit):
        sample_habit.edit_habit(name="New Name")
        assert sample_habit.name == "New Name"

    def test_edit_habit_frequency(self, sample_habit):
        sample_habit.edit_habit(frequency="weekly")
        assert sample_habit.frequency == "weekly"

    def test_edit_habit_notes(self, sample_habit):
        sample_habit.edit_habit(notes="Updated notes")
        assert sample_habit.notes == "Updated notes"

    def test_edit_habit_reminder_times(self, sample_habit):
        sample_habit.edit_habit(reminder_time="09:00", evening_reminder_time="21:00")
        assert sample_habit.reminder_time == "09:00"
        assert sample_habit.evening_reminder_time == "21:00"

    def test_edit_habit_no_changes(self, sample_habit):
        original_name = sample_habit.name
        sample_habit.edit_habit()
        assert sample_habit.name == original_name

class TestHabitMarkCompleted:
    def test_mark_completed_first_time(self, sample_habit):
        dt = datetime.datetime(2023, 1, 2, 10, 0)
        sample_habit.mark_completed(dt)
        assert sample_habit.streak == 1
        assert sample_habit.last_completed == dt

    def test_mark_completed_consecutive_daily(self, sample_habit):
        # First completion
        dt1 = datetime.datetime(2023, 1, 2, 10, 0)
        sample_habit.mark_completed(dt1)
        assert sample_habit.streak == 1

        # Consecutive day
        dt2 = datetime.datetime(2023, 1, 3, 10, 0)
        sample_habit.mark_completed(dt2)
        assert sample_habit.streak == 2

    def test_mark_completed_non_consecutive_daily(self, sample_habit):
        # First completion
        dt1 = datetime.datetime(2023, 1, 2, 10, 0)
        sample_habit.mark_completed(dt1)
        assert sample_habit.streak == 1

        # Skip a day
        dt3 = datetime.datetime(2023, 1, 4, 10, 0)
        sample_habit.mark_completed(dt3)
        assert sample_habit.streak == 1  # Reset

    def test_mark_completed_weekly_consecutive(self, sample_habit):
        sample_habit.frequency = "weekly"
        # First completion
        dt1 = datetime.datetime(2023, 1, 2, 10, 0)  # Monday
        sample_habit.mark_completed(dt1)
        assert sample_habit.streak == 1

        # Within same week (Thursday)
        dt2 = datetime.datetime(2023, 1, 5, 10, 0)
        sample_habit.mark_completed(dt2)
        assert sample_habit.streak == 2

    def test_mark_completed_weekly_non_consecutive(self, sample_habit):
        sample_habit.frequency = "weekly"
        # First completion
        dt1 = datetime.datetime(2023, 1, 2, 10, 0)
        sample_habit.mark_completed(dt1)
        assert sample_habit.streak == 1

        # Next week (exactly 7 days later)
        dt3 = datetime.datetime(2023, 1, 9, 10, 0)
        sample_habit.mark_completed(dt3)
        assert sample_habit.streak == 2  # Continue streak

    def test_mark_completed_default_now(self, sample_habit):
        before = datetime.datetime.now()
        sample_habit.mark_completed()
        after = datetime.datetime.now()
        assert before <= sample_habit.last_completed <= after
        assert sample_habit.streak == 1

class TestHabitCalculateLongestStreak:
    def test_calculate_longest_streak_empty(self, sample_habit):
        assert sample_habit.calculate_longest_streak([]) == 0

    def test_calculate_longest_streak_single(self, sample_habit):
        completions = [datetime.datetime(2023, 1, 2, 10, 0)]
        assert sample_habit.calculate_longest_streak(completions) == 1

    def test_calculate_longest_streak_daily_consecutive(self, sample_habit):
        completions = [
            datetime.datetime(2023, 1, 1, 10, 0),
            datetime.datetime(2023, 1, 2, 10, 0),
            datetime.datetime(2023, 1, 3, 10, 0),
            datetime.datetime(2023, 1, 5, 10, 0),  # Break
            datetime.datetime(2023, 1, 6, 10, 0)
        ]
        assert sample_habit.calculate_longest_streak(completions) == 3

    def test_calculate_longest_streak_weekly(self, sample_habit):
        sample_habit.frequency = "weekly"
        completions = [
            datetime.datetime(2023, 1, 1, 10, 0),  # Week 1
            datetime.datetime(2023, 1, 8, 10, 0),  # Week 2
            datetime.datetime(2023, 1, 15, 10, 0),  # Week 3
            datetime.datetime(2023, 1, 22, 10, 0),  # Week 4
            datetime.datetime(2023, 1, 30, 10, 0)   # Break >7 days
        ]
        assert sample_habit.calculate_longest_streak(completions) == 4

    def test_calculate_longest_streak_duplicates_same_day(self, sample_habit):
        completions = [
            datetime.datetime(2023, 1, 1, 10, 0),
            datetime.datetime(2023, 1, 1, 12, 0),  # Same day
            datetime.datetime(2023, 1, 2, 10, 0)
        ]
        assert sample_habit.calculate_longest_streak(completions) == 2

    def test_calculate_longest_streak_weekly_edge_cases(self, sample_habit):
        sample_habit.frequency = "weekly"
        completions = [
            datetime.datetime(2023, 1, 1, 10, 0),  # Sunday
            datetime.datetime(2023, 1, 8, 10, 0),  # Next Sunday
            datetime.datetime(2023, 1, 9, 10, 0),  # Monday same week
        ]
        assert sample_habit.calculate_longest_streak(completions) == 3  # All in same week or consecutive

    def test_from_dict_invalid_date(self):
        data = {
            'id': 1,
            'name': 'Test',
            'frequency': 'daily',
            'created_at': 'invalid-date',
            'last_completed': '2023-01-01',
            'is_active': True
        }
        habit = Habit.from_dict(data)
        assert habit.created_at is None  # Invalid date should result in None
        assert habit.last_completed is not None

    def test_from_dict_missing_keys(self):
        data = {'name': 'Test', 'frequency': 'daily'}
        habit = Habit.from_dict(data)
        assert habit.id is None
        assert habit.name == 'Test'
        assert habit.streak == 0

    def test_to_dict_complete(self, sample_habit):
        data = sample_habit.to_dict()
        assert 'id' in data
        assert 'name' in data
        assert data['name'] == 'Test Habit'
        assert data['is_active'] is True

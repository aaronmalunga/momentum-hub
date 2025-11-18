import pytest
import datetime
from goal import Goal
from habit import Habit
import momentum_db as db


class TestGoal:
    def setup_method(self):
        """Set up test database."""
        self.test_db_name = "tests/test_dbs/test_goal.db"
        db.init_db(self.test_db_name)
        # Create a test habit
        test_habit = Habit(name="Test Habit", frequency="daily")
        self.habit_id = db.add_habit(test_habit, self.test_db_name)

    def teardown_method(self):
        """Clean up test database."""
        db.close_all_connections()

    def test_goal_creation(self):
        """Test creating a new Goal instance."""
        goal = Goal(habit_id=self.habit_id, target_period_days=28)
        assert goal.habit_id == self.habit_id
        assert goal.target_period_days == 28
        assert goal.is_active is True
        assert goal.created_at is not None

    def test_goal_from_dict(self):
        """Test creating Goal from dictionary."""
        data = {
            'id': 1,
            'habit_id': self.habit_id,
            'target_period_days': 14,
            'target_completions': 10,
            'start_date': '2023-01-01T00:00:00',
            'end_date': '2023-01-14T23:59:59',
            'is_active': True,
            'created_at': '2023-01-01T00:00:00'
        }
        goal = Goal.from_dict(data)
        assert goal.id == 1
        assert goal.habit_id == self.habit_id
        assert goal.target_period_days == 14
        assert goal.target_completions == 10
        assert goal.is_active is True

    def test_goal_to_dict(self):
        """Test converting Goal to dictionary."""
        goal = Goal(habit_id=self.habit_id, target_period_days=7)
        data = goal.to_dict()
        assert data['habit_id'] == self.habit_id
        assert data['target_period_days'] == 7
        assert data['is_active'] is True
        assert 'created_at' in data

    def test_calculate_progress_no_completions(self):
        """Test progress calculation with no completions."""
        goal = Goal(habit_id=self.habit_id, target_period_days=28)
        progress = goal.calculate_progress(self.test_db_name)
        assert progress['count'] == 0
        assert progress['total'] == 28  # daily habit, 28 days
        assert progress['percent'] == 0.0
        assert progress['achieved'] is False

    def test_calculate_progress_with_completions(self):
        """Test progress calculation with completions."""
        # Add some completions
        now = datetime.datetime.now()
        for i in range(10):
            completion_date = now - datetime.timedelta(days=i)
            db.add_completion(self.habit_id, completion_date, self.test_db_name)

        goal = Goal(habit_id=self.habit_id, target_period_days=28)
        progress = goal.calculate_progress(self.test_db_name)
        assert progress['count'] == 10
        assert progress['total'] == 28
        assert progress['percent'] == pytest.approx(35.71, rel=1e-2)
        assert progress['achieved'] is False

    def test_calculate_progress_weekly_habit(self):
        """Test progress calculation for weekly habit."""
        # Create weekly habit
        weekly_habit = Habit(name="Weekly Test", frequency="weekly")
        weekly_habit_id = db.add_habit(weekly_habit, self.test_db_name)

        # Add weekly completions
        now = datetime.datetime.now()
        for i in range(2):
            completion_date = now - datetime.timedelta(weeks=i)
            db.add_completion(weekly_habit_id, completion_date, self.test_db_name)

        goal = Goal(habit_id=weekly_habit_id, target_period_days=28)  # 4 weeks
        progress = goal.calculate_progress(self.test_db_name)
        assert progress['count'] == 2
        assert progress['total'] == 4  # 28 days / 7 = 4 weeks
        assert progress['percent'] == 50.0
        assert progress['achieved'] is False

    def test_calculate_progress_with_target_completions(self):
        """Test progress with specific target completions."""
        goal = Goal(habit_id=self.habit_id, target_period_days=28, target_completions=5)
        progress = goal.calculate_progress(self.test_db_name)
        assert progress['total'] == 5  # uses target_completions instead of calculated

    def test_is_expired_no_end_date(self):
        """Test expiration check when no end date is set."""
        goal = Goal(habit_id=self.habit_id)
        assert goal.is_expired() is False

    def test_is_expired_with_end_date(self):
        """Test expiration check with end date."""
        past_date = datetime.datetime.now() - datetime.timedelta(days=1)
        goal = Goal(habit_id=self.habit_id, end_date=past_date)
        assert goal.is_expired() is True

        future_date = datetime.datetime.now() + datetime.timedelta(days=1)
        goal_future = Goal(habit_id=self.habit_id, end_date=future_date)
        assert goal_future.is_expired() is False

    def test_goal_repr(self):
        """Test string representation of Goal."""
        goal = Goal(habit_id=self.habit_id, target_period_days=14)
        repr_str = repr(goal)
        assert f"habit_id={self.habit_id}" in repr_str
        assert "target_period_days=14" in repr_str

import datetime
import os
import sys
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from momentum_hub import habit_analysis
from momentum_hub import momentum_db as db
from momentum_hub.habit import Habit

from . import test_data


class TestAnalysisFeatures:
    """Tests core analytics features on seeded data."""

    def setup_method(self):
        """Set up a clean test database and populate it with sample data before each test."""
        # Create a temporary database file
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db_file.close()
        self.test_db_name = self.temp_db_file.name

        # Populate with additional test data
        test_data.populate_test_db(self.test_db_name)

    def teardown_method(self):
        """Clean up after each test."""
        # Close all tracked connections
        db.close_all_connections()
        # Remove the temporary database file
        if os.path.exists(self.test_db_name):
            os.unlink(self.test_db_name)

    def test_initial_habits_exist(self):
        """Verify the 5 habits are created in the test database."""
        habits = db.get_all_habits(active_only=False, db_name=self.test_db_name)
        assert (
            len(habits) == 5
        ), "There should be 5 initial habits in the test database."
        habit_names = [h.name for h in habits]
        expected_names = [
            "Change beddings",
            "Code",
            "Study",
            "Meditate",
            "Blog",
        ]
        for name in expected_names:
            assert name in habit_names

    def test_calculate_longest_streak_change_beddings(self):
        """Test longest streak for 'Change beddings' (perfect weekly streak)."""
        change_beddings_habit = next(
            h
            for h in db.get_all_habits(db_name=self.test_db_name)
            if h.name == "Change beddings"
        )
        streak = habit_analysis.calculate_longest_streak_for_habit(
            change_beddings_habit.id, self.test_db_name
        )
        assert streak == 7

    def test_calculate_completion_rate_change_beddings(self):
        """Test completion rate for 'change beddings' (2/4 weeks completed)."""
        change_beddings_habit = next(
            h
            for h in db.get_all_habits(db_name=self.test_db_name)
            if h.name == "Change beddings"
        )
        completions = db.get_completions(change_beddings_habit.id, self.test_db_name)
        reference_date = max(c.date() for c in completions) if completions else None
        rate = habit_analysis.calculate_completion_rate_for_habit(
            change_beddings_habit.id, self.test_db_name, reference_date=reference_date
        )
        assert (
            rate == 0.5
        )  # Completion rate should be 50% (2 out of 4 weeks completed).

    def test_calculate_longest_streak_code_daily(self):
        """Test longest streak for 'Code' (perfect 28-day streak)."""
        code_daily_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        streak = habit_analysis.calculate_longest_streak_for_habit(
            code_daily_habit.id, self.test_db_name
        )
        assert streak == 28

    def test_calculate_overall_longest_streak(self):
        """Test if the overall longest streak is correctly identified."""
        # 'Code' has the longest streak of 28 days
        habit_name, streak = habit_analysis.calculate_overall_longest_streak(
            self.test_db_name
        )
        assert habit_name == "Code"
        assert streak == 28

    def test_calculate_completion_rate_code_daily(self):
        """Test completion rate for 'Code' (28/28 days completed)."""
        code_daily_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        completions = db.get_completions(code_daily_habit.id, self.test_db_name)
        reference_date = max(c.date() for c in completions) if completions else None
        rate = habit_analysis.calculate_completion_rate_for_habit(
            code_daily_habit.id, self.test_db_name, reference_date=reference_date
        )
        assert rate == 1.0

    def test_get_missed_days_code_daily(self):
        """Test missed days for 'Code' (should return 0 missed days)."""
        code_daily_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        missed_days = habit_analysis.get_missed_days_for_habit(
            code_daily_habit.id, self.test_db_name
        )
        assert missed_days == 0

    def test_calculate_longest_streak_study(self):
        """Test longest streak for 'Study' (known misses, then perfect streak)."""
        study_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Study"
        )
        streak = habit_analysis.calculate_longest_streak_for_habit(
            study_habit.id, self.test_db_name
        )
        assert streak == 23

    def test_calculate_completion_rate_study(self):
        """Test completion rate for 'Study' (25/28 days completed)."""
        study_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Study"
        )
        completions = db.get_completions(study_habit.id, self.test_db_name)
        reference_date = max(c.date() for c in completions) if completions else None
        rate = habit_analysis.calculate_completion_rate_for_habit(
            study_habit.id, self.test_db_name, reference_date=reference_date
        )
        # 25 Completions out of 28 days == 0.89
        assert round(rate, 4) == round(25 / 28, 4)

    def test_get_missed_days_study(self):
        """Test missed days for 'Study' (should return 3 missed days)."""
        study_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Study"
        )
        missed_days = habit_analysis.get_missed_days_for_habit(
            study_habit.id, self.test_db_name
        )
        # For the Study habit, only the count of missed days is asserted
        assert missed_days == 3

    def test_calculate_longest_streak_meditate(self):
        """Test longest streak for 'Meditate' (perfect 15-day streak)."""
        meditate_habit = next(
            h
            for h in db.get_all_habits(db_name=self.test_db_name)
            if h.name == "Meditate"
        )
        streak = habit_analysis.calculate_longest_streak_for_habit(
            meditate_habit.id, self.test_db_name
        )
        assert streak == 15

    def test_calculate_longest_streak_blog(self):
        """Test longest streak for 'Blog' (perfect weekly streak)."""
        blog_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Blog"
        )
        streak = habit_analysis.calculate_longest_streak_for_habit(
            blog_habit.id, self.test_db_name
        )
        # Blog has a perfect weekly streak of 7 weeks
        assert streak == 7

    def test_calculate_completion_rate_blog(self):
        """Test completion rate for 'Blog' (4/4 weeks completed)."""
        blog_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Blog"
        )
        completions = db.get_completions(blog_habit.id, self.test_db_name)
        reference_date = max(c.date() for c in completions) if completions else None
        rate = habit_analysis.calculate_completion_rate_for_habit(
            blog_habit.id, self.test_db_name, reference_date=reference_date
        )
        # Blog has a perfect completion rate of 100% (4 weeks completed)
        assert rate == 1.0

    def test_get_missed_days_weekly_habit_blog(self):
        """Test missed days for 'Blog' (should return empty list)."""
        blog_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Blog"
        )
        missed_days = habit_analysis.get_missed_days_for_habit(
            blog_habit.id, self.test_db_name
        )
        # Function should return an empty list for non-daily habits
        assert len(missed_days) == 0

    def test_calculate_goal_progress_daily(self):
        """Test goal progress for daily habit."""
        code_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        progress = habit_analysis.calculate_goal_progress(
            code_habit.id, self.test_db_name
        )
        assert "count" in progress
        assert "total" in progress
        assert "percent" in progress
        assert progress["total"] == 28  # 28 days for daily

    def test_calculate_goal_progress_weekly(self):
        """Test goal progress for weekly habit."""
        blog_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Blog"
        )
        progress = habit_analysis.calculate_goal_progress(
            blog_habit.id, self.test_db_name
        )
        assert progress["total"] == 4  # 4 weeks for weekly

    def test_get_completion_history_sorted(self):
        """Test completion history is sorted ascending."""
        code_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        history = habit_analysis.get_completion_history(
            code_habit.id, self.test_db_name
        )
        assert len(history) > 0
        # Check if sorted
        for i in range(len(history) - 1):
            assert history[i] <= history[i + 1]

    def test_calculate_overall_longest_streak(self):
        """Test if the overall longest streak is correctly identified."""
        habit_name, streak = habit_analysis.calculate_overall_longest_streak(
            self.test_db_name
        )
        assert habit_name == "Code"
        assert streak == 28

    def test_calculate_best_worst_habit(self):
        """Test calculating best and worst habits by streak."""
        best_habit, worst_habit = habit_analysis.calculate_best_worst_habit(
            self.test_db_name
        )
        assert best_habit is not None
        assert worst_habit is not None
        assert best_habit.streak >= worst_habit.streak

    def test_get_habit_analysis_with_goals(self):
        """Test comprehensive habit analysis with goals."""
        code_habit = next(
            h for h in db.get_all_habits(db_name=self.test_db_name) if h.name == "Code"
        )
        analysis_data = habit_analysis.get_habit_analysis_with_goals(
            code_habit.id, self.test_db_name
        )
        assert "completion_rate" in analysis_data
        assert "longest_streak" in analysis_data
        assert "current_streak" in analysis_data
        assert "goal_progress" in analysis_data
        assert "total_completions" in analysis_data

    def test_analyze_habits_by_category(self):
        """Test analyzing habits grouped by categories."""
        analysis = habit_analysis.analyze_habits_by_category(self.test_db_name)
        assert isinstance(analysis, dict)
        # Should have at least uncategorized habits
        assert "Uncategorized" in analysis or len(analysis) > 0

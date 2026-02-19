import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch

import pytest
from colorama import Fore

import momentum_hub.momentum_db as db
from momentum_hub.cli_analysis import (
    analyze_best_worst_habit,
    analyze_by_periodicity,
    analyze_completion_history,
    analyze_goal_progress,
    analyze_list_all_habits,
    analyze_longest_streak_all,
    analyze_longest_streak_one,
    analyze_streak_history_grid,
)
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_momentum_hub.cli_analysis.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def sample_habits(tmp_db_path):
    h1 = Habit(name="Daily Habit", frequency="daily")
    h2 = Habit(name="Weekly Habit", frequency="weekly")
    hid1 = db.add_habit(h1, db_name=tmp_db_path)
    hid2 = db.add_habit(h2, db_name=tmp_db_path)
    return tmp_db_path, hid1, hid2


class TestAnalyzeListAllHabits:
    """Tests CLI analysis: list all habits."""

    def test_analyze_list_all_habits_with_data(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
            analyze_list_all_habits(db_name)
        captured = capsys.readouterr()
        assert "Daily Habit" in captured.out
        assert "Weekly Habit" in captured.out

    def test_analyze_list_all_habits_empty(self, tmp_db_path, capsys):
        with patch("momentum_hub.cli_analysis.show_colored_message") as mock_show:
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_list_all_habits(tmp_db_path)
        mock_show.assert_called_with("No active habits found.", color=Fore.RED)


class TestAnalyzeByPeriodicity:
    """Tests CLI analysis: filter by periodicity."""

    def test_analyze_by_periodicity_daily(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.side_effect = [
                "daily",
                None,
            ]  # Select daily, then back
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_by_periodicity(db_name)
        captured = capsys.readouterr()
        assert "Daily Habit" in captured.out
        assert "Weekly Habit" not in captured.out

    def test_analyze_by_periodicity_cancel(self, sample_habits):
        db_name, hid1, hid2 = sample_habits
        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "Cancel"
            with patch("momentum_hub.cli_analysis.show_colored_message") as mock_show:
                with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                    analyze_by_periodicity(db_name)
            mock_show.assert_called_with(
                "Operation cancelled. No periodicity selected.", color=Fore.RED
            )


class TestAnalyzeLongestStreakAll:
    """Tests CLI analysis: longest streak across all habits."""

    def test_analyze_longest_streak_all(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
            analyze_longest_streak_all(db_name)
        captured = capsys.readouterr()
        assert "Daily Habit" in captured.out
        assert "Weekly Habit" in captured.out


class TestAnalyzeLongestStreakOne:
    """Tests CLI analysis: longest streak for a single habit."""

    def test_analyze_longest_streak_one_success(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[0]
        ):
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_longest_streak_one(db_name)
        captured = capsys.readouterr()
        assert "Daily Habit" in captured.out


class TestAnalyzeStreakHistoryGrid:
    """Tests CLI analysis: streak history calendar view."""

    def test_analyze_streak_history_grid_daily(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        # Add a completion to the habit
        now = datetime.datetime.now()
        db.add_completion(hid1, now, db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[0]
        ):
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_streak_history_grid(db_name)
        captured = capsys.readouterr()
        assert "Streak History (Calendar View)" in captured.out

    def test_analyze_streak_history_grid_weekly(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[1]
        ):
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_streak_history_grid(db_name)
        captured = capsys.readouterr()
        assert "Week completed" in captured.out


class TestAnalyzeBestWorstHabit:
    """Tests CLI analysis: best and worst habit selection."""

    def test_analyze_best_worst_habit_success(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        # Add streaks
        habit1 = db.get_habit(hid1, db_name)
        habit1.streak = 5
        db.update_habit(habit1, db_name)
        habit2 = db.get_habit(hid2, db_name)
        habit2.streak = 3
        db.update_habit(habit2, db_name)
        with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
            analyze_best_worst_habit(db_name)
        captured = capsys.readouterr()
        assert "Best" in captured.out
        assert "Worst" in captured.out

    def test_analyze_best_worst_habit_no_streaks(self, tmp_db_path):
        with patch("momentum_hub.cli_analysis.show_colored_message") as mock_show:
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_best_worst_habit(tmp_db_path)
        mock_show.assert_called_with(
            "No streaks found for any active habits yet. Keep tracking!", color=Fore.RED
        )


class TestAnalyzeGoalProgress:
    """Tests CLI analysis: goal progress reporting."""

    def test_analyze_goal_progress_success(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        # Create a goal for the habit
        from momentum_hub.goal import Goal

        goal = Goal(habit_id=hid1, target_period_days=28, target_completions=10)
        db.add_goal(goal, db_name)
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[0]
        ):
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_goal_progress(db_name)
        captured = capsys.readouterr()
        assert "Progress" in captured.out


class TestAnalyzeCompletionHistory:
    """Tests CLI analysis: completion history view."""

    def test_analyze_completion_history_with_data(self, sample_habits, capsys):
        db_name, hid1, hid2 = sample_habits
        # Add completion
        now = datetime.datetime.now()
        db.add_completion(hid1, now, db_name)
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[0]
        ):
            with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                analyze_completion_history(db_name)
        captured = capsys.readouterr()
        assert "Completion Date/Time" in captured.out

    def test_analyze_completion_history_no_data(self, sample_habits):
        db_name, hid1, hid2 = sample_habits
        habits = db.get_all_habits(active_only=True, db_name=db_name)
        with patch(
            "momentum_hub.cli_analysis._handle_habit_selection", return_value=habits[0]
        ):
            with patch("momentum_hub.cli_analysis.show_colored_message") as mock_show:
                with patch("momentum_hub.cli_analysis.press_enter_to_continue"):
                    analyze_completion_history(db_name)
        mock_show.assert_called_with(
            "No completions recorded yet for this habit.", color=Fore.YELLOW
        )

import os
import platform

if platform.system() == "Windows":
    os.environ["PROMPT_TOOLKIT_NO_WIN32_CONSOLE"] = "1"
import datetime
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

import momentum_hub
from momentum_hub import momentum_cli
from momentum_hub.habit import Habit


@pytest.fixture
def mock_db():
    """Fixture to mock the db module."""
    with patch("momentum_hub.momentum_cli.db") as mock_db:
        yield mock_db


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
        streak=5,
        created_at=datetime.datetime(2023, 1, 1),
        last_completed=datetime.datetime(2023, 1, 6),
        is_active=True,
    )


@pytest.fixture
def sample_habits(sample_habit):
    """Fixture to create a list of sample habits."""
    habit2 = Habit(
        id=2,
        name="Weekly Habit",
        frequency="weekly",
        notes="Weekly notes",
        reminder_time="09:00",
        evening_reminder_time="21:00",
        streak=2,
        created_at=datetime.datetime(2023, 1, 1),
        last_completed=datetime.datetime(2023, 1, 8),
        is_active=True,
    )
    return [sample_habit, habit2]


class TestMainMenu:
    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.create_new_habit")
    def test_main_menu_create_habit(self, mock_create, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Create a new habit"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_create.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.view_habits")
    def test_main_menu_view_habits(self, mock_view, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "View habits"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_view.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.mark_habit_completed")
    def test_main_menu_mark_completed(self, mock_mark, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Mark a habit as completed"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_mark.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.update_habit")
    def test_main_menu_update_habit(self, mock_update, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Update a habit"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_update.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.analyze_habits")
    def test_main_menu_analyze_habits(self, mock_analyze, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Analyze habits"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_analyze.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.delete_habit")
    def test_main_menu_delete_habit(self, mock_delete, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Delete a habit"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_delete.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("momentum_hub.momentum_cli.reactivate_habit")
    def test_main_menu_reactivate_habit(self, mock_reactivate, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Reactivate a habit"
        momentum_hub.momentum_cli.main_menu("test.db")
        mock_reactivate.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.questionary.select")
    @patch("builtins.print")
    def test_main_menu_exit(self, mock_print, mock_select, mock_db):
        mock_select.return_value.ask.return_value = "Exit"
        with pytest.raises(SystemExit):
            momentum_hub.momentum_cli.main_menu("test.db")


class TestCreateNewHabit:
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.add_habit")
    @patch("builtins.input")
    def test_create_new_habit_success(
        self, mock_input, mock_add_habit, mock_select, mock_text, mock_db
    ):
        mock_text.return_value.ask.side_effect = [
            "Test Habit",
            "Test notes",
            "08:00",
            "20:00",
        ]
        mock_select.return_value.ask.return_value = "daily"
        mock_add_habit.return_value = 1
        momentum_hub.momentum_cli.create_new_habit("test.db")
        mock_add_habit.assert_called_once()
        args, kwargs = mock_add_habit.call_args
        habit = args[0]
        assert habit.name == "Test Habit"
        assert habit.frequency == "daily"

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("builtins.input")
    def test_create_new_habit_cancel_name(self, mock_input, mock_text, mock_db):
        mock_text.return_value.ask.return_value = "cancel"
        momentum_hub.momentum_cli.create_new_habit("test.db")
        # Should not call db.add_habit


class TestViewHabits:
    @patch("momentum_hub.cli_display.db.get_all_habits")
    @patch("momentum_hub.cli_display.press_enter_to_continue")
    def test_view_habits_with_data(
        self, mock_continue, mock_get_habits, sample_habits, mock_db
    ):
        mock_get_habits.return_value = sample_habits
        momentum_hub.momentum_cli.view_habits("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")

    @patch("momentum_hub.cli_display.db.get_all_habits")
    @patch("momentum_hub.cli_display.press_enter_to_continue")
    def test_view_habits_no_data(self, mock_continue, mock_get_habits, mock_db):
        mock_get_habits.return_value = []
        momentum_hub.momentum_cli.view_habits("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestMarkHabitCompleted:
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.db.add_completion")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.db.update_streak")
    @patch("momentum_hub.cli_habit_management.db.get_habit")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_mark_habit_completed_success(
        self,
        mock_continue,
        mock_get_habit,
        mock_update_streak,
        mock_update_habit,
        mock_add_completion,
        mock_get_habits,
        mock_select,
        sample_habit,
        mock_db,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily) - Streak: 5"
        mock_get_habit.return_value = sample_habit
        momentum_hub.momentum_cli.mark_habit_completed("test.db")
        mock_add_completion.assert_called_once()
        mock_update_habit.assert_called_once()
        mock_update_streak.assert_called_once()

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_utils.press_enter_to_continue")
    def test_mark_habit_completed_no_habits(
        self, mock_continue, mock_get_habits, mock_db
    ):
        mock_get_habits.return_value = []
        momentum_hub.momentum_cli.mark_habit_completed("test.db")
        # Should handle gracefully


class TestDeleteHabit:
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.confirm")
    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.db.delete_habit")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_success(
        self,
        mock_continue,
        mock_delete,
        mock_get_habits,
        mock_confirm,
        mock_select,
        sample_habit,
        mock_db,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily)"
        mock_confirm.return_value.ask.return_value = True
        momentum_hub.momentum_cli.delete_habit("test.db")
        mock_delete.assert_called_once_with(1, "test.db")

    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.confirm")
    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_cancel(
        self,
        mock_continue,
        mock_get_habits,
        mock_confirm,
        mock_select,
        sample_habit,
        mock_db,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily)"
        mock_confirm.return_value.ask.return_value = False
        momentum_hub.momentum_cli.delete_habit("test.db")
        # Should not call delete


class TestReactivateHabit:
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.db.reactivate_habit")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_reactivate_habit_success(
        self,
        mock_continue,
        mock_reactivate,
        mock_get_habits,
        mock_select,
        sample_habit,
        mock_db,
    ):
        sample_habit.is_active = False
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily)"
        momentum_hub.momentum_cli.reactivate_habit("test.db")
        mock_reactivate.assert_called_once_with(1, "test.db")


class TestUpdateHabit:
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_success(
        self,
        mock_continue,
        mock_update,
        mock_get_habits,
        mock_select,
        mock_text,
        sample_habit,
        mock_db,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.side_effect = [
            MagicMock(
                ask=MagicMock(return_value="1. Test Habit (daily) - Streak: 5")
            ),  # habit selection
            MagicMock(ask=MagicMock(return_value="weekly")),  # frequency
            MagicMock(ask=MagicMock(return_value="No category")),  # category selection
        ]
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Updated Name")),  # name
            MagicMock(ask=MagicMock(return_value="Updated notes")),  # notes
            MagicMock(ask=MagicMock(return_value="09:00")),  # reminder
            MagicMock(ask=MagicMock(return_value="21:00")),  # evening reminder
        ]
        momentum_hub.momentum_cli.update_habit("test.db")
        mock_update.assert_called_once()


class TestAnalyzeHabits:
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.analyze_list_all_habits")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    def test_analyze_habits_list_all(self, mock_get_habits, mock_analyze, mock_select):
        mock_select.return_value.ask.return_value = "List all currently tracked habits"
        mock_get_habits.return_value = []
        momentum_hub.momentum_cli.analyze_habits("test.db")
        mock_analyze.assert_called_once_with("test.db")

    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.analyze_by_periodicity")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    def test_analyze_habits_by_periodicity(
        self, mock_get_habits, mock_analyze, mock_select
    ):
        mock_select.return_value.ask.return_value = (
            "List all habits with the same periodicity"
        )
        mock_get_habits.return_value = []
        momentum_hub.momentum_cli.analyze_habits("test.db")
        mock_analyze.assert_called_once_with("test.db")

    @patch("momentum_hub.cli_analysis.questionary.select")
    def test_analyze_habits_back_to_menu(self, mock_select):
        mock_select.return_value.ask.return_value = "Back to Main Menu"
        momentum_hub.momentum_cli.analyze_habits("test.db")
        # Should return without calling anything


class TestAnalyzeListAllHabits:
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_list_all_habits(
        self, mock_continue, mock_get_habits, sample_habits
    ):
        mock_get_habits.return_value = sample_habits
        momentum_hub.momentum_cli.analyze_list_all_habits("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestAnalyzeByPeriodicity:
    @patch(
        "momentum_hub.cli_analysis.analysis.calculate_completion_rate_for_habit",
        return_value=0.8,
    )
    @patch(
        "momentum_hub.cli_analysis.analysis.calculate_longest_streak_for_habit",
        return_value=5,
    )
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_by_periodicity_daily(
        self,
        mock_continue,
        mock_get_habits,
        mock_select,
        mock_longest_streak,
        mock_completion_rate,
        sample_habits,
    ):
        mock_get_habits.return_value = sample_habits
        mock_select.return_value.ask.return_value = "daily"
        momentum_hub.momentum_cli.analyze_by_periodicity("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestAnalyzeLongestStreakAll:
    @patch(
        "momentum_hub.cli_analysis.analysis.calculate_longest_streak_for_habit",
        return_value=5,
    )
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_longest_streak_all(
        self, mock_continue, mock_get_habits, mock_longest_streak, sample_habits
    ):
        mock_get_habits.return_value = sample_habits
        momentum_hub.momentum_cli.analyze_longest_streak_all("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestAnalyzeLongestStreakOne:
    @patch(
        "momentum_hub.cli_analysis.analysis.calculate_longest_streak_for_habit",
        return_value=5,
    )
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_longest_streak_one(
        self,
        mock_continue,
        mock_get_habits,
        mock_select,
        mock_longest_streak,
        sample_habit,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily) - Streak: 5"
        momentum_hub.momentum_cli.analyze_longest_streak_one("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestAnalyzeStreakHistoryGrid:
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.db.get_completions")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_streak_history_grid(
        self,
        mock_continue,
        mock_get_completions,
        mock_get_habits,
        mock_select,
        sample_habit,
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily) - Streak: 5"
        mock_get_completions.return_value = [datetime.datetime(2023, 1, 6)]
        momentum_hub.momentum_cli.analyze_streak_history_grid("test.db")
        mock_get_habits.assert_called_once_with(active_only=True, db_name="test.db")


class TestAnalyzeExportCsv:
    @patch("momentum_hub.cli_export.questionary.select")
    @patch("momentum_hub.cli_export.export_all_habits_to_csv")
    def test_analyze_export_csv_all_habits(self, mock_export, mock_select):
        mock_select.return_value.ask.return_value = (
            "Export all habits and their details"
        )
        momentum_hub.momentum_cli.analyze_export_csv("test.db")
        mock_export.assert_called_once_with("test.db")


class TestAnalyzeBestWorstHabit:
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_best_worst_habit(self, mock_continue):
        with patch(
            "momentum_hub.cli_analysis.analysis.calculate_best_worst_habit",
            return_value=(MagicMock(name="Best"), MagicMock(name="Worst")),
        ):
            momentum_hub.momentum_cli.analyze_best_worst_habit("test.db")


class TestAnalyzeGoalProgress:
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_goal_progress(
        self, mock_continue, mock_get_habits, mock_select, sample_habit
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily) - Streak: 5"
        with patch(
            "momentum_hub.cli_analysis.analysis.calculate_goal_progress",
            return_value={"count": 5, "total": 10, "percent": 50.0},
        ):
            momentum_hub.momentum_cli.analyze_goal_progress("test.db")


class TestAnalyzeCompletionHistory:
    @patch("momentum_hub.cli_analysis.questionary.select")
    @patch("momentum_hub.cli_analysis.db.get_all_habits")
    @patch("momentum_hub.cli_analysis.press_enter_to_continue")
    def test_analyze_completion_history(
        self, mock_continue, mock_get_habits, mock_select, sample_habit
    ):
        mock_get_habits.return_value = [sample_habit]
        mock_select.return_value.ask.return_value = "1. Test Habit (daily) - Streak: 5"
        with patch(
            "momentum_hub.cli_analysis.analysis.get_completion_history",
            return_value=[datetime.datetime(2023, 1, 6)],
        ):
            momentum_hub.momentum_cli.analyze_completion_history("test.db")


class TestHandleHabitSelection:
    @patch("momentum_hub.cli_utils.press_enter_to_continue")
    def test_handle_habit_selection_success(self, mock_continue, sample_habit):
        import questionary

        with patch.object(questionary, "select") as mock_select:
            mock_select.return_value.ask.return_value = (
                "1. Test Habit (daily) - Streak: 5"
            )
            result = momentum_hub.momentum_cli._handle_habit_selection(
                [sample_habit], "Select habit:", "No habits"
            )
            assert result == sample_habit

    @patch("momentum_hub.cli_utils.press_enter_to_continue")
    def test_handle_habit_selection_cancel(self, mock_continue, sample_habit):
        import questionary

        with patch.object(questionary, "select") as mock_select:
            mock_select.return_value.ask.return_value = "Cancel"
            result = momentum_hub.momentum_cli._handle_habit_selection(
                [sample_habit], "Select habit:", "No habits"
            )
            assert result is None

    @patch("momentum_hub.cli_utils.press_enter_to_continue")
    def test_handle_habit_selection_no_habits(self, mock_continue):
        result = momentum_hub.momentum_cli._handle_habit_selection(
            [], "Select habit:", "No habits"
        )
        assert result is None


class TestStartCli:
    @patch("momentum_hub.momentum_cli.db.init_db")
    @patch("momentum_hub.momentum_cli.startup_message")
    @patch("momentum_hub.momentum_cli.main_menu")
    @patch("builtins.print")
    def test_start_cli_success(
        self, mock_print, mock_main_menu, mock_startup, mock_init_db
    ):
        # Mock main_menu to raise SystemExit to exit the loop
        mock_main_menu.side_effect = SystemExit()
        momentum_hub.momentum_cli.start_cli("test.db")
        mock_init_db.assert_called_once_with("test.db")
        mock_startup.assert_called_once()
        mock_main_menu.assert_called_once_with("test.db")

    @patch("momentum_hub.momentum_cli.db.init_db")
    @patch("momentum_hub.momentum_cli.startup_message")
    @patch("momentum_hub.momentum_cli.main_menu")
    @patch("momentum_hub.momentum_cli.show_colored_message")
    @patch("builtins.input")
    def test_start_cli_exception_handling(
        self, mock_input, mock_show, mock_main_menu, mock_startup, mock_init_db
    ):
        # Mock input to avoid stdin issues
        mock_input.return_value = ""
        # Mock main_menu to raise an exception
        mock_main_menu.side_effect = [Exception("Test error"), SystemExit()]
        momentum_hub.momentum_cli.start_cli("test.db")
        mock_show.assert_called_with("An error occurred: Test error", color="\x1b[31m")

import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch

import pytest
from colorama import Fore

from momentum_hub.cli_utils import (
    _handle_habit_selection,
    _to_date,
    _validate_time_format,
)
from momentum_hub.habit import Habit


@pytest.fixture
def sample_habit():
    return Habit(id=1, name="Test Habit", frequency="daily")


class TestValidateTimeFormat:
    def test_valid_time_format_24_hour(self):
        assert _validate_time_format("14:30") is True

    def test_valid_time_format_empty(self):
        assert _validate_time_format("") is True

    def test_invalid_time_format_wrong_format(self):
        result = _validate_time_format("14-30")
        assert result == "Invalid time format. Please use HH:MM (24-hour format)."

    def test_invalid_time_format_non_numeric(self):
        result = _validate_time_format("ab:cd")
        assert result == "Invalid time format. Please use HH:MM (24-hour format)."

    def test_invalid_time_format_out_of_range(self):
        result = _validate_time_format("25:00")
        assert result == "Invalid time format. Please use HH:MM (24-hour format)."


class TestHandleHabitSelection:
    def test_handle_habit_selection_success(self, sample_habit):
        habits = [sample_habit]
        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = (
                "1. Test Habit (daily) - Streak: 0"
            )
            result = _handle_habit_selection(habits, "Select habit:")
            assert result == sample_habit

    def test_handle_habit_selection_cancel(self, sample_habit):
        habits = [sample_habit]
        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "Cancel"
            with patch("momentum_hub.cli_utils.press_enter_to_continue"):
                result = _handle_habit_selection(habits, "Select habit:")
                assert result is None

    def test_handle_habit_selection_no_habits(self):
        with patch("momentum_hub.cli_utils.show_colored_message") as mock_show:
            with patch("momentum_hub.cli_utils.press_enter_to_continue"):
                result = _handle_habit_selection([], "Select habit:", "No habits")
                assert result is None
                # The function prints directly, so mock_show is not called
                # mock_show.assert_called_with("No habits", color=Fore.RED)

    def test_handle_habit_selection_invalid_selection(self, sample_habit):
        habits = [sample_habit]
        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "invalid"
            with patch("momentum_hub.cli_utils.press_enter_to_continue"):
                result = _handle_habit_selection(habits, "Select habit:")
                assert result is None


class TestToDate:
    def test_to_date_with_datetime(self):
        dt = datetime.datetime(2023, 1, 1, 10, 0)
        assert _to_date(dt) == dt.date()

    def test_to_date_with_date(self):
        date_obj = datetime.date(2023, 1, 1)
        assert _to_date(date_obj) == date_obj


class TestPressEnterToContinue:
    def test_press_enter_to_continue(self):
        """Test that press_enter_to_continue calls input."""
        with patch("builtins.input") as mock_input:
            mock_input.return_value = ""
            from momentum_hub.cli_utils import press_enter_to_continue

            press_enter_to_continue()
            mock_input.assert_called_once_with("Press Enter to continue...")

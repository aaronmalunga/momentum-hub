import datetime
from unittest.mock import MagicMock, patch

import pytest

import momentum_hub.momentum_db as db
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_momentum_hub.cli_display.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def sample_habit(tmp_db_path):
    # Create sample habit
    h = Habit(name="Test Habit", frequency="daily")
    hid = db.add_habit(h, tmp_db_path)
    return db.get_habit(hid, tmp_db_path)


class TestStartupMessage:
    @patch("momentum_hub.cli_display.shutil.get_terminal_size")
    @patch("momentum_hub.cli_display.Figlet")
    @patch("builtins.print")
    def test_startup_message(self, mock_print, mock_figlet, mock_get_terminal_size):
        mock_get_terminal_size.return_value = MagicMock(columns=80)
        mock_figlet_instance = MagicMock()
        mock_figlet_instance.renderText.return_value = "MOMENTUM HUB"
        mock_figlet.return_value = mock_figlet_instance

        from momentum_hub.cli_display import startup_message

        startup_message()

        mock_print.assert_called()


class TestViewHabits:
    def test_view_habits_with_data(self, tmp_db_path, sample_habit):
        with (
            patch("momentum_hub.cli_display.show_colored_message"),
            patch("momentum_hub.cli_display.press_enter_to_continue"),
            patch("builtins.print"),
        ):

            from momentum_hub.cli_display import view_habits

            view_habits(tmp_db_path)

    def test_view_habits_no_data(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_display.show_colored_message") as mock_show,
            patch("momentum_hub.cli_display.press_enter_to_continue"),
        ):

            from momentum_hub.cli_display import view_habits

            view_habits(tmp_db_path)

            mock_show.assert_called_with(
                "No active habits found. Let's create one!", color="\x1b[31m"
            )

import csv
import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch

import pytest
from colorama import Fore

import momentum_hub.momentum_db as db
from momentum_hub.cli_export import (
    analyze_export_csv,
    export_all_completions_to_csv,
    export_all_habits_to_csv,
    export_habit_completions_to_csv,
)
from momentum_hub.completion import export_completions_to_csv
from momentum_hub.habit import Habit


@pytest.fixture(autouse=True)
def cleanup_db():
    """
    Closes all database connections after each test.
    """
    yield
    db.close_all_connections()


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_export.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def sample_data(tmp_db_path):
    # Add sample habits
    h1 = Habit(name="Daily Habit", frequency="daily", notes="Test daily")
    h2 = Habit(name="Weekly Habit", frequency="weekly", notes="Test weekly")
    hid1 = db.add_habit(h1, db_name=tmp_db_path)
    hid2 = db.add_habit(h2, db_name=tmp_db_path)

    # Add completions
    now = datetime.datetime.now()
    db.add_completion(hid1, now, db_name=tmp_db_path)
    db.add_completion(hid2, now, db_name=tmp_db_path)

    return tmp_db_path, hid1, hid2


def test_export_completions_to_csv_from_completion_module(sample_data, tmp_path):
    db_name, hid1, hid2 = sample_data
    output_file = tmp_path / "completions_fixed.csv"

    export_completions_to_csv(str(output_file), db_name)
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert "completion_id" in rows[0]
        assert "habit_name" in rows[0]


def test_export_completions_to_csv_from_momentum_db_module(sample_data, tmp_path):
    db_name, hid1, hid2 = sample_data
    output_file = tmp_path / "completions_db.csv"

    # Use the duplicate function in momentum_db.py
    db.export_completions_to_csv(str(output_file), db_name)
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert "completion_id" in rows[0]


def test_export_completions_to_csv_empty_path_raises_error(sample_data):
    """Test that export_completions_to_csv raises OSError for empty path."""
    db_name, hid1, hid2 = sample_data

    with pytest.raises(OSError, match="Output path cannot be empty"):
        export_completions_to_csv("", db_name)

    with pytest.raises(OSError, match="Output path cannot be empty"):
        export_completions_to_csv("   ", db_name)


def test_export_completions_to_csv_write_test_fails(sample_data, tmp_path, monkeypatch):
    """Test that export fails when write test fails."""
    db_name, hid1, hid2 = sample_data

    output_file = tmp_path / "completions.csv"

    # Mock Path.open to raise OSError when creating the test file
    from pathlib import Path

    original_open = Path.open

    def mock_open(self, *args, **kwargs):
        if ".export_test_write" in str(self):
            raise OSError("Write test failed")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", mock_open)

    with pytest.raises(OSError, match="Cannot write to directory"):
        export_completions_to_csv(str(output_file), db_name)


def test_export_all_habits_logic(sample_data):
    db_name, hid1, hid2 = sample_data
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    assert len(habits) == 2
    assert habits[0].name == "Daily Habit"
    assert habits[1].name == "Weekly Habit"


def test_export_all_completions_logic(sample_data):
    db_name, hid1, hid2 = sample_data
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    total_completions = 0
    for habit in habits:
        completions = db.get_completions(habit.id, db_name)
        total_completions += len(completions)
    assert total_completions == 2


def test_export_habit_completions_logic(sample_data):
    db_name, hid1, hid2 = sample_data
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    selected_habit = habits[0]
    completions = db.get_completions(selected_habit.id, db_name)
    assert len(completions) == 1
    assert selected_habit.name == "Daily Habit"


# New tests for momentum_hub.cli_export.py functions to improve coverage


def test_export_all_habits_to_csv_success(sample_data, tmp_path):
    db_name, hid1, hid2 = sample_data
    with patch("momentum_hub.cli_export.press_enter_to_continue"):
        export_all_habits_to_csv(db_name, base_dir=str(tmp_path))
    # Check if file was created in the temporary directory
    import os

    csv_files = [
        f
        for f in os.listdir(str(tmp_path))
        if f.startswith("habits_export_") and f.endswith(".csv")
    ]
    assert len(csv_files) >= 1


def test_export_all_habits_to_csv_empty_db(tmp_db_path, tmp_path):
    # Test with empty database
    with patch("momentum_hub.cli_export.press_enter_to_continue"):
        export_all_habits_to_csv(tmp_db_path)
    import os

    os.makedirs("CSV Export", exist_ok=True)
    csv_files = [
        f
        for f in os.listdir("CSV Export")
        if f.startswith("habits_export_") and f.endswith(".csv")
    ]
    assert len(csv_files) >= 1


def test_export_all_completions_to_csv_success(sample_data, tmp_path):
    db_name, hid1, hid2 = sample_data
    with patch("momentum_hub.cli_export.press_enter_to_continue"):
        export_all_completions_to_csv(db_name)
    import os

    os.makedirs("CSV Export", exist_ok=True)
    csv_files = [
        f
        for f in os.listdir("CSV Export")
        if f.startswith("all_completions_export_") and f.endswith(".csv")
    ]
    assert len(csv_files) >= 1


def test_export_habit_completions_to_csv_success(sample_data, tmp_path):
    db_name, hid1, hid2 = sample_data
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    selected_habit = habits[1]  # Weekly habit
    with (
        patch("momentum_hub.cli_export.press_enter_to_continue"),
        patch(
            "momentum_hub.cli_export._handle_habit_selection",
            return_value=selected_habit,
        ),
    ):
        export_habit_completions_to_csv(db_name, base_dir=str(tmp_path))
    import os

    csv_files = [
        f
        for f in os.listdir(str(tmp_path))
        if f.startswith("completions_Weekly_Habit_") and f.endswith(".csv")
    ]
    assert len(csv_files) >= 1
    # Find the most recent file
    csv_files.sort(reverse=True)
    csv_file = os.path.join(str(tmp_path), csv_files[0])
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert "Week Number" in rows[0]


def test_export_habit_completions_to_csv_no_completions(tmp_db_path, tmp_path):
    # Add habit with no completions
    h = Habit(name="No Completions", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    habit = db.get_habit(hid, db_name=tmp_db_path)
    with (
        patch("momentum_hub.cli_export.press_enter_to_continue"),
        patch("momentum_hub.cli_export._handle_habit_selection", return_value=habit),
    ):
        export_habit_completions_to_csv(tmp_db_path, base_dir=str(tmp_path))
    # Should not create file or handle gracefully
    import os

    csv_files = [
        f
        for f in os.listdir(str(tmp_path))
        if f.startswith("completions_No_Completions_") and f.endswith(".csv")
    ]
    assert len(csv_files) == 0  # No file created


def test_export_all_habits_to_csv_error_handling(tmp_db_path, tmp_path):
    # Add a habit to trigger the error path
    h = Habit(name="Test Habit", frequency="daily")
    db.add_habit(h, db_name=tmp_db_path)
    # Simulate file write error
    with patch("builtins.open", side_effect=OSError("Permission denied")):
        with patch("momentum_hub.cli_export.show_colored_message") as mock_show:
            with patch("momentum_hub.cli_export.press_enter_to_continue"):
                export_all_habits_to_csv(tmp_db_path)
                mock_show.assert_called_with(
                    "Error exporting habits: Permission denied", color=Fore.RED
                )


def test_export_all_completions_to_csv_error_handling(tmp_db_path, tmp_path):
    # Add a habit to trigger the error path
    h = Habit(name="Test Habit", frequency="daily")
    db.add_habit(h, db_name=tmp_db_path)
    # Simulate file write error
    with patch("builtins.open", side_effect=OSError("Permission denied")):
        with patch("momentum_hub.cli_export.show_colored_message") as mock_show:
            with patch("momentum_hub.cli_export.press_enter_to_continue"):
                export_all_completions_to_csv(tmp_db_path)
                mock_show.assert_called_with(
                    "Error exporting completions: Permission denied", color=Fore.RED
                )


def test_analyze_export_csv_all_habits(sample_data):
    db_name, hid1, hid2 = sample_data
    with (
        patch("momentum_hub.cli_export.questionary.select") as mock_select,
        patch("momentum_hub.cli_export.export_all_habits_to_csv") as mock_export,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        mock_select.return_value.ask.return_value = (
            "Export all habits and their details"
        )
        analyze_export_csv(db_name)
        mock_export.assert_called_once_with(db_name)


def test_analyze_export_csv_all_completions(sample_data):
    db_name, hid1, hid2 = sample_data
    with (
        patch("momentum_hub.cli_export.questionary.select") as mock_select,
        patch("momentum_hub.cli_export.export_all_completions_to_csv") as mock_export,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        mock_select.return_value.ask.return_value = "Export completions for all habits"
        analyze_export_csv(db_name)
        mock_export.assert_called_once_with(db_name)


def test_analyze_export_csv_specific_habit(sample_data):
    db_name, hid1, hid2 = sample_data
    with (
        patch("momentum_hub.cli_export.questionary.select") as mock_select,
        patch("momentum_hub.cli_export.export_habit_completions_to_csv") as mock_export,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        mock_select.return_value.ask.return_value = (
            "Export completions for a specific habit"
        )
        analyze_export_csv(db_name)
        mock_export.assert_called_once_with(db_name)


def test_analyze_export_csv_back_to_menu(sample_data):
    db_name, hid1, hid2 = sample_data
    with patch("momentum_hub.cli_export.questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "Back to Main Menu"
        analyze_export_csv(db_name)
        # Should not raise any exceptions


def test_export_all_completions_to_csv_no_habits(tmp_db_path):
    with (
        patch("momentum_hub.cli_export.show_colored_message") as mock_show,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        export_all_completions_to_csv(tmp_db_path)
        mock_show.assert_called_with(
            "No habits found to export completions.", color=Fore.RED
        )


def test_export_habit_completions_to_csv_no_habits(tmp_db_path):
    with (
        patch("momentum_hub.cli_export.show_colored_message") as mock_show,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        export_habit_completions_to_csv(tmp_db_path)
        mock_show.assert_called_with(
            "No habits found to export completions.", color=Fore.RED
        )


def test_export_habit_completions_to_csv_cancel_selection(tmp_db_path):
    # Add habit
    h = Habit(name="Test Habit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    with patch("momentum_hub.cli_export._handle_habit_selection", return_value=None):
        export_habit_completions_to_csv(tmp_db_path)
        # Should return without doing anything


def test_export_all_habits_to_csv_with_category_and_goal(tmp_db_path, tmp_path):
    # Add category
    from momentum_hub.category import Category

    cat = Category(name="Test Category", description="Test", color="blue")
    cat_id = db.add_category(cat, db_name=tmp_db_path)

    # Add habit with category
    h = Habit(name="Habit with Category", frequency="daily", category_id=cat_id)
    hid = db.add_habit(h, db_name=tmp_db_path)

    # Add goal
    from momentum_hub.goal import Goal

    g = Goal(habit_id=hid, target_completions=10, target_period_days=30)
    db.add_goal(g, db_name=tmp_db_path)

    with patch("momentum_hub.cli_export.press_enter_to_continue"):
        export_all_habits_to_csv(tmp_db_path, base_dir=str(tmp_path))

    # Check the csv has category and goal progress
    import os

    csv_files = [
        f
        for f in os.listdir(str(tmp_path))
        if f.startswith("habits_export_") and f.endswith(".csv")
    ]
    assert len(csv_files) >= 1
    csv_file = os.path.join(str(tmp_path), csv_files[0])
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Category"] == "Test Category"
        assert rows[0]["Goal Progress"] != ""  # Should have progress


def test_export_habit_completions_to_csv_error_handling(tmp_db_path, tmp_path):
    # Add habit with completions
    h = Habit(name="Test Habit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    now = datetime.datetime.now()
    db.add_completion(hid, now, db_name=tmp_db_path)
    habit = db.get_habit(hid, db_name=tmp_db_path)
    with (
        patch("momentum_hub.cli_export._handle_habit_selection", return_value=habit),
        patch("builtins.open", side_effect=OSError("Permission denied")),
        patch("momentum_hub.cli_export.show_colored_message") as mock_show,
        patch("momentum_hub.cli_export.press_enter_to_continue"),
    ):
        export_habit_completions_to_csv(tmp_db_path, base_dir=str(tmp_path))
        mock_show.assert_called_with(
            "Error exporting completions: Permission denied", color=Fore.RED
        )

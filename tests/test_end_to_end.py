import csv
import datetime
import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_hub.momentum_db as db
from momentum_hub import habit_analysis as analysis
from momentum_hub.completion import export_completions_to_csv
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_e2e_db_path(tmp_path):
    db_file = tmp_path / "test_e2e.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


def test_full_workflow_create_complete_analyze_export(tmp_e2e_db_path, tmp_path):
    """End-to-end test: create habit -> complete -> analyze -> export."""
    db_name = tmp_e2e_db_path

    # Step 1: Create a new habit
    habit = Habit(name="E2E Test Habit", frequency="daily", notes="Integration test")
    habit_id = db.add_habit(habit, db_name=db_name)
    assert habit_id is not None

    # Verify habit was created
    fetched_habit = db.get_habit(habit_id, db_name=db_name)
    assert fetched_habit.name == "E2E Test Habit"
    assert fetched_habit.frequency == "daily"

    # Step 2: Mark habit as completed multiple times
    now = datetime.datetime.now()
    db.add_completion(habit_id, now, db_name=db_name)
    db.update_streak(habit_id, db_name=db_name)
    yesterday = now - datetime.timedelta(days=1)
    db.add_completion(habit_id, yesterday, db_name=db_name)
    db.update_streak(habit_id, db_name=db_name)

    # Verify completions
    completions = db.get_completions(habit_id, db_name=db_name)
    assert len(completions) == 2

    # Update habit streak
    updated_habit = db.get_habit(habit_id, db_name=db_name)
    assert updated_habit.streak == 2

    # Step 3: Analyze the habit
    longest_streak = analysis.calculate_longest_streak_for_habit(habit_id, db_name)
    assert longest_streak == 2

    completion_rate = analysis.calculate_completion_rate_for_habit(habit_id, db_name)
    # For daily habits, completion rate is based on last 28 days
    # With 2 completions in the last 28 days, rate should be 2/28 ≈ 0.0714
    assert completion_rate == 2 / 28

    # Step 4: Export completions to CSV
    output_file = tmp_path / "e2e_completions.csv"
    export_completions_to_csv(str(output_file), db_name)

    # Verify export
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["habit_name"] == "E2E Test Habit"


def test_weekly_habit_workflow(tmp_e2e_db_path, tmp_path):
    """End-to-end test for weekly habit: create -> complete -> analyze -> export."""
    db_name = tmp_e2e_db_path

    # Create weekly habit
    habit = Habit(
        name="Weekly E2E Habit", frequency="weekly", notes="Weekly integration test"
    )
    habit_id = db.add_habit(habit, db_name=db_name)

    # Mark completed for two weeks
    now = datetime.datetime.now()
    db.add_completion(habit_id, now, db_name=db_name)
    last_week = now - datetime.timedelta(weeks=1)
    db.add_completion(habit_id, last_week, db_name=db_name)
    db.update_streak(habit_id, db_name=db_name)

    # Analyze
    longest_streak = analysis.calculate_longest_streak_for_habit(habit_id, db_name)
    assert longest_streak == 2

    # Export
    output_file = tmp_path / "weekly_e2e_completions.csv"
    export_completions_to_csv(str(output_file), db_name)
    assert output_file.exists()

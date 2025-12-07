import csv
import datetime
import os
import sqlite3
import tempfile
import threading

import pytest

import momentum_db as db
from category import Category
from goal import Goal
from habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_momentum_extended.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


def test_schema_migrations(tmp_db_path):
    with db.get_connection(tmp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(habits);")
        columns = [row[1] for row in cursor.fetchall()]
        assert "reactivated_at" in columns
        assert "category_id" in columns


def test_category_crud(tmp_db_path):
    c = Category(name="TestCat", description="Desc", color="blue")
    cid = db.add_category(c, db_name=tmp_db_path)
    assert isinstance(cid, int)

    fetched = db.get_category(cid, db_name=tmp_db_path)
    assert fetched is not None
    assert fetched.name == "TestCat"
    assert fetched.description == "Desc"
    assert fetched.color == "blue"
    assert fetched.is_active is True

    fetched.color = "red"
    db.update_category(fetched, db_name=tmp_db_path)
    updated = db.get_category(cid, db_name=tmp_db_path)
    assert updated.color == "red"

    db.delete_category(cid, db_name=tmp_db_path)
    deleted = db.get_category(cid, db_name=tmp_db_path)
    assert deleted.is_active is False


def test_goal_crud(tmp_db_path):
    # Need valid habit for FK
    h = Habit(name="GoalHabit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)

    g = Goal(
        habit_id=hid,
        target_period_days=14,
        target_completions=10,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=30),
    )
    gid = db.add_goal(g, db_name=tmp_db_path)
    assert isinstance(gid, int)

    fetched = db.get_goal(gid, db_name=tmp_db_path)
    assert fetched is not None
    assert fetched.habit_id == hid
    assert fetched.target_period_days == 14
    assert fetched.target_completions == 10

    fetched.target_completions = 12
    db.update_goal(fetched, db_name=tmp_db_path)
    updated = db.get_goal(gid, db_name=tmp_db_path)
    assert updated.target_completions == 12

    db.delete_goal(gid, db_name=tmp_db_path)
    deleted = db.get_goal(gid, db_name=tmp_db_path)
    assert deleted.is_active is False


def test_add_completion_edge_cases(tmp_db_path):
    h = Habit(name="EdgeCaseHabit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)

    now = datetime.datetime.now().replace(microsecond=0)

    # Add valid completion
    db.add_completion(hid, now, db_name=tmp_db_path)

    # Add completion for same day raises error
    with pytest.raises(ValueError):
        db.add_completion(hid, now, db_name=tmp_db_path)

    # Add completion in next day allowed
    next_day = now + datetime.timedelta(days=1)
    db.add_completion(hid, next_day, db_name=tmp_db_path)


def test_concurrent_completions(tmp_db_path):
    h = Habit(name="ConcurrentHabit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    base_time = datetime.datetime.now().replace(microsecond=0)

    # Define a function to add completion
    def add_comp():
        try:
            db.add_completion(hid, base_time, db_name=tmp_db_path)
        except ValueError:
            pass  # Expected duplicate

    threads = []
    for _ in range(5):
        t = threading.Thread(target=add_comp)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    comps = db.get_completions(hid, db_name=tmp_db_path)
    assert len(comps) == 1


def test_update_streak_weekly_and_daily(tmp_db_path):
    # Daily habit streak
    h1 = Habit(name="DailyStreak", frequency="daily")
    hid1 = db.add_habit(h1, db_name=tmp_db_path)

    base_date = datetime.datetime.now().date() - datetime.timedelta(days=3)
    for i in range(3):
        db.add_completion(
            hid1,
            datetime.datetime.combine(
                base_date + datetime.timedelta(days=i), datetime.time(9, 0)
            ),
            db_name=tmp_db_path,
        )
    db.update_streak(hid1, db_name=tmp_db_path)
    updated_h1 = db.get_habit(hid1, db_name=tmp_db_path)
    assert updated_h1.streak == 3

    # Weekly habit streak
    h2 = Habit(name="WeeklyStreak", frequency="weekly")
    hid2 = db.add_habit(h2, db_name=tmp_db_path)

    # Add completions spaced one week apart
    base_sunday = datetime.date.today()
    while base_sunday.weekday() != 6:
        base_sunday -= datetime.timedelta(days=1)

    for i in range(3):
        comp_date = datetime.datetime.combine(
            base_sunday + datetime.timedelta(weeks=i), datetime.time(10, 0)
        )
        db.add_completion(hid2, comp_date, db_name=tmp_db_path)

    db.update_streak(hid2, db_name=tmp_db_path)
    updated_h2 = db.get_habit(hid2, db_name=tmp_db_path)
    assert updated_h2.streak == 3


def test_export_completions_to_csv(tmp_db_path):
    h = Habit(name="ExportHabit", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    now = datetime.datetime.now().replace(microsecond=0)
    db.add_completion(hid, now, db_name=tmp_db_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "completions.csv")
        db.export_completions_to_csv(output_path=csv_path, db_name=tmp_db_path)
        assert os.path.exists(csv_path)

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert any(row["habit_id"] == str(hid) for row in rows)


def test_multiple_connections(tmp_db_path):
    # Test opening multiple connections without error and cleanup
    conns = []
    try:
        for _ in range(5):
            conns.append(db.get_connection(tmp_db_path))
        for c in conns:
            c.execute("SELECT 1")
    finally:
        for c in conns:
            c.close()


def test_error_handling_get_habit(tmp_db_path):
    # Request non-existing habit should return None
    non_existent = db.get_habit(999999, db_name=tmp_db_path)
    assert non_existent is None

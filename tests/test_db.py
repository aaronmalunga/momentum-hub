# tests/test_db.py
import datetime
import os
import sqlite3
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_hub.momentum_db as db
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_momentum.db"
    db_name = str(db_file)
    # initialize schema
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def test_db_path():
    """Fixture for using the persistent test database."""
    return "tests/test_dbs/test_momentum.db"


def test_sanity_probe():
    assert True


def test_add_and_get_habit(tmp_db_path):
    # create habit using Habit class and add via db.add_habit
    h = Habit(name="Habit A", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    assert isinstance(hid, int)

    fetched = db.get_habit(hid, db_name=tmp_db_path)
    assert fetched is not None
    assert fetched.id == hid
    assert fetched.name == "Habit A"
    assert fetched.frequency == "daily"


def test_add_and_get_completions_and_duplicates(tmp_db_path):
    # add habit
    h = Habit(name="DupTest", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)

    now = datetime.datetime.now().replace(microsecond=0)
    # add first completion
    db.add_completion(hid, now, db_name=tmp_db_path)
    comps = db.get_completions(hid, db_name=tmp_db_path)
    assert len(comps) == 1

    # adding same-day completion should raise ValueError
    with pytest.raises(ValueError):
        db.add_completion(hid, now, db_name=tmp_db_path)


def test_weekly_completion_duplicate_rule(tmp_db_path):
    # add weekly habit
    h = Habit(name="WeeklyTest", frequency="weekly")
    hid = db.add_habit(h, db_name=tmp_db_path)

    # choose a Sunday date (week start)
    sunday = datetime.date.today()
    # adjust backwards to Sunday
    while sunday.weekday() != 6:
        sunday -= datetime.timedelta(days=1)
    sunday_dt = datetime.datetime.combine(sunday, datetime.time(10, 0))

    # add a completion on that week's Sunday
    db.add_completion(hid, sunday_dt, db_name=tmp_db_path)

    # another completion later in same week (e.g. Monday) should raise
    monday_dt = sunday_dt + datetime.timedelta(days=1)
    with pytest.raises(ValueError):
        db.add_completion(hid, monday_dt, db_name=tmp_db_path)

    # a completion 7 days later (next Sunday) should be allowed
    next_week_dt = sunday_dt + datetime.timedelta(days=7)
    db.add_completion(hid, next_week_dt, db_name=tmp_db_path)
    comps = db.get_completions(hid, db_name=tmp_db_path)
    assert len(comps) == 2


def test_update_streak_daily(tmp_db_path):
    h = Habit(name="StreakDaily", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)

    base = datetime.datetime.now().date() - datetime.timedelta(days=3)
    # add 3 consecutive days
    db.add_completion(
        hid, datetime.datetime.combine(base, datetime.time(9, 0)), db_name=tmp_db_path
    )
    db.add_completion(
        hid,
        datetime.datetime.combine(
            base + datetime.timedelta(days=1), datetime.time(9, 0)
        ),
        db_name=tmp_db_path,
    )
    db.add_completion(
        hid,
        datetime.datetime.combine(
            base + datetime.timedelta(days=2), datetime.time(9, 0)
        ),
        db_name=tmp_db_path,
    )

    db.update_streak(hid, db_name=tmp_db_path)
    h2 = db.get_habit(hid, db_name=tmp_db_path)
    assert h2.streak == 3


def test_soft_delete_and_reactivate(tmp_db_path):
    h = Habit(name="SoftDelete", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)

    db.delete_habit(hid, db_name=tmp_db_path)
    h_del = db.get_habit(hid, db_name=tmp_db_path)
    assert h_del.is_active is False

    db.reactivate_habit(hid, db_name=tmp_db_path)
    h_re = db.get_habit(hid, db_name=tmp_db_path)
    assert h_re.is_active is True
    # Reactivated streak is expected to be reset by DB logic
    assert h_re.streak == 0
    assert h_re.reactivated_at is not None

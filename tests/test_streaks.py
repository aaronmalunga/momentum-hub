import datetime

import pytest

from momentum_hub import habit_analysis
from momentum_hub import momentum_db as db
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_streaks.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


def test_current_streak_daily(tmp_db_path):
    h = Habit(name="Daily Streak", frequency="daily")
    hid = db.add_habit(h, db_name=tmp_db_path)
    base = datetime.date(2026, 1, 1)
    for i in range(3):
        db.add_completion(
            hid,
            datetime.datetime.combine(
                base + datetime.timedelta(days=i), datetime.time(9, 0)
            ),
            db_name=tmp_db_path,
        )
    db.update_streak(hid, db_name=tmp_db_path)
    updated = db.get_habit(hid, db_name=tmp_db_path)
    assert updated.streak == 3


def test_longest_streak_daily():
    dates = [
        datetime.date(2026, 1, 1),
        datetime.date(2026, 1, 2),
        datetime.date(2026, 1, 3),
        datetime.date(2026, 1, 5),
    ]
    assert habit_analysis.calculate_longest_streak_from_dates(dates, "daily") == 3


def test_current_streak_weekly(tmp_db_path):
    h = Habit(name="Weekly Streak", frequency="weekly")
    hid = db.add_habit(h, db_name=tmp_db_path)
    base_sunday = datetime.date(2026, 1, 4)
    for i in range(3):
        db.add_completion(
            hid,
            datetime.datetime.combine(
                base_sunday + datetime.timedelta(weeks=i), datetime.time(10, 0)
            ),
            db_name=tmp_db_path,
        )
    db.update_streak(hid, db_name=tmp_db_path)
    updated = db.get_habit(hid, db_name=tmp_db_path)
    assert updated.streak == 3


def test_completion_rate():
    reference = datetime.date(2026, 1, 28)
    completion_dates = {reference - datetime.timedelta(days=i) for i in range(0, 28, 2)}
    rate = habit_analysis.calculate_completion_rate_from_dates(
        completion_dates, "daily", reference_date=reference
    )
    assert rate == 0.5


def test_empty_habit_data():
    assert habit_analysis.calculate_longest_streak_from_dates([], "daily") == 0
    assert (
        habit_analysis.calculate_completion_rate_from_dates(
            set(), "daily", reference_date=datetime.date(2026, 1, 28)
        )
        == 0.0
    )

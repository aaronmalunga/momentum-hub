import datetime

from habit_analysis import (
    calculate_completion_rate_from_dates,
    calculate_longest_streak_from_dates,
)


def make_dates(start: datetime.date, days: int):
    return [start + datetime.timedelta(days=i) for i in range(days)]


def test_longest_streak_daily():
    start = datetime.date(2025, 10, 1)
    dates = make_dates(start, 5)  # 5 consecutive days
    assert calculate_longest_streak_from_dates(dates, "daily") == 5


def test_longest_streak_weekly():
    # choose Sundays 3 consecutive weeks
    dates = [
        datetime.date(2025, 10, 5),
        datetime.date(2025, 10, 12),
        datetime.date(2025, 10, 19),
    ]
    assert calculate_longest_streak_from_dates(dates, "weekly") == 3


def test_completion_rate_daily():
    today = datetime.date(2025, 11, 30)
    # last 28 days: create 14 completion dates evenly spread
    completion_dates = {today - datetime.timedelta(days=i * 2) for i in range(14)}
    rate = calculate_completion_rate_from_dates(
        completion_dates, "daily", reference_date=today
    )
    assert abs(rate - (14 / 28)) < 1e-9


def test_completion_rate_weekly():
    today = datetime.date(2025, 11, 30)
    # create completions that map to 2 of the last 4 Sunday-week starts
    completion_dates = {datetime.date(2025, 11, 23), datetime.date(2025, 11, 9)}
    rate = calculate_completion_rate_from_dates(
        completion_dates, "weekly", reference_date=today
    )
    assert abs(rate - 0.5) < 1e-9

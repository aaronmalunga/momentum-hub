import datetime
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

import momentum_db as db
from habit import Habit


def populate_test_db(db_name: str):
    """
    Populates the specified database with 5 predefined habits and 4 weeks of synthetic completion dates.
    """
    db.init_db(db_name)  # Ensures that tables exist before populating

    # 5 predefined habits
    habits_data = [
        {
            "name": "Change beddings",
            "frequency": "weekly",
            "notes": "Wash and change beddings",
            "reminder_time": "09:00",
            "evening_reminder_time": None,
            "streak": 0,
            "is_active": True,
        },
        {
            "name": "Code",
            "frequency": "daily",
            "notes": "Code for at least 1 hour",
            "reminder_time": "10:00",
            "evening_reminder_time": None,
            "streak": 0,
            "is_active": True,
        },
        {
            "name": "Study",
            "frequency": "daily",
            "notes": "Review course materials",
            "reminder_time": "11:00",
            "evening_reminder_time": None,
            "streak": 0,
            "is_active": True,
        },
        {
            "name": "Meditate",
            "frequency": "daily",
            "notes": "Meditate for at least 10 minutes",
            "reminder_time": "07:00",
            "evening_reminder_time": None,
            "streak": 0,
            "is_active": True,
        },
        {
            "name": "Blog",
            "frequency": "weekly",
            "notes": "Write a Data Science blog post",
            "reminder_time": "11:00",
            "evening_reminder_time": None,
            "streak": 0,
            "is_active": True,
        },
    ]

    habit_ids = {}
    # Store the IDs of the created habits from DB for calculating of streaks
    created_habits = []

    for data in habits_data:
        # Create habits a month ago to have 4 weeks of data
        created_at_dt = datetime.datetime.now() - datetime.timedelta(days=328)

        # For weekly habits, make sure they are created on the same day weekly, in this instance, Sunday
        if data["frequency"] == "weekly":
            # Find the most recent Sunday 28 days ago or earlier for weekly habits
            while created_at_dt.weekday() != 6:  # 6 being Sunday
                created_at_dt -= datetime.timedelta(days=1)

        new_habit = Habit(
            name=data["name"],
            frequency=data["frequency"],
            notes=data["notes"],
            reminder_time=data["reminder_time"],
            evening_reminder_time=data["evening_reminder_time"],
            created_at=created_at_dt,
            last_completed=None,  # No completions yet
            is_active=True,
        )
        habit_id = db.add_habit(new_habit, db_name)
        new_habit.id = (
            habit_id  # Assign the ID returned from the database to the habit instance
        )
        db.update_habit(new_habit, db_name)  #
        habit_ids[data["name"]] = habit_id
        created_habits.append(new_habit)

    # Generate synthetic completion dates for the habits( 4 Weeks of data)
    today = (
        datetime.datetime.now()
    )  ### --> Making "Change beddings" with both streak and completion rate tests
    change_beddings_id = habit_ids["Change beddings"]
    change_beddings_habit_obj = next(
        h for h in created_habits if h.name == "Change beddings"
    )

    # Create exactly 7 consecutive weeks for the streak test, starting from 11 weeks ago
    for i in range(7):
        completion_date = today - datetime.timedelta(weeks=11 - i)  # Start 11 weeks ago
        # Find the Sunday of that week
        while completion_date.weekday() != 6:
            completion_date -= datetime.timedelta(days=1)
        db.add_completion(change_beddings_id, completion_date, db_name)

    # For the last 4 weeks (completion rate test), complete exactly 2 weeks
    for i in range(4):
        current_date = today - datetime.timedelta(weeks=i)
        # Find the Sunday of this week
        while current_date.weekday() != 6:
            current_date -= datetime.timedelta(days=1)
        # Only complete weeks 1 and 3 (second and fourth weeks)
        if i in [1, 3]:
            db.add_completion(change_beddings_id, current_date, db_name)

    ### --> Make "Code" have a perfect 28 day streak
    code_daily_id = habit_ids["Code"]
    for i in range(28, 0, -1):
        current_date = today - datetime.timedelta(days=i)
        db.add_completion(code_daily_id, current_date, db_name)
    ### --> Make "Study" have a known pattern: 3 misses in first week, then perfect
    study_id = habit_ids["Study"]
    # Create exactly 25 completions in 28 days, with 3 specific missed days
    for i in range(28, 0, -1):
        current_date = today - datetime.timedelta(days=i)
        # Skip days 26, 25, and 24 ago (these will be our missed days)
        if i not in [26, 25, 24]:
            db.add_completion(study_id, current_date, db_name)

    ### --> Make "Meditate" have a perfect 15-day streak
    meditate_id = habit_ids["Meditate"]
    for i in range(15, 0, -1):
        current_date = today - datetime.timedelta(days=i)
        db.add_completion(meditate_id, current_date, db_name)
    ### --> Make "Blog" a perfect weekly streak (7 weeks)
    blog_id = habit_ids["Blog"]
    blog_habit_obj = next(h for h in created_habits if h.name == "Blog")
    # Create exactly 7 weekly completions
    for i in range(7):
        completion_date = today - datetime.timedelta(weeks=i)
        # Adjust to the nearest Sunday
        while completion_date.weekday() != 6:  # 6 is Sunday
            completion_date -= datetime.timedelta(days=1)
        db.add_completion(blog_id, completion_date, db_name)

    print(f"Test database '{db_name}' populated with sample data.")


if __name__ == "__main__":
    #
    if os.path.exists("test.db"):
        os.remove("test.db")
    populate_test_db("test.db")

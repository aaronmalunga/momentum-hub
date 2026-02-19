import atexit
import datetime
import sqlite3
import threading
from typing import List, Optional

from .habit import Habit

DB_NAME = "momentum.db"

# Global list to track manually created connections for cleanup
_open_connections = []


class TrackedConnection:
    """A wrapper for SQLite connections that tracks them for proper cleanup."""

    # Design rationale: tests open many connections; tracking ensures teardown
    # closes everything deterministically to avoid file locks on Windows.

    def __init__(self, conn):
        self._conn = conn
        self._closed = False
        _open_connections.append(self)

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if not self._closed and self._conn:
            self._conn.close()
            self._closed = True
        # Remove from tracked connections
        if self in _open_connections:
            _open_connections.remove(self)

    def __del__(self):
        # Ensure underlying connection is closed if GC runs
        try:
            self.close()
        except Exception:
            pass

    def __getattr__(self, name):
        # Delegate all other attributes to the underlying connection
        return getattr(self._conn, name)

    def __bool__(self):
        return not self._closed


def get_connection(db_name: str = DB_NAME):
    """
    Get's a connection to the sqlite database(db) and Returns a TrackedConnection object.

    When used with a context manager (with statement), the connection will be
    automatically closed on exit. Manually created connections should be tracked
    for cleanup.
    """
    conn = sqlite3.connect(db_name)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    # Return tracked connection wrapper
    return TrackedConnection(conn)


def close_all_connections():
    """
    Closes all tracked database connections. Used for testing to ensure clean teardown.
    Handles both closed and open connections gracefully.
    """
    for tracked_conn in _open_connections[
        :
    ]:  # Create a copy to avoid modification during iteration
        try:
            if tracked_conn:  # This will call __bool__ which checks if not closed
                tracked_conn.close()
        except Exception:
            pass  # Ignore errors if already closed
    _open_connections.clear()


atexit.register(close_all_connections)


def init_db(db_name: str = DB_NAME):
    """
    Creates habits and completions tables if they do not exist.
    Adds reactivated_at field if missing.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()

        # Create habits table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS habits(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT NOT NULL,
           frequency TEXT NOT NULL,
           notes TEXT,
           reminder_time TEXT,
           evening_reminder_time TEXT,
           streak INTEGER DEFAULT 0,
           created_at TEXT,
           last_completed TEXT,
           is_active INTEGER DEFAULT 1,
           reactivated_at TEXT
        );
        """
        )

        # Add reactivated_at column if it doesn't exist (for migrations)
        cursor.execute("PRAGMA table_info(habits);")
        columns = [row[1] for row in cursor.fetchall()]
        if "reactivated_at" not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN reactivated_at TEXT;")

        # Create completions table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS completions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
        """
        )

        # Create categories table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        );
        """
        )

        # Create goals table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            target_period_days INTEGER DEFAULT 28,
            target_completions INTEGER,
            start_date TEXT,
            end_date TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
        """
        )

        # Add category_id column to habits table if it doesn't exist
        cursor.execute("PRAGMA table_info(habits);")
        columns = [row[1] for row in cursor.fetchall()]
        if "category_id" not in columns:
            cursor.execute(
                "ALTER TABLE habits ADD COLUMN category_id INTEGER REFERENCES categories(id);"
            )

        conn.commit()


def clear_demo_data(db_name: str = DB_NAME) -> None:
    """
    Clears all demo data from the database.
    Used in demo mode to ensure fresh demo content.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        # Delete in order to respect foreign keys (delete dependent tables first)
        cursor.execute("DELETE FROM goals;")
        cursor.execute("DELETE FROM completions;")
        cursor.execute("DELETE FROM habits;")
        cursor.execute("DELETE FROM categories;")
        conn.commit()


def add_habit(habit: Habit, db_name: str = DB_NAME) -> int:
    """
    Adds a new habit to database and returns newly created habit id.
    Ensures created_at is always set.
    """
    if habit.created_at is None:
        habit.created_at = datetime.datetime.now()
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO habits(
                name, frequency, notes, reminder_time, evening_reminder_time,
                streak, created_at, last_completed, is_active, reactivated_at, category_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,
            (
                habit.name,
                habit.frequency,
                habit.notes,
                habit.reminder_time,
                habit.evening_reminder_time,
                habit.streak,
                habit.created_at.isoformat() if habit.created_at else None,
                habit.last_completed.isoformat() if habit.last_completed else None,
                int(habit.is_active),
                habit.reactivated_at.isoformat() if habit.reactivated_at else None,
                habit.category_id,
            ),
        )
        conn.commit()
        """
        Get's id assigned by the database
        """
        habit_id = cursor.lastrowid
    return habit_id


def get_habit(habit_id: int, db_name: str = DB_NAME) -> Optional[Habit]:
    """
    Get habit from database by habit id
    A habit object is returen if found, otherwise None is returned

    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                   streak, created_at, last_completed, is_active, reactivated_at, category_id
            FROM habits
            WHERE id = ?

""",
            (habit_id,),
        )
        row = cursor.fetchone()

    if row:
        # Map  row to a Habit object using thee from_dict method
        habit_dict = {
            "id": row[0],
            "name": row[1],
            "frequency": row[2],
            "notes": row[3],
            "reminder_time": row[4],
            "evening_reminder_time": row[5],
            "streak": row[6],
            "created_at": (row[7]),
            "last_completed": (row[8]),
            "is_active": bool(row[9]),
            "reactivated_at": (row[10]),
            "category_id": row[11],
        }
        return Habit.from_dict(habit_dict)
    else:
        return None


def update_habit(habit: Habit, db_name: str = DB_NAME) -> None:
    """
    Updates an already existing habit to the database
    where the habit is a valid id.
    """

    if habit.id is None:
        raise ValueError("Habit id must be set before updating.")

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE habits
            SET name = ?, frequency = ?, notes = ?, reminder_time = ?,
                evening_reminder_time = ?, streak = ?, created_at = ?,
                last_completed = ?, is_active = ?, reactivated_at = ?, category_id = ?
            WHERE id = ? """,
            (
                habit.name,
                habit.frequency,
                habit.notes,
                habit.reminder_time,
                habit.evening_reminder_time,
                habit.streak,
                habit.created_at.isoformat() if habit.created_at else None,
                habit.last_completed.isoformat() if habit.last_completed else None,
                int(habit.is_active),
                habit.reactivated_at.isoformat() if habit.reactivated_at else None,
                habit.category_id,
                habit.id,
            ),
        )
        conn.commit()


def delete_habit(habit_id: int, db_name: str = DB_NAME) -> None:
    """
    Soft deletes a habit from the database by its id.
    Soft delete allows the habit to be deactivated in the database, yet accessible for analysis and history
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE habits
            SET is_active = 0
            WHERE id = ?
        """,
            (habit_id,),
        )
        conn.commit()


def reactivate_habit(habit_id: int, db_name: str = DB_NAME) -> None:
    """
    Reactivates a soft-deleted habit in the database by its id.
    Resets the streak to 0, preserves last_completed, and sets reactivated_at to now.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().isoformat()
        cursor.execute(
            """
            UPDATE habits
            SET is_active = 1, streak = 0, reactivated_at = ?
            WHERE id = ?
        """,
            (now, habit_id),
        )
        conn.commit()


def get_all_habits(active_only: bool = True, db_name: str = DB_NAME) -> list[Habit]:
    """
    Fetches all habits from the database.
    If active_only is True, only active habits are returned, where is_active = 1 and a list of habit ojects is returned.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                """
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at, category_id
                FROM habits
                WHERE is_active = 1
            """
            )
        else:
            cursor.execute(
                """
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at, category_id
                FROM habits
            """
            )

        rows = cursor.fetchall()
    habits = []
    for row in rows:
        habit_dict = {
            "id": row[0],
            "name": row[1],
            "frequency": row[2],
            "notes": row[3],
            "reminder_time": row[4],
            "evening_reminder_time": row[5],
            "streak": row[6],
            "created_at": row[7],
            "last_completed": row[8],
            "is_active": bool(row[9]),
            "reactivated_at": row[10],
            "category_id": row[11],
        }
        habits.append(Habit.from_dict(habit_dict))

    return habits


_completion_lock = threading.Lock()


def add_completion(
    habit_id: int, dt: datetime.datetime, db_name: str = DB_NAME
) -> None:
    """
    Records a habit completion in database,
    Inserts a new row in the completions table with the habit_id and datetime.
    Prevents duplicate completions for the same period (day or week).
    For weekly habits, uses American week (Sunday to Saturday).
    Only considers completions after the most recent reactivation (if any).
    Robustly handles new habits and prevents false duplicate errors.
    Uses a thread lock to ensure concurrency safety.
    """
    with _completion_lock:
        habit = get_habit(habit_id, db_name)
        if not habit:
            raise ValueError("Habit not found.")
        completions = get_completions(habit_id, db_name)
        dt_date = dt.date()
        # Only consider completions after reactivated_at (if set)
        if habit.reactivated_at:
            completions = [c for c in completions if c >= habit.reactivated_at]
        # Defensive: If no completions, always allow
        if not completions:
            pass  # No duplicate possible
        elif habit.frequency == "daily":
            # Only one completion per day
            for c in completions:
                if c.date() == dt_date:
                    raise ValueError("This habit has already been completed.")
        elif habit.frequency == "weekly":
            # Only one completion per American week (Sunday to Saturday)
            week_start = dt_date - datetime.timedelta(
                days=dt_date.weekday() + 1 if dt_date.weekday() < 6 else 0
            )
            for c in completions:
                c_date = c.date()
                c_week_start = c_date - datetime.timedelta(
                    days=c_date.weekday() + 1 if c_date.weekday() < 6 else 0
                )
                if c_week_start == week_start:
                    raise ValueError(
                        "This habit has already been completed for the week."
                    )
        with get_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO completions (habit_id, date)
                VALUES (?, ?)
            """,
                (habit_id, dt.isoformat()),
            )
            conn.commit()


def get_completions(habit_id: int, db_name: str = DB_NAME) -> list[datetime.datetime]:
    """
    Fetches alll completions for a specified habit from the database.
    A list of datetime.datetime objects is returned is order of ascention date

    """

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """        SELECT date
            FROM completions
            WHERE habit_id = ?
            ORDER BY date ASC

        """,
            (habit_id,),
        )
        rows = cursor.fetchall()

    completions = []
    for row in rows:
        completion_dt_str = row[0]
        if completion_dt_str:
            completions.append(datetime.datetime.fromisoformat(completion_dt_str))

    return completions


def update_streak(habit_id: int, db_name: str = DB_NAME) -> None:
    """
    Recalculates and updates the current streak for a habit based on its completions.
    This ensures the streak is correct if completions are added/removed or after data restoration.
    Only considers completions after the most recent reactivation.
    """
    habit = get_habit(habit_id, db_name)
    if not habit:
        return
    completions = get_completions(habit_id, db_name)
    # Only consider completions after reactivation
    if habit.reactivated_at:
        completions = [c for c in completions if c >= habit.reactivated_at]
    if not completions:
        habit.streak = 0
        habit.last_completed = None
        update_habit(habit, db_name)
        return
    if habit.frequency == "weekly":
        if len(completions) == 1:
            habit.streak = 1
            habit.last_completed = completions[-1]
            update_habit(habit, db_name)
            return
        # Find the Saturday of each completion week
        saturday_set = set()
        for c in completions:
            date = c.date()
            while date.weekday() != 5:  # 5 is Saturday
                date += datetime.timedelta(days=1)
            saturday_set.add(date)
        saturdays = sorted(saturday_set)
        if not saturdays:
            habit.streak = 0
            habit.last_completed = None
            update_habit(habit, db_name)
            return
        # Calculate current streak (consecutive weeks up to the most recent)
        current_streak = 1
        for i in range(len(saturdays) - 2, -1, -1):
            if (saturdays[i + 1] - saturdays[i]).days == 7:
                current_streak += 1
            else:
                break
        habit.streak = current_streak
        habit.last_completed = completions[-1]
    else:  # daily
        # Calculate current streak (consecutive days up to the most recent)
        current_streak = 1
        for i in range(len(completions) - 2, -1, -1):
            if (completions[i + 1].date() - completions[i].date()).days == 1:
                current_streak += 1
            else:
                break
        habit.streak = current_streak
        habit.last_completed = completions[-1]
    update_habit(habit, db_name)


def export_completions_to_csv(
    output_path: str = "completions.csv", db_name: str = DB_NAME
):
    """
    Exports all completions to a CSV file.
    """
    import csv
    from pathlib import Path

    with get_connection(db_name) as conn:
        cursor = conn.cursor()

        query = """
        SELECT c.id AS completion_id,
               c.habit_id AS habit_id,
               COALESCE(h.name, '') AS habit_name,
               COALESCE(h.frequency, '') AS frequency,
               c.date AS completion_iso
        FROM completions c
        LEFT JOIN habits h ON c.habit_id = h.id
        ORDER BY c.date ASC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

    outp = Path(output_path)
    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Exported {len(rows)} rows to {output_path}")


# Category functions
def add_category(category, db_name: str = DB_NAME) -> int:
    """
    Adds a new category to the database and returns the created category id.
    """
    if category.created_at is None:
        category.created_at = datetime.datetime.now()
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO categories (name, description, color, is_active, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                category.name,
                category.description,
                category.color,
                int(category.is_active),
                category.created_at.isoformat() if category.created_at else None,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_category(category_id: int, db_name: str = DB_NAME):
    """
    Gets a category from the database by id.
    """
    from .category import Category

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, description, color, is_active, created_at
            FROM categories
            WHERE id = ?
        """,
            (category_id,),
        )
        row = cursor.fetchone()

    if row:
        category_dict = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "color": row[3],
            "is_active": bool(row[4]),
            "created_at": row[5],
        }
        return Category.from_dict(category_dict)
    return None


def update_category(category, db_name: str = DB_NAME) -> None:
    """
    Updates an existing category in the database.
    """
    if category.id is None:
        raise ValueError("Category id must be set before updating.")
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE categories
            SET name = ?, description = ?, color = ?, is_active = ?
            WHERE id = ?
        """,
            (
                category.name,
                category.description,
                category.color,
                int(category.is_active),
                category.id,
            ),
        )
        conn.commit()


def delete_category(category_id: int, db_name: str = DB_NAME) -> None:
    """
    Soft deletes a category from the database by setting is_active to 0.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE categories
            SET is_active = 0
            WHERE id = ?
        """,
            (category_id,),
        )
        conn.commit()


def get_all_categories(active_only: bool = True, db_name: str = DB_NAME) -> List:
    """
    Gets all categories from the database.
    """
    from .category import Category

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                """
                SELECT id, name, description, color, is_active, created_at
                FROM categories
                WHERE is_active = 1
            """
            )
        else:
            cursor.execute(
                """
                SELECT id, name, description, color, is_active, created_at
                FROM categories
            """
            )
        rows = cursor.fetchall()

    categories = []
    for row in rows:
        category_dict = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "color": row[3],
            "is_active": bool(row[4]),
            "created_at": row[5],
        }
        categories.append(Category.from_dict(category_dict))
    return categories


def get_habits_by_category(
    category_id: int, active_only: bool = True, db_name: str = DB_NAME
) -> List[Habit]:
    """
    Gets all habits for a specific category.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                """
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at, category_id
                FROM habits
                WHERE category_id = ? AND is_active = 1
            """,
                (category_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at, category_id
                FROM habits
                WHERE category_id = ?
            """,
                (category_id,),
            )
        rows = cursor.fetchall()

    habits = []
    for row in rows:
        habit_dict = {
            "id": row[0],
            "name": row[1],
            "frequency": row[2],
            "notes": row[3],
            "reminder_time": row[4],
            "evening_reminder_time": row[5],
            "streak": row[6],
            "created_at": row[7],
            "last_completed": row[8],
            "is_active": bool(row[9]),
            "reactivated_at": row[10],
            "category_id": row[11],
        }
        habits.append(Habit.from_dict(habit_dict))
    return habits


# Goal functions
def add_goal(goal, db_name: str = DB_NAME) -> int:
    """
    Adds a new goal to the database and returns the created goal id.
    """
    if goal.created_at is None:
        goal.created_at = datetime.datetime.now()
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (habit_id, target_period_days, target_completions,
                              start_date, end_date, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                goal.habit_id,
                goal.target_period_days,
                goal.target_completions,
                goal.start_date.isoformat() if goal.start_date else None,
                goal.end_date.isoformat() if goal.end_date else None,
                int(goal.is_active),
                goal.created_at.isoformat() if goal.created_at else None,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_goal(goal_id: int, db_name: str = DB_NAME):
    """
    Gets a goal from the database by id.
    """
    from .goal import Goal

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, habit_id, target_period_days, target_completions,
                   start_date, end_date, is_active, created_at
            FROM goals
            WHERE id = ?
        """,
            (goal_id,),
        )
        row = cursor.fetchone()

    if row:
        goal_dict = {
            "id": row[0],
            "habit_id": row[1],
            "target_period_days": row[2],
            "target_completions": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "is_active": bool(row[6]),
            "created_at": row[7],
        }
        return Goal.from_dict(goal_dict)
    return None


def update_goal(goal, db_name: str = DB_NAME) -> None:
    """
    Updates an existing goal in the database.
    """
    if goal.id is None:
        raise ValueError("Goal id must be set before updating.")
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE goals
            SET habit_id = ?, target_period_days = ?, target_completions = ?,
                start_date = ?, end_date = ?, is_active = ?
            WHERE id = ?
        """,
            (
                goal.habit_id,
                goal.target_period_days,
                goal.target_completions,
                goal.start_date.isoformat() if goal.start_date else None,
                goal.end_date.isoformat() if goal.end_date else None,
                int(goal.is_active),
                goal.id,
            ),
        )
        conn.commit()


def delete_goal(goal_id: int, db_name: str = DB_NAME) -> None:
    """
    Soft deletes a goal from the database by setting is_active to 0.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE goals
            SET is_active = 0
            WHERE id = ?
        """,
            (goal_id,),
        )
        conn.commit()


def get_all_goals(active_only: bool = True, db_name: str = DB_NAME) -> List:
    """
    Gets all goals from the database.
    """
    from .goal import Goal

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute(
                """
                SELECT id, habit_id, target_period_days, target_completions,
                       start_date, end_date, is_active, created_at
                FROM goals
                WHERE is_active = 1
            """
            )
        else:
            cursor.execute(
                """
                SELECT id, habit_id, target_period_days, target_completions,
                       start_date, end_date, is_active, created_at
                FROM goals
            """
            )
        rows = cursor.fetchall()

    goals = []
    for row in rows:
        goal_dict = {
            "id": row[0],
            "habit_id": row[1],
            "target_period_days": row[2],
            "target_completions": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "is_active": bool(row[6]),
            "created_at": row[7],
        }
        goals.append(Goal.from_dict(goal_dict))
    return goals

import sqlite3
import datetime
from typing import Optional, List, Dict, Any
from habit import Habit

DB_NAME = 'momentum.db'

# Global list to track open connections for testing purposes
_open_connections = []

def get_connection(db_name: str = DB_NAME):
    """
    Get's a connection to the sqlite database(db) and Returns a sqlite3.Connection object.
    """
    conn = sqlite3.connect(db_name)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    _open_connections.append(conn)
    return conn


def close_all_connections():
    """
    Closes all tracked database connections. Used for testing to ensure clean teardown.
    """
    global _open_connections
    for conn in _open_connections:
        try:
            conn.close()
        except Exception:
            pass  # Ignore errors if already closed
    _open_connections = []


def init_db(db_name: str = DB_NAME):
    """
    Creates habits and completions tables if they do not exist.
    Adds reactivated_at field if missing.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()

        # Create habits table
        cursor.execute("""
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
        """)

        # Add reactivated_at column if it doesn't exist (for migrations)
        cursor.execute("PRAGMA table_info(habits);")
        columns = [row[1] for row in cursor.fetchall()]
        if 'reactivated_at' not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN reactivated_at TEXT;")

        # Create completions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        );
        """)
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
        cursor.execute("""
            INSERT INTO habits(
                name, frequency, notes, reminder_time, evening_reminder_time,
                streak, created_at, last_completed, is_active, reactivated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (        habit.name,
            habit.frequency,
            habit.notes,
            habit.reminder_time,
            habit.evening_reminder_time,
            habit.streak,
            habit.created_at.isoformat() if habit.created_at else None,
            habit.last_completed.isoformat() if habit.last_completed else None,
            int(habit.is_active),
            habit.reactivated_at.isoformat() if habit.reactivated_at else None
        ))
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
        cursor.execute("""
            SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                   streak, created_at, last_completed, is_active, reactivated_at
            FROM habits
            WHERE id = ?

""", (habit_id,))
        row = cursor.fetchone()

    if row:
        # Map  row to a Habit object using thee from_dict method
        habit_dict = {
            'id': row[0],
            'name': row[1],
            'frequency': row[2],
            'notes': row[3],
            'reminder_time': row[4],
            'evening_reminder_time': row[5],
            'streak': row[6],
            'created_at': (row[7]) ,
            'last_completed': (row[8]) ,
            'is_active': bool(row[9]),
            'reactivated_at': (row[10])
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
        cursor.execute("""
            UPDATE habits
            SET name = ?, frequency = ?, notes = ?, reminder_time = ?,
                evening_reminder_time = ?, streak = ?, created_at = ?,
                last_completed = ?, is_active = ?, reactivated_at = ?
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
                habit.id
        ))
        conn.commit()

def delete_habit(habit_id: int,db_name: str = DB_NAME) -> None:
    """
    Soft deletes a habit from the database by its id.
    Soft delete allows the habit to be deactivated in the database, yet accessible for analysis and history
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE habits
            SET is_active = 0
            WHERE id = ?
        """, (habit_id,))
        conn.commit()

def reactivate_habit(habit_id: int, db_name: str = DB_NAME) -> None:
    """
    Reactivates a soft-deleted habit in the database by its id.
    Resets the streak to 0, preserves last_completed, and sets reactivated_at to now.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().isoformat()
        cursor.execute("""
            UPDATE habits
            SET is_active = 1, streak = 0, reactivated_at = ?
            WHERE id = ?
        """, (now, habit_id))
        conn.commit()


def get_all_habits(active_only: bool = True, db_name: str = DB_NAME) -> list[Habit]:
    """
    Fetches all habits from the database.
    If active_only is True, only active habits are returned, where is_active = 1 and a list of habit ojects is returned.
    """
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute("""
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at
                FROM habits
                WHERE is_active = 1
            """)
        else:
            cursor.execute("""
                SELECT id, name, frequency, notes, reminder_time, evening_reminder_time,
                       streak, created_at, last_completed, is_active, reactivated_at
                FROM habits
            """)

        rows = cursor.fetchall()
    habits = []
    for row in rows:
        habit_dict = {
            'id': row[0],
            'name': row[1],
            'frequency': row[2],
            'notes': row[3],
            'reminder_time': row[4],
            'evening_reminder_time': row[5],
            'streak': row[6],
            'created_at': row[7],
            'last_completed': row[8],
            'is_active': bool(row[9]),
            'reactivated_at': row[10]
        }
        habits.append(Habit.from_dict(habit_dict))

    return habits

def add_completion(habit_id: int, dt: datetime.datetime, db_name: str = DB_NAME) -> None:
    """
    Records a habit completion in database,
    Inserts a new row in the completions table with the habit_id and datetime.
    Prevents duplicate completions for the same period (day or week).
    For weekly habits, uses American week (Sunday to Saturday).
    Only considers completions after the most recent reactivation (if any).
    Robustly handles new habits and prevents false duplicate errors.
    """
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
    elif habit.frequency == 'daily':
        # Only one completion per day
        for c in completions:
            if c.date() == dt_date:
                raise ValueError("This habit has already been completed.")
    elif habit.frequency == 'weekly':
        # Only one completion per American week (Sunday to Saturday)
        week_start = dt_date - datetime.timedelta(days=dt_date.weekday() + 1 if dt_date.weekday() < 6 else 0)
        week_end = week_start + datetime.timedelta(days=6)
        for c in completions:
            c_date = c.date()
            c_week_start = c_date - datetime.timedelta(days=c_date.weekday() + 1 if c_date.weekday() < 6 else 0)
            if c_week_start == week_start:
                raise ValueError("This habit has already been completed for the week.")
    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO completions (habit_id, date)
            VALUES (?, ?)
        """, (habit_id, dt.isoformat()))
        conn.commit()


def get_completions(habit_id: int, db_name: str = DB_NAME) -> list[datetime.datetime]:

    """
    Fetches alll completions for a specified habit from the database.
    A list of datetime.datetime objects is returned is order of ascention date

    """

    with get_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""        SELECT date
            FROM completions
            WHERE habit_id = ?
            ORDER BY date ASC

        """, (habit_id,))
        rows = cursor.fetchall()

    completions = []
    for row in rows:
        completion_dt_str = row [0]
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
    if habit.frequency == 'weekly':
        if len(completions) == 1:
            habit.streak = 1
            habit.last_completed = completions[-1]
            update_habit(habit, db_name)
            return
        # Find the Saturday of each completion week
        saturdays = set()
        for c in completions:
            date = c.date()
            while date.weekday() != 5:  # 5 is Saturday
                date += datetime.timedelta(days=1)
            saturdays.add(date)
        saturdays = sorted(saturdays)
        if not saturdays:
            habit.streak = 0
            habit.last_completed = None
            update_habit(habit, db_name)
            return
        # Calculate current streak (consecutive weeks up to the most recent)
        current_streak = 1
        for i in range(len(saturdays)-2, -1, -1):
            if (saturdays[i+1] - saturdays[i]).days == 7:
                current_streak += 1
            else:
                break
        habit.streak = current_streak
        habit.last_completed = completions[-1]
    else:  # daily
        # Calculate current streak (consecutive days up to the most recent)
        current_streak = 1
        for i in range(len(completions)-2, -1, -1):
            if (completions[i+1].date() - completions[i].date()).days == 1:
                current_streak += 1
            else:
                break
        habit.streak = current_streak
        habit.last_completed = completions[-1]
    update_habit(habit, db_name)


def export_completions_to_csv(output_path: str = "completions.csv", db_name: str = DB_NAME):
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


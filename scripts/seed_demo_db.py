"""
Seed demo database for Momentum CLI.

This script mirrors the seeder used in the development venv but chooses a
safe default for local runs. When running under CI (detected by the
`GITHUB_ACTIONS` or `CI` environment variables) the default target becomes
`momentum.db` so tests that expect `momentum.db` are satisfied.

Usage:
    python scripts/seed_demo_db.py
    python scripts/seed_demo_db.py --db momentum.db --overwrite

"""

import argparse
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default: use the real momentum.db in CI so tests find it, otherwise use
# a demo DB locally to avoid accidental overwrites.
if os.getenv("GITHUB_ACTIONS") or os.getenv("CI"):
    DEFAULT_DB = Path("momentum.db")
else:
    DEFAULT_DB = Path("momentum_demo.db")


def create_schema(conn):
    cur = conn.cursor()
    cur.execute(
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
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS completions(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       habit_id INTEGER NOT NULL,
       date TEXT NOT NULL,
       FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );
    """
    )
    conn.commit()


def seed_data(conn):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.cursor()

    habits = [
        (
            "Read 20 pages",
            "daily",
            "Demo habit: reading",
            "08:00",
            "20:00",
            5,
            now,
            now,
            1,
            None,
        ),
        (
            "Stretch 10 min",
            "daily",
            "Morning stretch",
            "07:00",
            "19:00",
            3,
            now,
            now,
            1,
            None,
        ),
    ]
    cur.executemany(
        """
        INSERT INTO habits (name, frequency, notes, reminder_time, evening_reminder_time,
                            streak, created_at, last_completed, is_active, reactivated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        habits,
    )
    conn.commit()

    cur.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (1, now))
    cur.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (2, now))
    conn.commit()


def show_preview(conn, db_path: Path):
    cur = conn.cursor()
    print(" DEMO DATABASE SEEDED SUCCESSFULLY!\n")

    print(" Habits:")
    print("-" * 70)
    for row in cur.execute(
        "SELECT id, name, frequency, streak, is_active FROM habits;"
    ):
        print(
            f"ID: {row[0]} | Name: {row[1]} | Freq: {row[2]} | Streak: {row[3]} | Active: {row[4]}"
        )

    print("\n Completions:")
    print("-" * 70)
    for row in cur.execute("SELECT id, habit_id, date FROM completions;"):
        print(f"ID: {row[0]} | Habit_ID: {row[1]} | Date: {row[2]}")

    print("\n Database ready at:", Path(db_path).resolve(), "\n")


def main():
    parser = argparse.ArgumentParser(description="Seed a demo database for Momentum")
    parser.add_argument(
        "--db",
        dest="db_path",
        default=str(DEFAULT_DB),
        help="Target database file (default: momentum_demo.db or momentum.db in CI)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the target database if it exists",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if db_path.exists() and not args.overwrite:
        print(
            f"Target {db_path} already exists. Use --overwrite to replace it or choose a different --db path."
        )
        print(
            "Tip: run with --db momentum_demo.db (the default) to keep the primary "
            "momentum.db safe."
        )
        return

    if db_path.exists() and args.overwrite:
        # Attempt to run a backup helper if present (best-effort)
        backup_script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "maintenance"
            / "backup_db.py"
        )
        if backup_script.exists():
            print(
                f"Creating backup of existing {db_path} before overwrite using {backup_script}..."
            )
            try:
                subprocess.run(
                    [sys.executable, str(backup_script), "--src", str(db_path)],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"Backup helper failed (exit {e.returncode}). Aborting overwrite to avoid data loss."
                )
                return
            except Exception as e:
                print(
                    f"Failed to run backup helper: {e}. Aborting overwrite to avoid data loss."
                )
                return
        else:
            print(
                f"Warning: backup helper not found at {backup_script}. Continuing without backup."
            )

        print(f"Overwriting existing {db_path} for demo...")
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    create_schema(conn)
    seed_data(conn)
    show_preview(conn, db_path)
    conn.close()


if __name__ == "__main__":
    main()

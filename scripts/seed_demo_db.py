#!/usr/bin/env python3
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
import sqlite3
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Default: use the real momentum.db in CI so tests find it, otherwise use
# a demo DB locally to avoid accidental overwrites.
if os.getenv("GITHUB_ACTIONS") or os.getenv("CI"):
    DEFAULT_DB = Path("momentum.db")
else:
    DEFAULT_DB = Path("momentum_demo.db")

def create_schema(conn):
    cur = conn.cursor()
    cur.execute("""
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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS completions(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       habit_id INTEGER NOT NULL,
       date TEXT NOT NULL,
       FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );
    """)

    # Create categories table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        color TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT
    );
    """)

    # Create goals table
    cur.execute("""
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
    """)

    # Add category_id column to habits table if it doesn't exist
    cur.execute("PRAGMA table_info(habits);")
    columns = [row[1] for row in cur.fetchall()]
    if 'category_id' not in columns:
        cur.execute("ALTER TABLE habits ADD COLUMN category_id INTEGER REFERENCES categories(id);")

    conn.commit()

def seed_data(conn):
    now = datetime.utcnow().isoformat()
    cur = conn.cursor()

    # Create demo categories
    categories = [
        ("Health & Fitness", "Habits related to physical health and exercise", "#FF6B6B", now),
        ("Personal Development", "Habits for learning and self-improvement", "#4ECDC4", now),
        ("Productivity", "Habits to improve efficiency and organization", "#45B7D1", now),
        ("Mindfulness & Wellness", "Habits for mental health and relaxation", "#96CEB4", now),
        ("Social & Relationships", "Habits for building and maintaining relationships", "#FFEAA7", now),
        ("Finance & Money", "Habits for financial planning and management", "#DDA0DD", now),
        ("Creativity & Hobbies", "Habits for creative expression and leisure activities", "#98D8C8", now),
        ("Home & Environment", "Habits for maintaining home and environmental care", "#F7DC6F", now)
    ]
    cur.executemany("""
        INSERT INTO categories (name, description, color, created_at)
        VALUES (?, ?, ?, ?)
    """, categories)
    conn.commit()

    # Get category IDs
    category_ids = {}
    for row in cur.execute("SELECT id, name FROM categories"):
        category_ids[row[1]] = row[0]

    habits = [
        ("Read 20 pages", "daily", "Demo habit: reading", "08:00", "20:00", 5, now, now, 1, None, category_ids["Personal Development"]),
        ("Stretch 10 min", "daily", "Morning stretch", "07:00", "19:00", 3, now, now, 1, None, category_ids["Health & Fitness"])
    ]
    cur.executemany("""
        INSERT INTO habits (name, frequency, notes, reminder_time, evening_reminder_time,
                            streak, created_at, last_completed, is_active, reactivated_at, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, habits)
    conn.commit()

    # Create demo goals
    goals = [
        (1, 30, 30, now, (datetime.utcnow() + timedelta(days=30)).isoformat(), now),  # Read 20 pages: 30/30 days
        (2, 28, 28, now, (datetime.utcnow() + timedelta(days=28)).isoformat(), now)   # Stretch: 28/28 days
    ]
    cur.executemany("""
        INSERT INTO goals (habit_id, target_period_days, target_completions, start_date, end_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, goals)
    conn.commit()

    cur.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (1, now))
    cur.execute("INSERT INTO completions (habit_id, date) VALUES (?, ?)", (2, now))
    conn.commit()

def show_preview(conn, db_path: Path):
    cur = conn.cursor()
    print("\nDemo database seeded successfully!\n")

    print("Categories:")
    print("-" * 70)
    for row in cur.execute("SELECT id, name, description, color FROM categories;"):
        print(f"ID: {row[0]} | Name: {row[1]} | Desc: {row[2]} | Color: {row[3]}")

    print("\nHabits:")
    print("-" * 70)
    for row in cur.execute("SELECT h.id, h.name, h.frequency, h.streak, h.is_active, c.name as category FROM habits h LEFT JOIN categories c ON h.category_id = c.id;"):
        category = row[5] if row[5] else "None"
        print(f"ID: {row[0]} | Name: {row[1]} | Freq: {row[2]} | Streak: {row[3]} | Active: {row[4]} | Category: {category}")

    print("\nGoals:")
    print("-" * 70)
    for row in cur.execute("SELECT g.id, h.name, g.target_completions, g.target_period_days FROM goals g JOIN habits h ON g.habit_id = h.id;"):
        print(f"ID: {row[0]} | Habit: {row[1]} | Target: {row[2]}/{row[3]} days")

    print("\nCompletions:")
    print("-" * 70)
    for row in cur.execute("SELECT id, habit_id, date FROM completions;"):
        print(f"ID: {row[0]} | Habit_ID: {row[1]} | Date: {row[2]}")

    print("\nDatabase ready at:", Path(db_path).resolve(), "\n")

def main():
    parser = argparse.ArgumentParser(description="Seed a demo database for Momentum")
    parser.add_argument("--db", dest="db_path", default=str(DEFAULT_DB),
                        help="Target database file (default: momentum_demo.db or momentum.db in CI)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite the target database if it exists")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if db_path.exists() and not args.overwrite:
        print(f"Target {db_path} already exists. Use --overwrite to replace it or choose a different --db path.")
        print(f"Tip: run with --db momentum_demo.db (the default) to keep your primary momentum.db safe.")
        return

    if db_path.exists() and args.overwrite:
        # Attempt to run a backup helper if present (best-effort)
        backup_script = Path(__file__).resolve().parents[1] / "scripts" / "maintenance" / "backup_db.py"
        if backup_script.exists():
            print(f"Creating backup of existing {db_path} before overwrite using {backup_script}...")
            try:
                subprocess.run([sys.executable, str(backup_script), "--src", str(db_path)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Backup helper failed (exit {e.returncode}). Aborting overwrite to avoid data loss.")
                return
            except Exception as e:
                print(f"Failed to run backup helper: {e}. Aborting overwrite to avoid data loss.")
                return
        else:
            print(f"Warning: backup helper not found at {backup_script}. Continuing without backup.")

        print(f"Overwriting existing {db_path} for demo...")
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    create_schema(conn)
    seed_data(conn)
    show_preview(conn, db_path)
    conn.close()

if __name__ == "__main__":
    main()

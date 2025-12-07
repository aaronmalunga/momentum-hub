import sqlite3
from datetime import datetime, timedelta


def _to_date(dt):
    return dt.date() if hasattr(dt, "date") else dt


def cleanup_duplicates(db_path="momentum.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get all habits
    cursor.execute("SELECT id, frequency FROM habits")
    habits = cursor.fetchall()
    total_deleted = 0
    for habit_id, frequency in habits:
        cursor.execute(
            "SELECT rowid, date FROM completions WHERE habit_id = ? ORDER BY date ASC",
            (habit_id,),
        )
        rows = cursor.fetchall()
        seen = set()
        for rowid, d in rows:
            try:
                dt = datetime.fromisoformat(d)
            except Exception:
                try:
                    dt = datetime.strptime(d, "%Y-%m-%d")
                except Exception:
                    continue
            if frequency == "daily":
                key = _to_date(dt)
            elif frequency == "weekly":
                date_part = _to_date(dt)
                key = date_part - timedelta(days=(date_part.weekday() + 1) % 7)
            else:
                continue
            if key in seen:
                cursor.execute("DELETE FROM completions WHERE rowid = ?", (rowid,))
                total_deleted += 1
            else:
                seen.add(key)
    conn.commit()
    conn.close()
    print(f"Deleted {total_deleted} duplicate completions.")


if __name__ == "__main__":
    cleanup_duplicates()

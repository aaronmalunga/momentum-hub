import sqlite3
from datetime import datetime

DB_PATH = "momentum.db"


def list_completions_for_habit():
    habit_name = input("Enter the habit name: ")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM habits WHERE name = ?", (habit_name,))
    row = cursor.fetchone()
    if not row:
        print(f"No habit found with name: {habit_name}")
        return
    habit_id = row[0]
    cursor.execute(
        "SELECT date FROM completions WHERE habit_id = ? ORDER BY date ASC", (habit_id,)
    )
    completions = cursor.fetchall()
    print(f"Completions for habit '{habit_name}' (ID: {habit_id}):")
    for (d,) in completions:
        try:
            dt = datetime.fromisoformat(d)
            print(f"{dt} (date part: {dt.date()})")
        except Exception:
            print(d)
    print(f"Total completions: {len(completions)}")
    conn.close()


if __name__ == "__main__":
    list_completions_for_habit()

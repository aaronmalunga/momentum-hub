import sqlite3
from datetime import datetime


def patch_missing_created_at(db_path="momentum.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM habits WHERE created_at IS NULL OR created_at = ''")
    rows = cursor.fetchall()
    for (habit_id,) in rows:
        cursor.execute(
            "SELECT MIN(date) FROM completions WHERE habit_id = ?", (habit_id,)
        )
        result = cursor.fetchone()
        earliest = result[0] if result and result[0] else datetime.now().isoformat()
        cursor.execute(
            "UPDATE habits SET created_at = ? WHERE id = ?", (earliest, habit_id)
        )
    conn.commit()
    conn.close()
    print(f"Patched {len(rows)} habits with missing created_at.")


if __name__ == "__main__":
    patch_missing_created_at()

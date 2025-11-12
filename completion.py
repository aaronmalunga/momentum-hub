import sqlite3
import csv
from pathlib import Path
from momentum_db import DB_NAME

def export_completions_to_csv(output_path: str = "completions_fixed.csv", db_name: str = DB_NAME):
    conn = sqlite3.connect(db_name)
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

    conn.close()
    print(f"Exported {len(rows)} rows to {output_path}")


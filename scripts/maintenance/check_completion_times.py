import sqlite3
from datetime import datetime

def check_completion_times(db_path='momentum.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, date FROM completions')
    rows = cursor.fetchall()
    with_time = 0
    date_only = 0
    for _, d in rows:
        try:
            dt = datetime.fromisoformat(d)
            # If the string includes time, dt will be a datetime, otherwise a date
            if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
                with_time += 1
            elif 'T' in d:
                with_time += 1  # Has time part, even if 00:00:00
            else:
                date_only += 1
        except Exception:
            date_only += 1
    print(f'Completions with time: {with_time}')
    print(f'Completions date-only: {date_only}')

if __name__ == '__main__':
    check_completion_times()

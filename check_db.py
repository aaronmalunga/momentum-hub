import sqlite3
from pathlib import Path

DB_PATH = Path('momentum.db')
print(f'\n📁 DB Path: {DB_PATH.resolve()}')
print(f'📊 DB exists: {DB_PATH.exists()}')
print(f'📦 DB size: {DB_PATH.stat().st_size} bytes\n')

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# Get habits
print('📘 HABITS:')
print('-' * 70)
cur.execute('SELECT id, name, frequency, streak, is_active FROM habits')
for row in cur.fetchall():
    print(f'  ID: {row[0]} | Name: {row[1]} | Freq: {row[2]} | Streak: {row[3]} | Active: {row[4]}')

print(f'\n✅ COMPLETIONS:')
print('-' * 70)
cur.execute('SELECT id, habit_id, date FROM completions')
for row in cur.fetchall():
    print(f'  ID: {row[0]} | Habit_ID: {row[1]} | Date: {row[2]}')

conn.close()
print('\n')

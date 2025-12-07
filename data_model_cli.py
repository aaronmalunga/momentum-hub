def print_data_model():
    print("SQLite Data Model - Habits and Event Logs\n")
    print("Table: habits")
    print(
        """
CREATE TABLE habits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  frequency TEXT NOT NULL,         -- daily, weekly, etc.
  notes TEXT,                     -- optional
  reminder_time TEXT,             -- optional
  evening_reminder_time TEXT,     -- optional
  streak INTEGER DEFAULT 0,
  created_at TEXT,                -- ISO timestamp
  last_completed TEXT,            -- ISO timestamp
  is_active INTEGER DEFAULT 1,   -- 1 = active, 0 = inactive
  reactivated_at TEXT,            -- optional; ISO timestamp
  category_id INTEGER             -- optional; foreign key to categories
);
"""
    )
    print("Table: completions")
    print(
        """
CREATE TABLE completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  habit_id INTEGER NOT NULL,      -- foreign key to habits.id
  date TEXT NOT NULL              -- timestamp when completion occurred
);
"""
    )
    print("Relationship:")
    print("  One habit can have many completions (event logs).")
    print("  completions.habit_id is a foreign key to habits.id\n")


if __name__ == "__main__":
    print_data_model()

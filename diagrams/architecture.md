# Momentum Hub Architecture

## High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Momentum Hub CLI App                         │
│                                                                       │
│  User (Terminal/Shell)                                               │
│           │                                                          │
│           ↓                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │          momentum_main.py (Entry Point)                        │ │
│  │  • Parse CLI args (--db, --help)                              │ │
│  │  • Initialize database                                         │ │
│  │  • Offer demo data on first run                               │ │
│  │  • Start interactive CLI                                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           │                                                          │
│           ↓                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │          momentum_cli.py (CLI Orchestrator)                    │ │
│  │  • Main menu loop                                              │ │
│  │  • Route user choices to CLI modules                           │ │
│  │  • Handle questionary prompts                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           │                                                          │
│  ┌────────┼────────┬─────────────┬──────────────┬──────────────┐   │
│  ↓        ↓        ↓             ↓              ↓              ↓    │
│  cli_    cli_    cli_habit_    cli_          cli_             cli_  │
│  display export  management   analysis      utils            _*    │
│                                                                      │
│           ↓ (all converge to data layer)                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │       momentum_db.py (Database Access Layer)                   │ │
│  │  • Connection pooling & caching                                │ │
│  │  • CRUD for habits, completions                                │ │
│  │  • Streak calculations, analysis queries                       │ │
│  │  • Soft delete, reactivation logic                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           │                                                          │
│           ↓                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           Data Models (ORM-like)                               │ │
│  │  • habit.py → Habit class (name, freq, streak, etc.)          │ │
│  │  • completion.py → Completion class (habit_id, date)          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           │                                                          │
│           ↓                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │         SQLite Database (momentum.db)                          │ │
│  │  ┌──────────────────┐  ┌──────────────────────┐               │ │
│  │  │ habits table     │  │ completions table    │               │ │
│  │  │ ├─ id (PK)       │  │ ├─ id (PK)           │               │ │
│  │  │ ├─ name          │  │ ├─ habit_id (FK)    │               │ │
│  │  │ ├─ frequency     │  │ ├─ date              │               │ │
│  │  │ ├─ streak        │  │ └─ (unique per day) │               │ │
│  │  │ ├─ is_active     │  │                      │               │ │
│  │  │ ├─ created_at    │  └──────────────────────┘               │ │
│  │  │ ├─ last_completed│                                         │ │
│  │  │ └─ (timestamps)  │                                         │ │
│  │  └──────────────────┘                                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Entry Point
- **momentum_main.py**
  - Accepts `--db` CLI flag or reads `MOMENTUM_DB` env var
  - Initializes the SQLite database (schema setup)
  - Prompts for demo habits on first run (via `seed_data.py`)
  - Hands off to `start_cli(db_name)` to begin interactive loop

### CLI Layer (User Interaction)
- **momentum_cli.py** — Main menu loop and routing
- **cli_habit_management.py** — Create, update, delete, reactivate habits
- **cli_analysis.py** — Analyze streaks, completion rates, trends
- **cli_export.py** — Export habits/completions to CSV
- **cli_display.py** — Formatted display of habit tables
- **cli_utils.py** — Prompt helpers, habit selection, validation

### Data Layer (Business Logic & DB Access)
- **momentum_db.py**
  - SQLite connection management (caching, pooling)
  - CRUD operations on habits and completions
  - Streak calculation logic (daily vs. weekly)
  - Soft-delete and reactivation
  - Analysis queries (longest streak, completion rate, etc.)

### Data Models
- **habit.py** — Habit class with methods for marking complete, editing, streak calculation
- **completion.py** — Completion record (date + habit_id)
- **habit_analysis.py** — Analysis computations (gaps, streaks, trends)

### Utilities & Support
- **momentum_utils.py** — Terminal I/O helpers (colors, input validation)
- **encouragements.py** — Motivational messages
- **error_manager.py** — Global error message store (database.db)
- **seed_data.py** — Production demo habits (first-run seeding)

### Maintenance & Testing
- **scripts/maintenance/backup_db.py** — Timestamped DB backups with gzip support
- **scripts/maintenance/\*.py** — One-off maintenance scripts
- **tests/** — 176 unit & integration tests (84% coverage)

## Data Flow

### Creating a Habit
```
User Input (questionary)
    ↓
cli_habit_management.py (prompt_name, frequency, notes, reminders)
    ↓
habit.py (Habit object instantiation)
    ↓
momentum_db.add_habit(habit, db_name)
    ↓
SQLite INSERT into habits table
    ↓
User sees success message
```

### Marking a Habit Complete
```
User selects habit from list
    ↓
cli_habit_management.py (confirm, set timestamp)
    ↓
habit.py (mark_completed method, streak recalc)
    ↓
momentum_db.add_completion(completion, db_name)
    ↓
SQLite INSERT into completions table
    ↓
encouragements.py (fetch congratulatory message)
    ↓
Display streak + encouragement to user
```

### Analyzing Habits
```
User chooses "Analyze"
    ↓
cli_analysis.py (show menu: by periodicity, longest streak, etc.)
    ↓
momentum_db queries (get_all_habits, get_completions_for_habit, etc.)
    ↓
habit_analysis.py (compute longest streak, completion rate, gaps)
    ↓
cli_display.py (format results as tables/grids)
    ↓
Display to user
```

### Exporting Data
```
User chooses "Export"
    ↓
cli_export.py (select habits or completions)
    ↓
momentum_db.get_all_habits / get_all_completions
    ↓
completion.py.export_to_csv (write CSV)
    ↓
File saved to CSV Export/ directory
    ↓
User sees confirmation with file path
```

## Database Schema

### habits table
```sql
CREATE TABLE habits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  frequency TEXT NOT NULL,           -- 'daily' or 'weekly'
  notes TEXT,
  reminder_time TEXT,                -- HH:MM format
  evening_reminder_time TEXT,        -- Optional second reminder
  streak INTEGER DEFAULT 0,          -- Current consecutive days/weeks
  created_at TEXT,                   -- ISO 8601 timestamp
  last_completed TEXT,               -- ISO 8601 timestamp of most recent completion
  is_active INTEGER DEFAULT 1,       -- 0 = soft-deleted, 1 = active
  reactivated_at TEXT                -- ISO 8601 timestamp if reactivated
);
```

### completions table
```sql
CREATE TABLE completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  habit_id INTEGER NOT NULL,         -- Foreign key to habits.id
  date TEXT NOT NULL,                -- ISO 8601 date (unique per day per habit)
  FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
  UNIQUE(habit_id, date)             -- Prevents duplicate completions same day
);
```

### error_manager table (in database.db)
```sql
CREATE TABLE error_messages (
  key TEXT PRIMARY KEY,
  message TEXT NOT NULL
);
```

## Deployment & Configuration

### Environment Variables
- `MOMENTUM_DB` — Path to the SQLite database (default: `momentum.db`)

### CLI Flags
- `--db <path>` — Override database file location
- `--help` — Show usage and examples

### Demo Seeding
- **First-run:** User is prompted; if yes, `seed_data.py` creates 5 sample habits (no completions)
- **Manual:** `.venv/Scripts/seed_demo_db.py` creates demo habits + completions
  - Default target: `momentum_demo.db` (safe)
  - With `--db momentum.db --overwrite`: Backs up existing DB, then seeds
  - Backup is automatic via `scripts/maintenance/backup_db.py`

### Cross-Platform Support
- Windows: PowerShell/cmd activation scripts, backslash paths handled by pathlib
- Linux/macOS: bash/zsh activation scripts, forward-slash paths
- All code uses `pathlib.Path` for platform-agnostic file handling

## Testing Strategy

### Test Organization (176 tests, 84% coverage)
- `tests/test_db.py` — Database layer (CRUD, streak calculations)
- `tests/test_habit.py` — Habit model (mark_completed, edit, streak logic)
- `tests/test_edge_cases.py` — Boundary cases (empty DB, invalid data, reactivation)
- `tests/test_cli_*.py` — CLI prompt flows, mocked questionary
- `tests/test_end_to_end.py` — Full workflows (create → complete → analyze → export)
- `tests/test_error_handling.py` — Error paths (DB failures, permission errors)

### Coverage Summary
- Core logic (habits, completions, analysis): **90%+**
- CLI UI branches: **70-75%** (lower but acceptable for CLI apps)
- Utilities: **95-100%**

## Key Design Decisions

1. **SQLite over other DB** — Single-file, no server, portable, embedded
2. **Soft delete (is_active flag)** — Allows reactivation without losing history
3. **Streak calculation at query time** — Always accurate, reflects DB state
4. **Modular CLI modules** — Easy to add features without touching core
5. **Isolated demo DB** — Safe default (`momentum_demo.db`); explicit `--overwrite` required
6. **Timestamped backups** — Automatic backup before destructive seeding

## Future Enhancement Ideas

1. **Cloud Sync** — Backup/restore to AWS S3, Google Drive
2. **Web UI** — Flask/FastAPI wrapper with browser interface
3. **Mobile App** — Python compiled to mobile (Kivy, Pydantic)
4. **Habit Templates** — Pre-defined habit sets (fitness, learning, wellness)
5. **Statistics Export** — PDF reports, charts with matplotlib
6. **CI/CD Pipeline** — GitHub Actions auto-test, Docker image
7. **Packaging** — Distribute via PyPI (`pip install momentum-hub`)
8. **Dark Mode** — Terminal theme toggle (colorama customization)

---

**Diagram Created:** November 12, 2025  
**Version:** 1.0  
**Coverage:** Full system architecture, data models, workflows, schema, testing strategy

# Momentum Hub - Design Notes

## 1. Overview
Momentum Hub is a CLI habit tracker designed to support daily and weekly habits, track completions over time, and provide analytics such as current streaks, longest streaks, and completion rates. The project emphasizes clarity, testability, and maintainable architecture suitable for an academic portfolio.

## 2. Architectural Choices
The system is structured into focused modules:
- **CLI layer** (`momentum_hub/cli_*`): Input prompts and user interaction flows.
- **Core models** (`momentum_hub/habit.py`, `goal.py`, `category.py`): Domain objects and business behavior.
- **Persistence** (`momentum_hub/momentum_db.py`): SQLite access and CRUD operations.
- **Analytics** (`momentum_hub/habit_analysis.py`): Pure functions for streaks and rates.
- **Utilities** (`momentum_hub/cli_utils.py`, `momentum_hub/momentum_utils.py`): Shared helpers and formatting.

This separation of concerns keeps logic isolated and reduces coupling, which made refactoring and test-driven changes easier after tutor feedback.

**Note:** The database layer is centralized in `momentum_hub/momentum_db.py` by design to keep persistence logic in one place, simplify testing, and avoid scattered SQL across the codebase.

**Why a split DB module was not pursued:** While splitting persistence into multiple files (e.g., `db_habits.py`, `db_goals.py`) can improve file size and reuse, it also introduces additional surface area, more import wiring, and a higher refactor risk close to submission. For this portfolio scope, a single, cohesive DB module provides clarity and keeps the persistence layer easy to audit and test.

**Why strict static typing enforcement was not added to CI:** A `mypy` configuration is included for local checks, but CI enforcement was not added to avoid failing builds due to third-party stubs or false positives under limited time. The current approach balances type clarity with practical reliability for a portfolio submission.

## 3. Paradigm Justification (OOP + FP)
The project intentionally blends object-oriented and functional programming:
- **OOP** is used for **Habits, Goals, and Categories** because they represent entities with state and behavior that evolve over time.
- **FP** is used for **analytics** because streak and completion rate calculations are clearer when expressed as pure functions over historical data.

This mix keeps domain objects intuitive while making analytics deterministic and easy to test.

## 4. Persistence and Data Model
SQLite was chosen because it is lightweight, local, and sufficient for single-user CLI workflows. It provides reliable persistence without the overhead of a server.

Key tables:
- `habits`: habit definitions and metadata
- `completions`: timestamped completion events
- `goals`: optional goal tracking per habit
- `categories`: organization and filtering

Soft deletion is used for habits so historical analytics remain valid while allowing users to "remove" habits from active views.

## 5. Streak Logic (Daily vs. Weekly)
Streak calculation is the most subtle area:
- **Daily habits**: streak increments only when consecutive days are completed; a missed day resets the streak.
- **Weekly habits**: streak increments only when a full weekly period is completed; multiple completions in the same week do not increase the streak.

Weekly streaks use **Sunday-start weeks** to align with completion rules. This decision prevents inflated streaks and matches the rubric's periodicity requirement.

## 6. Demo Mode Isolation
Demo mode uses a **separate database** (`momentum_demo.db`) to avoid mixing sample data with user data. This ensures:
- New users start with an empty primary DB (`momentum.db`).
- Reviewers can explore analytics immediately without affecting real data.
- Demo data can be reseeded safely without risking production records.

## 7. Testing Strategy
Testing uses `pytest` with a mix of unit and integration coverage:
- **Unit tests** validate pure analytics functions and core model behavior.
- **Integration tests** validate persistence, CLI workflows, and database integrity.
- **Deterministic fixtures** provide a fixed 4-week dataset for reproducible analytics tests.

This strategy ensures streak and completion-rate logic remains stable across refactors.

## 8. Tradeoffs and Limitations
- The CLI interface maximizes simplicity but lacks a GUI.
- SQLite fits single-user workflows but does not support multi-user concurrency.
- Advanced analytics (predictive insights, gamification) were intentionally out of scope.

Despite these limits, the current design offers a clean foundation for extensions.

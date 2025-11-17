# Module–Paradigm–Rationale Mapping

| Module (file) | Paradigm | Rationale |
|---|---|---|
| `habit.py` | **Object-Oriented (OO)** | Domain entity: holds state and methods for habit lifecycle. |
| `momentum_db.py` | **Adapter / Imperative** | Isolates I/O and side-effects; keeps core logic testable. |
| `habit_analysis.py` | **Functional / Procedural** | Pure analytics functions for metrics and streaks; deterministic. |
| `momentum_cli.py` | **Controller / Imperative** | Orchestrates commands and parses user input. |

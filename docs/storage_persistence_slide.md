# Storage & Persistence Design

- SQLite database (`momentum.db`) is the primary persistent storage for habit tracking.
- Storage layer serializes/deserializes Habit, Completion, Category, and Goal data.
- Ensures data persists reliably between sessions with schema validation and migrations.
- Supports soft deletes via `is_active` flags to preserve historical data across Habits, Categories, and Goals.
- Designed with clean architecture, enabling future extension without changing business logic.
- Concurrency control for completions uses thread locking to prevent duplicate entries in concurrent scenarios.
- Streak calculation algorithms compute continuous completions for daily and weekly frequencies, considering reactivation times.
- Schema migrations automatically add new columns like `reactivated_at` and `category_id` if missing, maintaining backward compatibility.
- Export functionality allows data to be exported as CSV for sharing or backups.
- JSON is used conceptually for CLI simplicity but SQLite handles durable persistence.
- The following diagram illustrates the data flow involving user input, business logic, and data storage components.

![Data Flow Diagram](../diagrams/uml/data_flow_diagram.png)

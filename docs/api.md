
# Momentum Hub API Documentation

This document provides comprehensive API documentation for the Momentum Hub habit tracking application.

## Table of Contents

- [Core Classes](#core-classes)
  - [Habit](#habit)
  - [Goal](#goal)
  - [Category](#category)
  - [Completion](#completion)
- [Database Operations](#database-operations)
- [Analysis Functions](#analysis-functions)
- [CLI Modules](#cli-modules)

## Core Classes

### Habit

The main class representing a habit in the system.

#### Attributes

- `id` (int): Unique identifier
- `name` (str): Habit name
- `frequency` (str): "daily" or "weekly"
- `notes` (str): Optional notes
- `reminder_time` (str): Morning reminder time (HH:MM)
- `evening_reminder_time` (str): Evening reminder time (HH:MM)
- `streak` (int): Current streak count
- `created_at` (datetime): Creation timestamp
- `last_completed` (datetime): Last completion timestamp
- `is_active` (bool): Whether habit is active
- `category_id` (int): Associated category ID

#### Methods

##### `mark_completed(completion_time=None)`
Mark the habit as completed at the specified time.

**Parameters:**
- `completion_time` (datetime, optional): Time of completion. Defaults to current time.

**Returns:** None

**Example:**
```python
habit = Habit(name="Exercise", frequency="daily")
habit.mark_completed()  # Mark as completed now
```

##### `calculate_longest_streak(db_name)`
Calculate the longest streak for this habit.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** int - Longest streak length

##### `calculate_completion_rate(db_name, days=30)`
Calculate completion rate over the specified period.

**Parameters:**
- `db_name` (str): Database file path
- `days` (int): Number of days to analyze (default: 30)

**Returns:** float - Completion rate (0.0 to 1.0)

### Goal

Represents a goal set for a specific habit.

#### Attributes

- `id` (int): Unique identifier
- `habit_id` (int): Associated habit ID
- `target_period_days` (int): Goal period in days
- `target_completions` (int): Target number of completions
- `start_date` (datetime): Goal start date
- `end_date` (datetime): Goal end date
- `is_active` (bool): Whether goal is active

#### Methods

##### `calculate_progress(db_name)`
Calculate current progress toward the goal.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** dict with keys:
- `count` (int): Current completions
- `total` (int): Target completions
- `percent` (float): Progress percentage

**Example:**
```python
progress = goal.calculate_progress("habits.db")
print(f"Progress: {progress['count']}/{progress['total']} ({progress['percent']}%)")
```

##### `is_expired()`
Check if the goal has expired.

**Returns:** bool - True if goal has ended

### Category

Represents a category for organizing habits.

#### Attributes

- `id` (int): Unique identifier
- `name` (str): Category name
- `description` (str): Category description
- `color` (str): Hex color code (e.g., "#FF5733")
- `is_active` (bool): Whether category is active

#### Methods

##### `get_habits(db_name)`
Get all habits in this category.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** list[Habit] - List of habits in the category

## Database Operations

### Habit Operations

#### `add_habit(habit, db_name)`
Add a new habit to the database.

**Parameters:**
- `habit` (Habit): Habit object to add
- `db_name` (str): Database file path

**Returns:** int - New habit ID

#### `get_habit(habit_id, db_name)`
Retrieve a habit by ID.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path

**Returns:** Habit or None

#### `get_all_habits(active_only=True, db_name="")`
Get all habits from the database.

**Parameters:**
- `active_only` (bool): Include only active habits (default: True)
- `db_name` (str): Database file path

**Returns:** list[Habit]

#### `update_habit(habit, db_name)`
Update an existing habit.

**Parameters:**
- `habit` (Habit): Updated habit object
- `db_name` (str): Database file path

**Returns:** None

#### `delete_habit(habit_id, db_name)`
Soft delete a habit.

**Parameters:**
- `habit_id` (int): Habit ID to delete
- `db_name` (str): Database file path

**Returns:** None

### Completion Operations

#### `add_completion(habit_id, completion_time, db_name)`
Add a completion record.

**Parameters:**
- `habit_id` (int): Habit ID
- `completion_time` (datetime): Completion timestamp
- `db_name` (str): Database file path

**Returns:** int - Completion ID

#### `get_completions(habit_id, db_name)`
Get all completions for a habit.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path

**Returns:** list[datetime] - List of completion timestamps

### Goal Operations

#### `add_goal(goal, db_name)`
Add a new goal.

**Parameters:**
- `goal` (Goal): Goal object
- `db_name` (str): Database file path

**Returns:** int - Goal ID

#### `get_all_goals(db_name)`
Get all goals.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** list[Goal]

### Category Operations

#### `add_category(category, db_name)`
Add a new category.

**Parameters:**
- `category` (Category): Category object
- `db_name` (str): Database file path

**Returns:** int - Category ID

#### `get_all_categories(db_name)`
Get all categories.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** list[Category]

## Analysis Functions

### `calculate_longest_streak_for_habit(habit_id, db_name)`
Calculate longest streak for a specific habit.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path

**Returns:** int - Longest streak length

### `calculate_completion_rate_for_habit(habit_id, db_name, days=30)`
Calculate completion rate for a habit over a period.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path
- `days` (int): Analysis period in days (default: 30)

**Returns:** float - Completion rate (0.0 to 1.0)

### `calculate_overall_longest_streak(db_name)`
Find the habit with the longest current streak.

**Parameters:**
- `db_name` (str): Database file path

**Returns:** tuple - (habit_name, streak_length)

### `get_completion_history(habit_id, db_name)`
Get completion history for analysis.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path

**Returns:** list[datetime] - Sorted completion timestamps

### `calculate_goal_progress(habit_id, db_name)`
Calculate progress toward goals for a habit.

**Parameters:**
- `habit_id` (int): Habit ID
- `db_name` (str): Database file path

**Returns:** dict - Progress information

## CLI Modules

### Main CLI Entry Points

#### `start_cli(db_name)`
Initialize and start the main CLI interface.

**Parameters:**
- `db_name` (str): Database file path

#### `main_menu(db_name)`
Display and handle the main menu navigation.

**Parameters:**
- `db_name` (str): Database file path

### Habit Management CLI

#### `create_new_habit(db_name)`
Interactive habit creation.

#### `mark_habit_completed(db_name)`
Interactive habit completion marking.

#### `update_habit(db_name)`
Interactive habit updating.

#### `delete_habit(db_name)`
Interactive habit deletion.

### Analysis CLI

#### `analyze_habits(db_name)`
Main analysis menu.

#### `analyze_list_all_habits(db_name)`
List all habits with statistics.

#### `analyze_longest_streak_all(db_name)`
Show longest streaks for all habits.

#### `analyze_completion_history(db_name)`
Show completion history for a habit.

### Export CLI

#### `export_all_habits_to_csv(db_name)`
Export all habits to CSV.

#### `export_all_completions_to_csv(db_name)`
Export all completions to CSV.

#### `export_habit_completions_to_csv(db_name)`
Export completions for a specific habit.

## Error Handling

The application uses a centralized error management system:

### ErrorManager
Handles error display and user feedback.

#### `display_error(key, **kwargs)`
Display a formatted error message.

**Parameters:**
- `key` (str): Error message key
- `**kwargs`: Formatting parameters

## Configuration

### Environment Variables

- `MOMENTUM_DEMO_DB`: Override demo database filename (default: "momentum_demo.db")

### Database Schema

The application uses SQLite with the following main tables:

- `habits`: Habit definitions
- `completions`: Completion records
- `goals`: Goal definitions
- `categories`: Category definitions
- `habit_categories`: Many-to-many relationship between habits and categories

## Examples

### Basic Usage

```python
import momentum_db as db
from habit import Habit

# Initialize database
db.init_db("my_habits.db")

# Create and add a habit
habit = Habit(name="Read", frequency="daily", notes="Read for 30 minutes")
habit_id = db.add_habit(habit, "my_habits.db")

# Mark as completed
habit.mark_completed()
db.update_habit(habit, "my_habits.db")

# Get statistics
streak = habit.calculate_longest_streak("my_habits.db")
rate = habit.calculate_completion_rate("my_habits.db")
```

### Advanced Analytics

```python
import habit_analysis as analysis

# Get overall statistics
habit_name, longest_streak = analysis.calculate_overall_longest_streak("my_habits.db")

# Analyze specific habit
history = analysis.get_completion_history(habit_id, "my_habits.db")
progress = analysis.calculate_goal_progress(habit_id, "my_habits.db")
```

This API documentation covers the core functionality. For more detailed examples, see the main README.md file.

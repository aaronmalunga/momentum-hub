
"""
Production seed data module for Momentum habit tracker.
Provides optional demo habits for new users.

This module is separate from tests/test_data.py which is used exclusively for testing.
"""

import datetime
import momentum_db as db
from habit import Habit


def create_default_categories(db_name: str) -> None:
    """
    Creates default categories for new users.

    These provide basic organization structure without demo habits.
    Users can assign their own habits to these categories.

    Args:
        db_name: The database file name to populate
    """
    default_categories = [
        {
            "name": "Health & Fitness",
            "description": "Habits related to physical health and exercise",
            "color": "#FF6B6B"
        },
        {
            "name": "Personal Development",
            "description": "Habits for learning and self-improvement",
            "color": "#4ECDC4"
        },
        {
            "name": "Productivity",
            "description": "Habits to improve efficiency and organization",
            "color": "#45B7D1"
        },
        {
            "name": "Mindfulness & Wellness",
            "description": "Habits for mental health and relaxation",
            "color": "#96CEB4"
        },
        {
            "name": "Social & Relationships",
            "description": "Habits for building and maintaining relationships",
            "color": "#FFEAA7"
        },
        {
            "name": "Finance & Money",
            "description": "Habits for financial planning and management",
            "color": "#DDA0DD"
        },
        {
            "name": "Creativity & Hobbies",
            "description": "Habits for creative expression and leisure activities",
            "color": "#98D8C8"
        },
        {
            "name": "Home & Environment",
            "description": "Habits for maintaining home and environmental care",
            "color": "#F7DC6F"
        }
    ]

    from category import Category
    for cat_data in default_categories:
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"],
            color=cat_data["color"],
            created_at=datetime.datetime.now(),
            is_active=True
        )
        db.add_category(category, db_name)


def create_demo_habits(db_name: str) -> None:
    """
    Creates realistic demo habits for new users.

    These habits serve as examples to help users understand the app.
    No synthetic completion data is created - users build their own history.

    Args:
        db_name: The database file name to populate
    """
    # First create demo categories (reuse default ones if they exist)
    demo_categories = [
        {
            "name": "Health & Fitness",
            "description": "Habits related to physical health and exercise",
            "color": "#FF6B6B"
        },
        {
            "name": "Personal Development",
            "description": "Habits for learning and self-improvement",
            "color": "#4ECDC4"
        },
        {
            "name": "Productivity",
            "description": "Habits to improve efficiency and organization",
            "color": "#45B7D1"
        }
    ]

    from category import Category
    category_ids = {}
    for cat_data in demo_categories:
        # Check if category already exists
        existing = db.get_all_categories(active_only=True, db_name=db_name)
        existing_names = [c.name for c in existing]
        if cat_data["name"] not in existing_names:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                color=cat_data["color"],
                created_at=datetime.datetime.now(),
                is_active=True
            )
            cat_id = db.add_category(category, db_name)
        else:
            cat_id = next(c.id for c in existing if c.name == cat_data["name"])
        category_ids[cat_data["name"]] = cat_id

    # Demo habits with category assignments (using test data habits)
    demo_habits = [
        {
            "name": "Change beddings",
            "frequency": "weekly",
            "notes": "Wash and change beddings",
            "reminder_time": "09:00",
            "evening_reminder_time": None,
            "category": "Health & Fitness"
        },
        {
            "name": "Code",
            "frequency": "daily",
            "notes": "Code for at least 1 hour",
            "reminder_time": "10:00",
            "evening_reminder_time": None,
            "category": "Personal Development"
        },
        {
            "name": "Study",
            "frequency": "daily",
            "notes": "Review course materials",
            "reminder_time": "11:00",
            "evening_reminder_time": None,
            "category": "Personal Development"
        },
        {
            "name": "Meditate",
            "frequency": "daily",
            "notes": "Meditate for at least 10 minutes",
            "reminder_time": "07:00",
            "evening_reminder_time": None,
            "category": "Health & Fitness"
        },
        {
            "name": "Blog",
            "frequency": "weekly",
            "notes": "Write a Data Science blog post",
            "reminder_time": "11:00",
            "evening_reminder_time": None,
            "category": "Productivity"
        }
    ]

    created_count = 0
    for habit_data in demo_habits:
        habit = Habit(
            name=habit_data["name"],
            frequency=habit_data["frequency"],
            notes=habit_data["notes"],
            reminder_time=habit_data.get("reminder_time"),
            evening_reminder_time=habit_data.get("evening_reminder_time"),
            created_at=datetime.datetime.now(),  # Current time, not backdated
            last_completed=None,  # No completions yet
            streak=0,
            is_active=True
        )
        habit_id = db.add_habit(habit, db_name)

        # Update habit with category_id
        habit.id = habit_id
        habit.category_id = category_ids.get(habit_data["category"])
        db.update_habit(habit, db_name)

        created_count += 1

    # Create demo goals for some habits
    demo_goals = [
        {
            "habit_name": "Code",
            "target_period_days": 30,
            "target_completions": 30,  # Daily goal for 30 days
            "start_date": datetime.datetime.now(),
            "end_date": datetime.datetime.now() + datetime.timedelta(days=30)
        },
        {
            "habit_name": "Study",
            "target_period_days": 28,
            "target_completions": 25,  # 25 out of 28 days
            "start_date": datetime.datetime.now(),
            "end_date": datetime.datetime.now() + datetime.timedelta(days=28)
        },
        {
            "habit_name": "Blog",
            "target_period_days": 12,  # 12 weeks
            "target_completions": 12,  # Weekly goal
            "start_date": datetime.datetime.now(),
            "end_date": datetime.datetime.now() + datetime.timedelta(weeks=12)
        }
    ]

    from goal import Goal
    for goal_data in demo_goals:
        # Find habit by name
        habit = next((h for h in db.get_all_habits(db_name=db_name) if h.name == goal_data["habit_name"]), None)
        if habit:
            goal = Goal(
                habit_id=habit.id,
                target_period_days=goal_data["target_period_days"],
                target_completions=goal_data["target_completions"],
                start_date=goal_data["start_date"],
                end_date=goal_data["end_date"],
                is_active=True,
                created_at=datetime.datetime.now()
            )
            db.add_goal(goal, db_name)

    print(f"\n✓ Created {len(demo_categories)} demo categories, {created_count} demo habits, and {len(demo_goals)} demo goals!")
    print("You can modify, delete, or add your own habits anytime.\n")


def prompt_for_demo_habits() -> bool:
    """
    Prompts the user to choose whether to start with demo habits.
    
    Returns:
        bool: True if user wants demo habits, False otherwise
    """
    print("\n" + "="*60)
    print("Welcome to Momentum - Your Personal Habit Tracker!")
    print("="*60)
    print("\nIt looks like this is your first time using Momentum.")
    print("\nWould you like to start with some demo habits?")
    print("  • Demo habits provide examples to help you get started")
    print("  • You can modify or delete them anytime")
    print("  • Or start with a clean slate and create your own\n")
    
    while True:
        choice = input("Start with demo habits? (yes/no): ").strip().lower()
        if choice in ['yes', 'y']:
            return True
        elif choice in ['no', 'n']:
            print("\n✓ Starting with an empty tracker. Create your first habit from the main menu!\n")
            return False
        else:
            print("Please enter 'yes' or 'no'")


if __name__ == "__main__":
    # For testing this module independently
    import os
    test_db = "test_seed.db"
    
    # Clean up if exists
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Initialize and populate
    db.init_db(test_db)
    create_demo_habits(test_db)
    
    # Verify
    habits = db.get_all_habits(db_name=test_db)
    print(f"\nVerification: Created {len(habits)} habits in {test_db}")
    for h in habits:
        print(f"  - {h.name} ({h.frequency})")
    
    # Cleanup - close connections first
    db.close_all_connections()
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"\nTest database {test_db} removed.")

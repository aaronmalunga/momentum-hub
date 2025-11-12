"""
Production seed data module for Momentum habit tracker.
Provides optional demo habits for new users.

This module is separate from tests/test_data.py which is used exclusively for testing.
"""

import datetime
import momentum_db as db
from habit import Habit


def create_demo_habits(db_name: str) -> None:
    """
    Creates realistic demo habits for new users.
    
    These habits serve as examples to help users understand the app.
    No synthetic completion data is created - users build their own history.
    
    Args:
        db_name: The database file name to populate
    """
    demo_habits = [
        {
            "name": "Morning Exercise",
            "frequency": "daily",
            "notes": "Start your day with 20 minutes of exercise",
            "reminder_time": "07:00",
            "evening_reminder_time": None
        },
        {
            "name": "Read",
            "frequency": "daily",
            "notes": "Read for at least 15 minutes",
            "reminder_time": "20:00",
            "evening_reminder_time": None
        },
        {
            "name": "Meditate",
            "frequency": "daily",
            "notes": "Practice mindfulness for 10 minutes",
            "reminder_time": "08:00",
            "evening_reminder_time": None
        },
        {
            "name": "Weekly Review",
            "frequency": "weekly",
            "notes": "Review your goals and progress",
            "reminder_time": "09:00",
            "evening_reminder_time": None
        },
        {
            "name": "Meal Prep",
            "frequency": "weekly",
            "notes": "Prepare healthy meals for the week",
            "reminder_time": "10:00",
            "evening_reminder_time": None
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
        db.add_habit(habit, db_name)
        created_count += 1
    
    print(f"\n✓ Created {created_count} demo habits!")
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

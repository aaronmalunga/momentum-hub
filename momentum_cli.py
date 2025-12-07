import datetime
import os
import shutil
import sys

import questionary
from colorama import Fore, Style
from pyfiglet import Figlet
from tabulate import tabulate

import encouragements
import habit_analysis as analysis
import momentum_db as db
from cli_analysis import (
    analyze_best_worst_habit,
    analyze_by_periodicity,
    analyze_completion_history,
    analyze_goal_progress,
    analyze_habits,
    analyze_list_all_habits,
    analyze_longest_streak_all,
    analyze_longest_streak_one,
    analyze_streak_history_grid,
)
from cli_category_management import manage_categories

# Import CLI functions from modularized files
from cli_display import startup_message, view_habits
from cli_export import analyze_export_csv, export_all_habits_to_csv
from cli_goal_management import manage_goals
from cli_habit_management import (
    create_new_habit,
    delete_habit,
    mark_habit_completed,
    reactivate_habit,
    update_habit,
)
from cli_utils import _handle_habit_selection, _to_date, _validate_time_format
from error_manager import error_manager
from habit import Habit
from momentum_utils import press_enter_to_continue, show_colored_message


def main_menu(db_name: str):
    """Displays the main menu and handles user input."""
    show_colored_message(
        "\nWelcome to Momentum Hub! Choose an action to begin.",
        color=Fore.YELLOW,
        style=Style.BRIGHT,
    )

    choice = questionary.select(
        "What would you like to do? Let's keep the momentum going!",
        choices=[
            "Create a new habit",
            "Mark a habit as completed",
            "View habits",
            "Update a habit",
            "Analyze habits",
            "Manage Goals",
            "Manage Categories",
            "Delete a habit",
            "Reactivate a habit",
            "Exit",
        ],
    ).ask()

    menu_actions = {
        "Create a new habit": lambda: create_new_habit(db_name),
        "Mark a habit as completed": lambda: mark_habit_completed(db_name),
        "View habits": lambda: view_habits(db_name),
        "Update a habit": lambda: update_habit(db_name),
        "Analyze habits": lambda: analyze_habits(db_name),
        "Manage Goals": lambda: manage_goals(db_name),
        "Manage Categories": lambda: manage_categories(db_name),
        "Delete a habit": lambda: delete_habit(db_name),
        "Reactivate a habit": lambda: reactivate_habit(db_name),
        "Exit": lambda: sys.exit(),
    }

    if choice in menu_actions:
        if choice == "Exit":
            show_colored_message(
                "\nThank you for using Momentum Hub! Keep up the great work!",
                color=Fore.GREEN,
            )
        menu_actions[choice]()


def start_cli(db_name: str):
    """Starts the Momentum Hub CLI application."""
    # Initialize the database
    db.init_db(db_name)

    startup_message()
    while True:
        try:
            main_menu(db_name)
        except SystemExit:
            break
        except Exception as e:
            show_colored_message(f"An error occurred: {str(e)}", color=Fore.RED)
            press_enter_to_continue()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="momentum_cli")
    parser.add_argument(
        "--db", default="momentum.db", help="SQLite DB filename (default: momentum.db)"
    )
    args = parser.parse_args()

    start_cli(args.db)

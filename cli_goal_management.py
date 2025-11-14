import questionary
import datetime
from colorama import Fore, Style
from tabulate import tabulate
from momentum_utils import show_colored_message, press_enter_to_continue
from error_manager import error_manager
from goal import Goal
import momentum_db as db
from cli_utils import _handle_habit_selection

def manage_goals(db_name: str):
    """Handles the goal management menu."""
    show_colored_message("\n--- Manage Goals ---", color=Fore.YELLOW, style=Style.BRIGHT)
    choice = questionary.select(
        "What would you like to do with goals?",
        choices=[
            "Create a new goal",
            "View all goals",
            "Update a goal",
            "Delete a goal",
            "Back to Main Menu"
        ]
    ).ask()

    goal_actions = {
        "Create a new goal": lambda: create_goal(db_name),
        "View all goals": lambda: view_goals(db_name),
        "Update a goal": lambda: update_goal(db_name),
        "Delete a goal": lambda: delete_goal(db_name),
        "Back to Main Menu": lambda: None
    }

    if choice in goal_actions:
        goal_actions[choice]()

def create_goal(db_name: str):
    """Handles creating a new goal."""
    show_colored_message("\n--- Create New Goal ---", color=Fore.YELLOW, style=Style.BRIGHT)

    # Select habit
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("No active habits found. Create a habit first!", color=Fore.RED)
        press_enter_to_continue()
        return

    selected_habit = _handle_habit_selection(habits, "Select a habit for the goal:", "No active habits found.")
    if not selected_habit:
        return

    # Get goal parameters
    target_period_days = questionary.text(
        "Enter target period in days (default: 28):",
        default="28",
        validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()
    if target_period_days is None:
        show_colored_message("Goal creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    target_period_days = int(target_period_days)

    target_completions = questionary.text(
        "Enter specific target completions (optional, leave blank for auto-calculation):"
    ).ask()
    if target_completions and not target_completions.isdigit():
        show_colored_message("Invalid target completions. Must be a number.", color=Fore.RED)
        press_enter_to_continue()
        return
    target_completions = int(target_completions) if target_completions else None

    start_date_str = questionary.text(
        "Enter start date (YYYY-MM-DD, optional, leave blank for habit creation):"
    ).ask()
    start_date = None
    if start_date_str:
        try:
            start_date = datetime.datetime.fromisoformat(start_date_str)
        except ValueError:
            show_colored_message("Invalid date format. Use YYYY-MM-DD.", color=Fore.RED)
            press_enter_to_continue()
            return

    end_date_str = questionary.text(
        "Enter end date (YYYY-MM-DD, optional):"
    ).ask()
    end_date = None
    if end_date_str:
        try:
            end_date = datetime.datetime.fromisoformat(end_date_str)
        except ValueError:
            show_colored_message("Invalid date format. Use YYYY-MM-DD.", color=Fore.RED)
            press_enter_to_continue()
            return

    # Create goal
    goal = Goal(
        habit_id=selected_habit.id,
        target_period_days=target_period_days,
        target_completions=target_completions,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )

    goal_id = db.add_goal(goal, db_name)
    show_colored_message(
        f"Goal created successfully for '{selected_habit.name}' with ID: {goal_id}",
        color=Fore.GREEN,
        style=Style.BRIGHT
    )
    press_enter_to_continue()

def view_goals(db_name: str):
    """Handles viewing all goals."""
    show_colored_message("\n--- All Goals ---", color=Fore.YELLOW, style=Style.BRIGHT)

    goals = db.get_all_goals(active_only=True, db_name=db_name)
    if not goals:
        show_colored_message("No active goals found.", color=Fore.RED)
        press_enter_to_continue()
        return

    table = []
    for goal in goals:
        habit = db.get_habit(goal.habit_id, db_name)
        habit_name = habit.name if habit else "Unknown Habit"
        progress = goal.calculate_progress(db_name)
        progress_str = f"{progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
        status = "Achieved" if progress['achieved'] else "In Progress"
        status_col = f"{Fore.GREEN}{status}{Style.RESET_ALL}" if progress['achieved'] else f"{Fore.YELLOW}{status}{Style.RESET_ALL}"

        table.append([
            goal.id,
            habit_name,
            goal.target_period_days,
            goal.target_completions or "Auto",
            progress_str,
            status_col
        ])

    headers = [
        f"{Fore.CYAN}ID{Style.RESET_ALL}",
        f"{Fore.CYAN}Habit{Style.RESET_ALL}",
        f"{Fore.CYAN}Period (days){Style.RESET_ALL}",
        f"{Fore.CYAN}Target{Style.RESET_ALL}",
        f"{Fore.CYAN}Progress{Style.RESET_ALL}",
        f"{Fore.CYAN}Status{Style.RESET_ALL}"
    ]
    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def update_goal(db_name: str):
    """Handles updating an existing goal."""
    show_colored_message("\n--- Update Goal ---", color=Fore.YELLOW, style=Style.BRIGHT)

    goals = db.get_all_goals(active_only=True, db_name=db_name)
    if not goals:
        show_colored_message("No active goals found to update.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Create choices for goal selection
    choices = []
    for goal in goals:
        habit = db.get_habit(goal.habit_id, db_name)
        habit_name = habit.name if habit else "Unknown Habit"
        progress = goal.calculate_progress(db_name)
        choices.append(f"{goal.id}. {habit_name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)")
    choices.append("Cancel")

    answer = questionary.select("Select a goal to update:", choices=choices).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    try:
        goal_id = int(answer.split(".")[0])
        goal = db.get_goal(goal_id, db_name)
        if not goal:
            show_colored_message("Goal not found.", color=Fore.RED)
            press_enter_to_continue()
            return
    except ValueError:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Update fields
    target_period_days = questionary.text(
        f"Enter new target period in days (current: {goal.target_period_days}):",
        default=str(goal.target_period_days),
        validate=lambda x: x.isdigit() and int(x) > 0
    ).ask()
    if target_period_days is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    goal.target_period_days = int(target_period_days)

    target_completions = questionary.text(
        f"Enter new target completions (current: {goal.target_completions or 'Auto'}, leave blank for auto):"
    ).ask()
    if target_completions and not target_completions.isdigit():
        show_colored_message("Invalid target completions. Must be a number.", color=Fore.RED)
        press_enter_to_continue()
        return
    goal.target_completions = int(target_completions) if target_completions else None

    start_date_str = questionary.text(
        f"Enter new start date (YYYY-MM-DD, current: {goal.start_date.isoformat() if goal.start_date else 'None'}):"
    ).ask()
    if start_date_str:
        try:
            goal.start_date = datetime.datetime.fromisoformat(start_date_str)
        except ValueError:
            show_colored_message("Invalid date format. Use YYYY-MM-DD.", color=Fore.RED)
            press_enter_to_continue()
            return
    else:
        goal.start_date = None

    end_date_str = questionary.text(
        f"Enter new end date (YYYY-MM-DD, current: {goal.end_date.isoformat() if goal.end_date else 'None'}):"
    ).ask()
    if end_date_str:
        try:
            goal.end_date = datetime.datetime.fromisoformat(end_date_str)
        except ValueError:
            show_colored_message("Invalid date format. Use YYYY-MM-DD.", color=Fore.RED)
            press_enter_to_continue()
            return
    else:
        goal.end_date = None

    db.update_goal(goal, db_name)
    show_colored_message(f"Goal ID {goal.id} updated successfully!", color=Fore.GREEN, style=Style.BRIGHT)
    press_enter_to_continue()

def delete_goal(db_name: str):
    """Handles deleting a goal."""
    show_colored_message("\n--- Delete Goal ---", color=Fore.YELLOW, style=Style.BRIGHT)

    goals = db.get_all_goals(active_only=True, db_name=db_name)
    if not goals:
        show_colored_message("No active goals found to delete.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Create choices for goal selection
    choices = []
    for goal in goals:
        habit = db.get_habit(goal.habit_id, db_name)
        habit_name = habit.name if habit else "Unknown Habit"
        progress = goal.calculate_progress(db_name)
        choices.append(f"{goal.id}. {habit_name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)")
    choices.append("Cancel")

    answer = questionary.select("Select a goal to delete:", choices=choices).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Deletion cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    try:
        goal_id = int(answer.split(".")[0])
        goal = db.get_goal(goal_id, db_name)
        if not goal:
            show_colored_message("Goal not found.", color=Fore.RED)
            press_enter_to_continue()
            return
    except ValueError:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return

    confirm = questionary.confirm(f"Are you sure you want to delete this goal?").ask()
    if not confirm:
        show_colored_message("Deletion cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    db.delete_goal(goal_id, db_name)
    show_colored_message("Goal deleted successfully!", color=Fore.GREEN)
    press_enter_to_continue()

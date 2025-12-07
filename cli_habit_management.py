import datetime

import questionary
from colorama import Fore, Style

import encouragements
import momentum_db as db
from cli_utils import _handle_habit_selection, _validate_time_format
from error_manager import error_manager
from habit import Habit
from momentum_utils import press_enter_to_continue, show_colored_message


def create_new_habit(db_name: str):
    """Handles creating a new habit and saving it to the database."""
    show_colored_message(
        "\n--- Create New Habit ---", color=Fore.YELLOW, style=Style.BRIGHT
    )
    while True:
        habit_name = questionary.text(
            "Enter habit name (or type 'cancel' to go back):"
        ).ask()
        if habit_name is None or habit_name.strip().lower() == "cancel":
            show_colored_message("Habit creation cancelled.", color=Fore.YELLOW)
            press_enter_to_continue()
            return
        if not habit_name.strip():
            show_colored_message("Habit name cannot be empty.", color=Fore.RED)
            continue
        break
    frequency = questionary.select(
        f"How often should '{habit_name}' be done?", choices=["daily", "weekly"]
    ).ask()
    if frequency is None:
        show_colored_message("Habit creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    notes = questionary.text(f"Enter any notes for '{habit_name}' (optional):").ask()
    if notes is None:
        show_colored_message("Habit creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    reminder_time = questionary.text(
        f"Set a morning reminder time for '{habit_name}' (HH:MM, 24-hour format):",
        validate=_validate_time_format,
    ).ask()
    if reminder_time is None:
        show_colored_message("Habit creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    evening_reminder_time = questionary.text(
        f"Set an evening reminder time for '{habit_name}' (HH:MM, 24-hour format):",
        validate=_validate_time_format,
    ).ask()
    if evening_reminder_time is None:
        show_colored_message("Habit creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    # Select category (optional)
    categories = db.get_all_categories(active_only=True, db_name=db_name)
    category_id = None
    if categories:
        category_choices = ["No category"] + [
            f"{cat.id}. {cat.name}" for cat in categories
        ]
        category_choice = questionary.select(
            "Select a category for this habit (optional):", choices=category_choices
        ).ask()
        if category_choice and category_choice != "No category":
            try:
                category_id = int(category_choice.split(".")[0])
            except ValueError:
                pass

    new_habit = Habit(
        name=habit_name,
        frequency=frequency,
        notes=notes,
        reminder_time=reminder_time,
        evening_reminder_time=evening_reminder_time,
        created_at=datetime.datetime.now(),
        is_active=True,
    )
    habit_id = db.add_habit(new_habit, db_name)

    # Update habit with category if selected
    if category_id:
        new_habit.id = habit_id
        new_habit.category_id = category_id
        db.update_habit(new_habit, db_name)

    category_msg = (
        f" in category '{db.get_category(category_id, db_name).name}'"
        if category_id
        else ""
    )
    show_colored_message(
        f"'{habit_name}' ({frequency}) has been created successfully with ID: {habit_id}{category_msg}",
        color=Fore.GREEN,
        style=Style.BRIGHT,
    )
    press_enter_to_continue()


def mark_habit_completed(db_name: str):
    """Handles marking a habit as completed."""
    show_colored_message(
        "\n--- Mark Habit as Completed ---", color=Fore.YELLOW, style=Style.BRIGHT
    )
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    selected_habit = _handle_habit_selection(
        habits,
        "Select a habit to mark as completed:",
        "No active habits found. Let's create one!",
    )
    if not selected_habit:
        return
    habit = selected_habit
    completion_time = datetime.datetime.now()
    try:
        habit.mark_completed(completion_time)
        db.add_completion(habit.id, completion_time, db_name)
        db.update_habit(habit, db_name)
        db.update_streak(habit.id, db_name)
        updated_habit = db.get_habit(habit.id, db_name)
        show_colored_message(
            f"'{habit.name}' marked as completed! Current streak: {updated_habit.streak}",
            color=Fore.GREEN,
            style=Style.BRIGHT,
        )
    except ValueError as e:
        show_colored_message(
            f"Cannot mark '{habit.name}' as completed: {str(e)}",
            color=Fore.RED,
            style=Style.BRIGHT,
        )
        press_enter_to_continue()
        return
    show_colored_message(
        encouragements.get_completion_encouragement(),
        color=Fore.CYAN,
        style=Style.BRIGHT,
    )
    if habit.frequency == "daily":
        if habit.streak in [7, 30, 100]:
            show_colored_message(
                encouragements.get_streak_encouragement(habit.streak, is_weekly=False),
                color=Fore.MAGENTA,
                style=Style.BRIGHT,
            )
    else:  # weekly habit
        if habit.streak in [4, 12, 52]:
            show_colored_message(
                encouragements.get_streak_encouragement(habit.streak, is_weekly=True),
                color=Fore.MAGENTA,
                style=Style.BRIGHT,
            )
    press_enter_to_continue()


def delete_habit(db_name: str):
    """Handles deleting (deactivating) a habit from the database."""
    show_colored_message(
        "\n--- Delete Habit ---", color=Fore.YELLOW, style=Style.BRIGHT
    )
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("No active habits found to delete.", color=Fore.RED)
        press_enter_to_continue()
        return
    # Use interactive menu for habit selection, with Cancel option
    habit_to_delete = _handle_habit_selection(
        habits,
        "Select a habit to delete (or Cancel):",
        "No active habits found to delete.",
    )
    if not habit_to_delete:
        return  # _handle_habit_selection already shows cancellation message and waits for input
    confirm = questionary.confirm(
        f"Are you sure you want to delete '{habit_to_delete.name}'?"
    ).ask()
    if not confirm:
        show_colored_message("Deletion cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    db.delete_habit(habit_to_delete.id, db_name)
    show_colored_message(
        f"Habit '{habit_to_delete.name}' deleted (deactivated) successfully!",
        color=Fore.GREEN,
    )
    press_enter_to_continue()


def reactivate_habit(db_name: str):
    """Handles reactivating a soft-deleted habit."""
    show_colored_message(
        "\n--- Reactivate Habit ---", color=Fore.YELLOW, style=Style.BRIGHT
    )
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    deleted_habits = [h for h in habits if not h.is_active]
    if not deleted_habits:
        show_colored_message("No deleted habits found to reactivate.", color=Fore.RED)
        press_enter_to_continue()
        return
    # Use interactive menu for habit selection, with Cancel option
    choices = [
        f"{habit.id}. {habit.name} ({habit.frequency})" for habit in deleted_habits
    ]
    choices.append("Cancel")
    answer = questionary.select(
        "Select a habit to reactivate (or Cancel):", choices=choices
    ).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Reactivation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    try:
        habit_id = int(answer.split(".")[0])
        for habit in deleted_habits:
            if habit.id == habit_id:
                db.reactivate_habit(habit.id, db_name)
                show_colored_message(
                    f"Habit '{habit.name}' reactivated successfully!", color=Fore.GREEN
                )
                press_enter_to_continue()
                return
    except Exception:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return


def update_habit(db_name: str):
    """Handles updating an existing habit in the database."""
    show_colored_message(
        "\n--- Update Habit ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message(
            "No active habits found. Let's create one!", color=Fore.RED
        )
        press_enter_to_continue()
        return

    # Use interactive menu for habit selection
    habit_to_update = _handle_habit_selection(
        habits,
        "Select a habit to update (or Cancel):",
        "No active habits found to update.",
    )
    if not habit_to_update:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    show_colored_message(
        f"\n--- Updating Habit ID: {habit_to_update.id} - '{habit_to_update.name}' ---",
        color=Fore.CYAN,
        style=Style.BRIGHT,
    )
    if habit_to_update.reactivated_at:
        show_colored_message(
            f"Reactivated At: {habit_to_update.reactivated_at.strftime('%Y-%m-%d %H:%M')}",
            color=Fore.CYAN,
        )
    new_name = questionary.text(
        f"Enter new name for '{habit_to_update.name}' (leave blank to keep current name or type 'cancel' to exit):",
        default=habit_to_update.name,
    ).ask()
    if new_name is None or new_name.strip().lower() == "cancel":
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    if not new_name.strip():
        new_name = habit_to_update.name

    new_frequency = questionary.select(
        f"Select new frequency for '{habit_to_update.name}' (current: {habit_to_update.frequency}):",
        choices=["daily", "weekly"],
        default=habit_to_update.frequency,
    ).ask()

    new_notes = questionary.text(
        f"Enter new notes for '{habit_to_update.name}' (leave blank to keep current):",
        default=habit_to_update.notes if habit_to_update.notes else "",
    ).ask()
    if not new_notes:
        new_notes = None

    new_reminder_time = questionary.text(
        f"Enter new morning reminder time for '{habit_to_update.name}' (HH:MM, leave blank to keep current):",
        default=habit_to_update.reminder_time if habit_to_update.reminder_time else "",
        validate=_validate_time_format,
    ).ask()
    if not new_reminder_time:
        new_reminder_time = None

    new_evening_reminder_time = questionary.text(
        f"Enter new evening reminder time for '{habit_to_update.name}' (HH:MM, leave blank to keep current):",
        default=(
            habit_to_update.evening_reminder_time
            if habit_to_update.evening_reminder_time
            else ""
        ),
        validate=_validate_time_format,
    ).ask()
    if not new_evening_reminder_time:
        new_evening_reminder_time = None

    # Update category
    categories = db.get_all_categories(active_only=True, db_name=db_name)
    current_category = None
    if habit_to_update.category_id:
        current_category = db.get_category(habit_to_update.category_id, db_name)

    category_choices = ["No category"] + [f"{cat.id}. {cat.name}" for cat in categories]
    if current_category:
        category_choices.insert(1, f"Keep current ({current_category.name})")

    category_choice = questionary.select(
        f"Select new category for '{habit_to_update.name}' (current: {current_category.name if current_category else 'None'}):",
        choices=category_choices,
    ).ask()
    if category_choice == "Keep current" or (
        current_category
        and category_choice == f"Keep current ({current_category.name})"
    ):
        pass  # Keep current category
    elif category_choice == "No category":
        habit_to_update.category_id = None
    else:
        try:
            habit_to_update.category_id = int(category_choice.split(".")[0])
        except ValueError:
            pass

    habit_to_update.edit_habit(
        name=new_name,
        frequency=new_frequency,
        notes=new_notes,
        reminder_time=new_reminder_time,
        evening_reminder_time=new_evening_reminder_time,
    )
    db.update_habit(habit_to_update, db_name)
    show_colored_message(
        f"Habit ID {habit_to_update.id} updated successfully!",
        color=Fore.GREEN,
        style=Style.BRIGHT,
    )
    press_enter_to_continue()

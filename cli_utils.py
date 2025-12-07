import datetime

from momentum_utils import press_enter_to_continue, show_colored_message


def _validate_time_format(time_str: str) -> bool:
    """Validates the time format (HH:MM) and allows empty string for optional times."""
    if not time_str:
        return True
    try:
        datetime.datetime.strptime(time_str, "%H:%M").time()
        return True
    except ValueError:
        return "Invalid time format. Please use HH:MM (24-hour format)."


def press_enter_to_continue():
    """
    Waits for the user to press Enter before continuing.
    """
    input("Press Enter to continue...")


def _handle_habit_selection(habits, title, error_msg="No active habits found"):
    import questionary
    from colorama import Fore

    from momentum_utils import show_colored_message

    if not habits:
        show_colored_message(error_msg, color=Fore.RED)
        press_enter_to_continue()
        return None
    choices = [
        f"{habit.id}. {habit.name} ({habit.frequency}) - Streak: {habit.streak}"
        for habit in habits
    ]
    choices.append("Cancel")
    answer = questionary.select(title, choices=choices).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Operation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return None
    try:
        habit_id = int(answer.split(".")[0])
        for habit in habits:
            if habit.id == habit_id:
                return habit
    except Exception:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return None


def _to_date(dt):
    return dt.date() if hasattr(dt, "date") else dt

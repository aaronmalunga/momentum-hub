import os
import shutil

from colorama import Fore, Style
from pyfiglet import Figlet
from tabulate import tabulate

import momentum_db as db
from momentum_utils import press_enter_to_continue, show_colored_message


def startup_message():
    """Displays a startup message for the Momentum Hub CLI, centered and in ASCII art."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    figlet = Figlet(font="standard")
    ascii_title = figlet.renderText("Momentum Hub")
    # Center each line of the ASCII art
    centered_ascii = "\n".join(
        line.center(term_width) for line in ascii_title.splitlines()
    )
    subtitle = "Your personal habit tracker."
    centered_subtitle = subtitle.center(term_width)
    print("\n\n\n" + f"{Fore.GREEN}{centered_ascii}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{centered_subtitle}{Style.RESET_ALL}\n")


def view_habits(db_name: str):
    """Displays all active habits in a tabulated format."""
    show_colored_message("\n--- View Habits ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)

    if not habits:
        show_colored_message(
            "No active habits found. Let's create one!", color=Fore.RED
        )
    else:
        table = []
        for habit in habits:
            last_completed_str = (
                habit.last_completed.strftime("%Y-%m-%d %H:%M")
                if habit.last_completed
                else "-"
            )
            reactivated_at_str = (
                habit.reactivated_at.strftime("%Y-%m-%d %H:%M")
                if habit.reactivated_at
                else "-"
            )
            table.append(
                [
                    habit.id,
                    habit.name,
                    habit.frequency,
                    habit.streak,
                    habit.notes or "-",
                    habit.reminder_time or "-",
                    habit.evening_reminder_time or "-",
                    last_completed_str,
                    reactivated_at_str,
                ]
            )
        headers = [
            f"{Fore.CYAN}ID{Style.RESET_ALL}",
            f"{Fore.CYAN}Name{Style.RESET_ALL}",
            f"{Fore.CYAN}Frequency{Style.RESET_ALL}",
            f"{Fore.CYAN}Streak{Style.RESET_ALL}",
            f"{Fore.CYAN}Notes{Style.RESET_ALL}",
            f"{Fore.CYAN}Morning Reminder{Style.RESET_ALL}",
            f"{Fore.CYAN}Evening Reminder{Style.RESET_ALL}",
            f"{Fore.CYAN}Last Completed{Style.RESET_ALL}",
            f"{Fore.CYAN}Reactivated At{Style.RESET_ALL}",
        ]
        print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

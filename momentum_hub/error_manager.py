import os
import sqlite3

from colorama import Fore

from .momentum_utils import show_colored_message


class ErrorManager:
    """
    Manages error messages for the "Momentum Hub" application.
    """

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv("MOMENTUM_DB", "momentum.db")
        self.db_path = db_path
        self.error_messages = self._load_errors()

    def _load_errors(self):
        """Load error messages from database using context manager."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create table if not exists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS errors (
                    key TEXT PRIMARY KEY,
                    message TEXT NOT NULL
                )
            """
            )
            # Insert default messages if table is empty
            cursor.execute("SELECT COUNT(*) FROM errors")
            if cursor.fetchone()[0] == 0:
                default_errors = [
                    (
                        "empty_input",
                        "Even a snail leaves a trail! Please don't leave this field blank.",
                    ),
                    (
                        "invalid_number",
                        "That's not a number in my book! Please enter a digit.",
                    ),
                    (
                        "invalid_habit_id",
                        "Habit Not Found! Please check your ID and try again.",
                    ),
                    (
                        "invalid_menu_option",
                        "My crystal ball says that's not a valid choice. Try another number from the options.",
                    ),
                ]
                cursor.executemany(
                    "INSERT INTO errors (key, message) VALUES (?, ?)", default_errors
                )
            # Load errors into dict
            cursor.execute("SELECT key, message FROM errors")
            return dict(cursor.fetchall())

    def display_error(self, error_key: str, **kwargs):
        """
        Displays an error message based on a given key.
        Parameters:
        error_key (str): The key for the error message to display.
        **kwargs: Additional keyword arguments to format the error message.
        """

        message = self.error_messages.get(
            error_key, "An unexpected error occurred. Please try again."
        )
        formatted_message = message.format(
            **kwargs
        )  # For error messages like "Habit {habit_id} not found."
        show_colored_message(formatted_message, color=Fore.RED)


# Creates a gobal instance for easy access throughout the application
error_manager = ErrorManager()

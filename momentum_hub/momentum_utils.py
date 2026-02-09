from colorama import Fore, Style, init

init(autoreset=True)


def get_int_input(
    prompt: str, error_message: str = "Invalid input. Please enter a valid number."
) -> int:
    """
    Prompts for an integer input and handles invalid entries.
    Continues until a valid integer is entered.

    Prompt: str - Message shown to the caller.
    Error_message: str - Message shown when input is invalid.
    int - A valid integer input.
    """

    while True:
        try:
            choice = int(input(prompt))
            return int(choice)
        except ValueError:
            show_colored_message(error_message, color=Fore.RED)


def show_colored_message(message: str, color: str = "", style: str = ""):
    """
    Print a message with the specified color and style using Colorama.

    Parameters:
        message: str - Message to display.
        color: str - Foreground color from colorama.Fore (e.g., Fore.RED, Fore.GREEN).
        style: str - Text style from colorama.Style (e.g., Style.BRIGHT, Style.DIM).
    """

    print(f"{color}{style}{message}{Style.RESET_ALL}")


def press_enter_to_continue():
    """
    Waits for Enter before continuing.
    """
    input("Press Enter to continue...")

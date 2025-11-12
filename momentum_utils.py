import sys
import time
from colorama import Fore, Style, init

init(autoreset=True)

def get_int_input(prompt: str, error_message: str = "Invalid input. Please enter a valid number.") -> int:

    """
    Prompts the user for an integer input and handles invalid inputs.
    Continues to prompt until a valid integer is entered.   

    Prompt: str - The message is displayed to the user.
    Error_message: str - The message is displayed if the input is invalid.
    int - a valid integer input by the user.
    """



    while True:
        try:    
            choice = int(input(prompt))
            return int(choice)
        except ValueError:
            show_colored_message(error_message, color=Fore.RED)


def show_colored_message(message: str, color: str = '', style: str = ''):
    """
   print a message with specified color and style from the module "colorama"

   parameters:
    message: str - The message to be displayed.
    color: str - The foreground color to use from colorama.Fore (e.g., Fore.RED, Fore.GREEN).
    style: str - The text style to use from colorama.Style (e.g., Style.BRIGHT, Style.DIM).

    """

    print(f"{color}{style}{message}{Style.RESET_ALL}")

def press_enter_to_continue():
    """
    Waits for the user to press Enter before continuing.
    """
    input("Press Enter to continue...")

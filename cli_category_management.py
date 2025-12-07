import datetime

import questionary
from colorama import Fore, Style
from tabulate import tabulate

import momentum_db as db
from category import Category
from cli_utils import _handle_habit_selection
from error_manager import error_manager
from momentum_utils import press_enter_to_continue, show_colored_message


def manage_categories(db_name: str):
    """Handles the category management menu."""
    show_colored_message(
        "\n--- Manage Categories ---", color=Fore.YELLOW, style=Style.BRIGHT
    )
    choice = questionary.select(
        "What would you like to do with categories?",
        choices=[
            "Create a new category",
            "View all categories",
            "Update a category",
            "Delete a category",
            "Assign habit to category",
            "Back to Main Menu",
        ],
    ).ask()

    category_actions = {
        "Create a new category": lambda: create_category(db_name),
        "View all categories": lambda: view_categories(db_name),
        "Update a category": lambda: update_category(db_name),
        "Delete a category": lambda: delete_category(db_name),
        "Assign habit to category": lambda: assign_habit_to_category(db_name),
        "Back to Main Menu": lambda: None,
    }

    if choice in category_actions:
        category_actions[choice]()


def create_category(db_name: str):
    """Handles creating a new category."""
    show_colored_message(
        "\n--- Create New Category ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    while True:
        name = questionary.text(
            "Enter category name (or type 'cancel' to go back):"
        ).ask()
        if name is None or name.strip().lower() == "cancel":
            show_colored_message("Category creation cancelled.", color=Fore.YELLOW)
            press_enter_to_continue()
            return
        if not name.strip():
            show_colored_message("Category name cannot be empty.", color=Fore.RED)
            continue
        break

    description = questionary.text("Enter category description (optional):").ask()
    if description is None:
        show_colored_message("Category creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    color = questionary.text(
        "Enter category color (hex code, optional, e.g., #FF5733):"
    ).ask()
    if color is None:
        show_colored_message("Category creation cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    category = Category(
        name=name.strip(),
        description=description.strip() if description else None,
        color=color.strip() if color else None,
        is_active=True,
    )

    category_id = db.add_category(category, db_name)
    show_colored_message(
        f"Category '{name}' created successfully with ID: {category_id}",
        color=Fore.GREEN,
        style=Style.BRIGHT,
    )
    press_enter_to_continue()


def view_categories(db_name: str):
    """Handles viewing all categories."""
    show_colored_message(
        "\n--- All Categories ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    categories = db.get_all_categories(active_only=True, db_name=db_name)
    if not categories:
        show_colored_message("No active categories found.", color=Fore.RED)
        press_enter_to_continue()
        return

    table = []
    for category in categories:
        habits = category.get_habits(db_name)
        habit_count = len(habits)
        habit_names = ", ".join([h.name for h in habits[:3]])  # Show first 3 habits
        if habit_count > 3:
            habit_names += f" (+{habit_count - 3} more)"

        table.append(
            [
                category.id,
                category.name,
                category.description or "",
                category.color or "",
                habit_count,
                habit_names,
            ]
        )

    headers = [
        f"{Fore.CYAN}ID{Style.RESET_ALL}",
        f"{Fore.CYAN}Name{Style.RESET_ALL}",
        f"{Fore.CYAN}Description{Style.RESET_ALL}",
        f"{Fore.CYAN}Color{Style.RESET_ALL}",
        f"{Fore.CYAN}Habits{Style.RESET_ALL}",
        f"{Fore.CYAN}Habit Names{Style.RESET_ALL}",
    ]
    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()


def update_category(db_name: str):
    """Handles updating an existing category."""
    show_colored_message(
        "\n--- Update Category ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    categories = db.get_all_categories(active_only=True, db_name=db_name)
    if not categories:
        show_colored_message("No active categories found to update.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Create choices for category selection
    choices = [f"{cat.id}. {cat.name}" for cat in categories]
    choices.append("Cancel")

    answer = questionary.select("Select a category to update:", choices=choices).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    try:
        category_id = int(answer.split(".")[0])
        category = db.get_category(category_id, db_name)
        if not category:
            show_colored_message("Category not found.", color=Fore.RED)
            press_enter_to_continue()
            return
    except ValueError:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Update fields
    new_name = questionary.text(
        f"Enter new name for '{category.name}' (leave blank to keep current):",
        default=category.name,
    ).ask()
    if new_name is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    if new_name.strip():
        category.name = new_name.strip()

    new_description = questionary.text(
        f"Enter new description (leave blank to keep current):",
        default=category.description or "",
    ).ask()
    if new_description is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    category.description = new_description.strip() if new_description else None

    new_color = questionary.text(
        f"Enter new color (leave blank to keep current):", default=category.color or ""
    ).ask()
    if new_color is None:
        show_colored_message("Update cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    category.color = new_color.strip() if new_color else None

    db.update_category(category, db_name)
    show_colored_message(
        f"Category '{category.name}' updated successfully!",
        color=Fore.GREEN,
        style=Style.BRIGHT,
    )
    press_enter_to_continue()


def delete_category(db_name: str):
    """Handles deleting a category."""
    show_colored_message(
        "\n--- Delete Category ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    categories = db.get_all_categories(active_only=True, db_name=db_name)
    if not categories:
        show_colored_message("No active categories found to delete.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Create choices for category selection
    choices = [f"{cat.id}. {cat.name}" for cat in categories]
    choices.append("Cancel")

    answer = questionary.select("Select a category to delete:", choices=choices).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Deletion cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    try:
        category_id = int(answer.split(".")[0])
        category = db.get_category(category_id, db_name)
        if not category:
            show_colored_message("Category not found.", color=Fore.RED)
            press_enter_to_continue()
            return
    except ValueError:
        show_colored_message("Invalid selection.", color=Fore.RED)
        press_enter_to_continue()
        return

    # Check if category has habits
    habits = category.get_habits(db_name)
    if habits:
        show_colored_message(
            f"Warning: Category '{category.name}' has {len(habits)} habit(s) assigned. "
            "Deleting will remove habits from this category.",
            color=Fore.YELLOW,
        )

    confirm = questionary.confirm(
        f"Are you sure you want to delete category '{category.name}'?"
    ).ask()
    if not confirm:
        show_colored_message("Deletion cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    # Remove category from habits first
    for habit in habits:
        habit.category_id = None
        db.update_habit(habit, db_name)

    db.delete_category(category_id, db_name)
    show_colored_message(
        f"Category '{category.name}' deleted successfully!", color=Fore.GREEN
    )
    press_enter_to_continue()


def assign_habit_to_category(db_name: str):
    """Handles assigning a habit to a category."""
    show_colored_message(
        "\n--- Assign Habit to Category ---", color=Fore.YELLOW, style=Style.BRIGHT
    )

    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("No active habits found.", color=Fore.RED)
        press_enter_to_continue()
        return

    selected_habit = _handle_habit_selection(
        habits, "Select a habit to assign to a category:", "No active habits found."
    )
    if not selected_habit:
        return

    categories = db.get_all_categories(active_only=True, db_name=db_name)
    if not categories:
        show_colored_message(
            "No active categories found. Create a category first!", color=Fore.RED
        )
        press_enter_to_continue()
        return

    # Create choices for category selection
    choices = [f"{cat.id}. {cat.name}" for cat in categories]
    choices.append("Remove from category")
    choices.append("Cancel")

    answer = questionary.select(
        f"Select a category for habit '{selected_habit.name}':", choices=choices
    ).ask()
    if answer == "Cancel" or answer is None:
        show_colored_message("Assignment cancelled.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    if answer == "Remove from category":
        selected_habit.category_id = None
        db.update_habit(selected_habit, db_name)
        show_colored_message(
            f"Habit '{selected_habit.name}' removed from category!", color=Fore.GREEN
        )
    else:
        try:
            category_id = int(answer.split(".")[0])
            selected_habit.category_id = category_id
            db.update_habit(selected_habit, db_name)
            category = db.get_category(category_id, db_name)
            category_name = category.name if category else "Unknown"
            show_colored_message(
                f"Habit '{selected_habit.name}' assigned to category '{category_name}'!",
                color=Fore.GREEN,
            )
        except ValueError:
            show_colored_message("Invalid selection.", color=Fore.RED)

    press_enter_to_continue()

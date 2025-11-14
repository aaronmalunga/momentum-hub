import questionary
from colorama import Fore, Style
import momentum_db as db
from momentum_utils import show_colored_message, press_enter_to_continue
from cli_utils import _handle_habit_selection

def analyze_export_csv(db_name: str):
    """Handles exporting analysis to a CSV file."""
    show_colored_message("\n--- Export Analysis to CSV ---", color=Fore.YELLOW, style=Style.BRIGHT)

    analysis_choice = questionary.select(
        "What kind of analysis would you like to export?",
        choices=[
            "Export all habits and their details",
            "Export completions for all habits",
            "Export completions for a specific habit",
            "Back to Main Menu"
        ]
    ).ask()

    if analysis_choice == "Export all habits and their details":
        export_all_habits_to_csv(db_name)
    elif analysis_choice == "Export completions for all habits":
        export_all_completions_to_csv(db_name)
    elif analysis_choice == "Export completions for a specific habit":
        export_habit_completions_to_csv(db_name)
    elif analysis_choice == "Back to Main Menu":
        return

def export_all_habits_to_csv(db_name: str):
    """Export all habits to a CSV file."""
    import csv
    import os
    from datetime import datetime

    habits = db.get_all_habits(active_only=False, db_name=db_name)

    os.makedirs("CSV Export", exist_ok=True)
    filename = os.path.join("CSV Export", f"habits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID', 'Name', 'Frequency', 'Category', 'Goal Progress', 'Notes', 'Morning Reminder', 'Evening Reminder',
                         'Streak', 'Created At', 'Last Completed', 'Is Active', 'Reactivated At']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for habit in habits:
                # Get category name if habit has one
                category_name = ''
                if habit.category_id:
                    category = db.get_category(habit.category_id, db_name)
                    category_name = category.name if category else ''

                # Get goal progress if habit has active goals
                goal_progress = ''
                goals = db.get_all_goals(active_only=True, db_name=db_name)
                habit_goals = [g for g in goals if g.habit_id == habit.id]
                if habit_goals:
                    goal = max(habit_goals, key=lambda g: g.created_at)
                    progress = goal.calculate_progress(db_name)
                    goal_progress = f"{progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"

                writer.writerow({
                    'ID': habit.id,
                    'Name': habit.name,
                    'Frequency': habit.frequency,
                    'Category': category_name,
                    'Notes': habit.notes or '',
                    'Morning Reminder': habit.reminder_time or '',
                    'Evening Reminder': habit.evening_reminder_time or '',
                    'Streak': habit.streak,
                    'Goal Progress': goal_progress,
                    'Created At': habit.created_at.strftime('%Y-%m-%d %H:%M') if habit.created_at else '',
                    'Last Completed': habit.last_completed.strftime('%Y-%m-%d %H:%M') if habit.last_completed else '',
                    'Is Active': 'Yes' if habit.is_active else 'No',
                    'Reactivated At': habit.reactivated_at.strftime('%Y-%m-%d %H:%M') if habit.reactivated_at else ''
                })

        show_colored_message(f"Successfully exported {len(habits)} habits to {filename}", color=Fore.GREEN)
    except Exception as e:
        show_colored_message(f"Error exporting habits: {str(e)}", color=Fore.RED)

    press_enter_to_continue()

def export_all_completions_to_csv(db_name: str):
    """Export all completions to a CSV file."""
    import csv
    import os
    from datetime import datetime

    habits = db.get_all_habits(active_only=False, db_name=db_name)
    if not habits:
        show_colored_message("No habits found to export completions.", color=Fore.RED)
        press_enter_to_continue()
        return

    os.makedirs("CSV Export", exist_ok=True)
    filename = os.path.join("CSV Export", f"all_completions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Habit ID', 'Habit Name', 'Frequency', 'Completion Date', 'Completion Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            total_completions = 0
            
            for habit in habits:
                completions = db.get_completions(habit.id, db_name)
                for completion in completions:
                    writer.writerow({
                        'Habit ID': habit.id,
                        'Habit Name': habit.name,
                        'Frequency': habit.frequency,
                        'Completion Date': completion.strftime('%Y-%m-%d'),
                        'Completion Time': completion.strftime('%H:%M:%S')
                    })
                    total_completions += 1
        
        show_colored_message(f"Successfully exported {total_completions} completions to {filename}", color=Fore.GREEN)
    except Exception as e:
        show_colored_message(f"Error exporting completions: {str(e)}", color=Fore.RED)
    
    press_enter_to_continue()

def export_habit_completions_to_csv(db_name: str):
    """Export completions for a specific habit to a CSV file."""
    import csv
    import os
    from datetime import datetime

    habits = db.get_all_habits(active_only=False, db_name=db_name)
    if not habits:
        show_colored_message("No habits found to export completions.", color=Fore.RED)
        press_enter_to_continue()
        return

    selected_habit = _handle_habit_selection(habits, "Select a habit to export completions:", "No habits found to export.")
    if not selected_habit:
        return

    completions = db.get_completions(selected_habit.id, db_name)
    if not completions:
        show_colored_message(f"No completions found for '{selected_habit.name}'.", color=Fore.YELLOW)
        press_enter_to_continue()
        return

    os.makedirs("CSV Export", exist_ok=True)
    filename = os.path.join("CSV Export", f"completions_{selected_habit.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Habit ID', 'Habit Name', 'Frequency', 'Completion Date', 'Completion Time', 'Week Number']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for completion in completions:
                # Calculate week number for weekly habits
                week_number = ''
                if selected_habit.frequency == 'weekly':
                    from datetime import timedelta
                    completion_date = completion.date()
                    week_start = completion_date - timedelta(days=completion_date.weekday() + 1 if completion_date.weekday() < 6 else 0)
                    # Week number since habit creation
                    if selected_habit.created_at:
                        habit_start = selected_habit.created_at.date()
                        weeks_since_creation = ((week_start - habit_start).days // 7) + 1
                        week_number = f"Week {weeks_since_creation}"
                
                writer.writerow({
                    'Habit ID': selected_habit.id,
                    'Habit Name': selected_habit.name,
                    'Frequency': selected_habit.frequency,
                    'Completion Date': completion.strftime('%Y-%m-%d'),
                    'Completion Time': completion.strftime('%H:%M:%S'),
                    'Week Number': week_number
                })
        
        show_colored_message(f"Successfully exported {len(completions)} completions for '{selected_habit.name}' to {filename}", color=Fore.GREEN)
    except Exception as e:
        show_colored_message(f"Error exporting completions: {str(e)}", color=Fore.RED)
    
    press_enter_to_continue()

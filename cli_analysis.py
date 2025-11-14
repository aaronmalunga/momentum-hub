import questionary
from colorama import Fore, Style
from tabulate import tabulate
import momentum_db as db
import habit_analysis as analysis
from momentum_utils import show_colored_message, press_enter_to_continue
from cli_utils import _handle_habit_selection, _to_date
from cli_export import analyze_export_csv

def analyze_habits(db_name: str):
    """Handles the process of analyzing habits."""
    show_colored_message("\n--- Analyze Habits ---", color=Fore.YELLOW, style=Style.BRIGHT)
    analysis_choice = questionary.select(
        "What kind of analysis would you like to see?",
        choices=[
            "List all currently tracked habits",
            "List all habits with the same periodicity",
            "See the longest streak of all habits",
            "See the longest streak of a specific habit",
            "Show streak history (Calendar View)",
            "Export analysis to CSV",
            "Show best/worst habit",
            "Show goal progress",
            "Show completion history for a habit",
            "Back to Main Menu"
        ]
    ).ask()
    analysis_actions = {
        "List all currently tracked habits": lambda: analyze_list_all_habits(db_name),
        "List all habits with the same periodicity": lambda: analyze_by_periodicity(db_name),
        "See the longest streak of all habits": lambda: analyze_longest_streak_all(db_name),
        "See the longest streak of a specific habit": lambda: analyze_longest_streak_one(db_name),
        "Show streak history (Calendar View)": lambda: analyze_streak_history_grid(db_name),
        "Export analysis to CSV": lambda: analyze_export_csv(db_name),
        "Show best/worst habit": lambda: analyze_best_worst_habit(db_name),
        "Show goal progress": lambda: analyze_goal_progress(db_name),
        "Show completion history for a habit": lambda: analyze_completion_history(db_name),
        "Back to Main Menu": lambda: None
    }
    if analysis_choice in analysis_actions:
        analysis_actions[analysis_choice]()

def analyze_list_all_habits(db_name: str):
    show_colored_message("\n--- All Currently Tracked Habits ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("No active habits found.", color=Fore.RED)
    else:
        table = []
        for habit in habits:
            created_at_str = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "-"
            table.append([habit.id, habit.name, created_at_str])
        headers = [f"{Fore.CYAN}ID{Style.RESET_ALL}", f"{Fore.CYAN}Name{Style.RESET_ALL}", f"{Fore.CYAN}Created At{Style.RESET_ALL}"]
        print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def analyze_by_periodicity(db_name: str):
    show_colored_message("\n--- Habits by Periodicity ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("You have no active habits to analyze.", color=Fore.RED)
        press_enter_to_continue()
        return
    periodicity_choice = questionary.select("Select a periodicity to filter habits:", choices=["daily", "weekly", "all", "Cancel"]).ask()
    if periodicity_choice is None or periodicity_choice == "Cancel" or not periodicity_choice:
        show_colored_message("Operation cancelled. No periodicity selected.", color=Fore.RED)
        press_enter_to_continue()
        return
    if periodicity_choice == "all":
        filtered_habits = db.get_all_habits(active_only=True, db_name=db_name)
    else:
        filtered_habits = [h for h in habits if h.frequency == periodicity_choice]
    if not filtered_habits:
        show_colored_message(f"No {periodicity_choice} habits found.", color=Fore.RED)
    else:
        table = []
        for habit in filtered_habits:
            longest_streak = analysis.calculate_longest_streak_for_habit(habit.id, db_name)
            last_completed_str = habit.last_completed.strftime("%Y-%m-%d %H:%M") if habit.last_completed else "-"
            created_at_str = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "-"
            current_streak_col = f"{Fore.GREEN}{habit.streak}{Style.RESET_ALL}" if habit.streak > 0 else f"{Fore.RED}{habit.streak}{Style.RESET_ALL}"
            completion_rate = analysis.calculate_completion_rate_for_habit(habit.id, db_name)
            completion_rate_col = (f"{Fore.GREEN}{completion_rate*100:.0f}%{Style.RESET_ALL}" if completion_rate >= 0.8
                                 else f"{Fore.YELLOW}{completion_rate*100:.0f}%{Style.RESET_ALL}" if completion_rate >= 0.5
                                 else f"{Fore.RED}{completion_rate*100:.0f}%{Style.RESET_ALL}")
            table.append([habit.id, habit.name, habit.frequency, current_streak_col, created_at_str,
                         longest_streak, completion_rate_col, last_completed_str])
        headers = [f"{Fore.CYAN}ID{Style.RESET_ALL}", f"{Fore.CYAN}Name{Style.RESET_ALL}", f"{Fore.CYAN}Periodicity{Style.RESET_ALL}",
                  f"{Fore.CYAN}Current{Style.RESET_ALL}", f"{Fore.CYAN}Created At{Style.RESET_ALL}", f"{Fore.CYAN}Longest{Style.RESET_ALL}",
                  f"{Fore.CYAN}Completion Rate{Style.RESET_ALL}", f"{Fore.CYAN}Last Completed{Style.RESET_ALL}"]
        print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def analyze_longest_streak_all(db_name: str):
    show_colored_message("\n--- Longest Streaks of All Habits ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    if not habits:
        show_colored_message("No active habits found to analyze.", color=Fore.RED)
        press_enter_to_continue()
        return
    table = []
    for habit in habits:
        longest_streak = analysis.calculate_longest_streak_for_habit(habit.id, db_name)
        created_at_str = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "-"
        current_streak_col = f"{Fore.GREEN}{habit.streak}{Style.RESET_ALL}" if habit.streak > 0 else f"{Fore.RED}{habit.streak}{Style.RESET_ALL}"
        longest_streak_col = f"{Fore.GREEN}{longest_streak}{Style.RESET_ALL}" if longest_streak > 0 else f"{Fore.RED}{longest_streak}{Style.RESET_ALL}"
        table.append([habit.id, habit.name, habit.frequency, created_at_str, longest_streak_col, current_streak_col])
    headers = [f"{Fore.CYAN}ID{Style.RESET_ALL}", f"{Fore.CYAN}Name{Style.RESET_ALL}", f"{Fore.CYAN}Periodicity{Style.RESET_ALL}",
              f"{Fore.CYAN}Created At{Style.RESET_ALL}", f"{Fore.CYAN}Longest Streak{Style.RESET_ALL}", f"{Fore.CYAN}Current Streak{Style.RESET_ALL}"]
    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def analyze_longest_streak_one(db_name: str):
    show_colored_message("\n--- Longest Streak of a Specific Habit ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    selected_habit = _handle_habit_selection(habits, "Select a habit to analyze its longest streak:", "No active habits found to analyze.")
    if not selected_habit:
        return
    habit_to_analyze = selected_habit
    longest_streak = analysis.calculate_longest_streak_for_habit(habit_to_analyze.id, db_name)
    last_completed = habit_to_analyze.last_completed.strftime("%Y-%m-%d %H:%M") if habit_to_analyze.last_completed else "-"
    created_at_str = habit_to_analyze.created_at.strftime("%Y-%m-%d %H:%M") if habit_to_analyze.created_at else "-"
    if habit_to_analyze.reactivated_at:
        show_colored_message(f"Reactivated At: {habit_to_analyze.reactivated_at.strftime('%Y-%m-%d %H:%M')}", color=Fore.CYAN)
    current_streak_col = f"{Fore.GREEN}{habit_to_analyze.streak}{Style.RESET_ALL}" if habit_to_analyze.streak > 0 else f"{Fore.RED}{habit_to_analyze.streak}{Style.RESET_ALL}"
    longest_streak_col = f"{Fore.GREEN}{longest_streak}{Style.RESET_ALL}" if longest_streak > 0 else f"{Fore.RED}{longest_streak}{Style.RESET_ALL}"
    table = [[habit_to_analyze.id, habit_to_analyze.name, habit_to_analyze.frequency, created_at_str,
              longest_streak_col, current_streak_col, last_completed]]
    headers = [f"{Fore.CYAN}ID{Style.RESET_ALL}", f"{Fore.CYAN}Name{Style.RESET_ALL}", f"{Fore.CYAN}Periodicity{Style.RESET_ALL}",
              f"{Fore.CYAN}Created At{Style.RESET_ALL}", f"{Fore.CYAN}Longest{Style.RESET_ALL}", f"{Fore.CYAN}Current{Style.RESET_ALL}",
              f"{Fore.CYAN}Last Completed{Style.RESET_ALL}"]
    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def analyze_streak_history_grid(db_name: str):
    show_colored_message("\n--- Streak History (Calendar View) ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    selected_habit = _handle_habit_selection(habits, "Select a habit to view its streak history:", "No active habits found to analyze.")
    if not selected_habit:
        return
    habit = selected_habit
    completions = db.get_completions(habit.id, db_name)
    completion_dates = set(_to_date(c) for c in completions)
    from datetime import date, timedelta
    today = date.today()
    habit_created_date = habit.created_at.date() if habit.created_at else today
    created_at_str = habit.created_at.strftime("%Y-%m-%d %H:%M") if habit.created_at else "-"
    show_colored_message(f"Created At: {created_at_str}", color=Fore.CYAN)
    if habit.reactivated_at:
        show_colored_message(f"Reactivated At: {habit.reactivated_at.strftime('%Y-%m-%d %H:%M')}", color=Fore.CYAN)
    total_completions = len(completions)
    show_colored_message(f"Total completions: {total_completions}", color=Fore.CYAN)
    import calendar
    if habit.frequency == "daily":
        current_month = today.month
        current_year = today.year
        calendar.setfirstweekday(calendar.SUNDAY)
        cal = calendar.monthcalendar(current_year, current_month)
        month_name = calendar.month_name[current_month]
        print(f"\n    {month_name} {current_year}")
        print("Sun Mon Tue Wed Thu Fri Sat")
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "    "
                else:
                    check_date = date(current_year, current_month, day)
                    if check_date > today:
                        week_str += f"{Fore.LIGHTBLACK_EX}{day:3d}{Style.RESET_ALL} "
                    elif check_date < habit_created_date:
                        week_str += f"{Fore.WHITE}{day:3d}{Style.RESET_ALL} "
                    elif check_date in completion_dates:
                        week_str += f"{Fore.GREEN}{day:3d}{Style.RESET_ALL} "
                    else:
                        week_str += f"{Fore.RED}{day:3d}{Style.RESET_ALL} "
            print(week_str)
        print(f"\nLegend:")
        print(f"{Fore.GREEN}Green{Style.RESET_ALL} = Completed")
        print(f"{Fore.RED}Red{Style.RESET_ALL} = Missed")
        print(f"{Fore.WHITE}White{Style.RESET_ALL} = Before habit creation")
        print(f"{Fore.LIGHTBLACK_EX}Gray{Style.RESET_ALL} = Future dates")
        if total_completions > 0:
            month_completions = sum(1 for d in completion_dates if d.month == current_month and d.year == current_year)
            from calendar import monthrange
            days_in_month = monthrange(current_year, current_month)[1]
            completion_rate = month_completions / days_in_month
            show_colored_message(f"Completion rate this month: {completion_rate*100:.1f}% ({month_completions}/{days_in_month} days)", color=Fore.MAGENTA)
    elif habit.frequency == "weekly":
        # Calculate the first week (Sunday) containing the creation date
        from datetime import timedelta
        creation_week_start = habit_created_date - timedelta(days=(habit_created_date.weekday() + 1) % 7)
        today = date.today()
        current_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        # Number of weeks since creation (inclusive)
        total_weeks = ((current_week_start - creation_week_start).days // 7) + 1
        weeks_to_show = min(8, total_weeks)
        print("\nLast {} weeks (Sunday-Saturday):".format(weeks_to_show))
        completed_weeks = 0
        for i in range(weeks_to_show):
            this_week_start = creation_week_start + timedelta(weeks=i)
            this_week_end = this_week_start + timedelta(days=6)
            week_label = f"Week {i+1:2d} "
            # Determine if this week is in the future
            if this_week_start > current_week_start:
                # Future week: all gray dashes
                week_row = week_label + f"{Fore.LIGHTBLACK_EX}  -  {Style.RESET_ALL}" * 7
            else:
                # Check if any completion exists in this week
                week_completed = any((c >= this_week_start and c <= this_week_end) for c in completion_dates)
                if week_completed:
                    week_row = week_label + f"{Fore.GREEN}  ✓  {Style.RESET_ALL}" * 7
                    completed_weeks += 1
                else:
                    week_row = week_label + f"{Fore.RED}  ✗  {Style.RESET_ALL}" * 7
            print(week_row)
        print(f"\nLegend:")
        print(f"{Fore.GREEN}Green{Style.RESET_ALL} = Week completed")
        print(f"{Fore.RED}Red{Style.RESET_ALL} = Week not completed")
        print(f"{Fore.LIGHTBLACK_EX}Gray{Style.RESET_ALL} = Future dates")
        if weeks_to_show > 0:
            weekly_completion_rate = completed_weeks / weeks_to_show
            show_colored_message(f"Completion rate last {weeks_to_show} weeks: {weekly_completion_rate*100:.1f}% ({completed_weeks}/{weeks_to_show} weeks)", color=Fore.MAGENTA)
    else:
        show_colored_message("Unsupported periodicity for calendar view.", color=Fore.RED)
    if total_completions == 0 or (habit.streak == 0):
        show_colored_message("Habit not completed yet.", color=Fore.YELLOW)
        press_enter_to_continue()
        return
    press_enter_to_continue()

def analyze_best_worst_habit(db_name: str):
    """Handles displaying the best and worst habit."""
    show_colored_message("\n--- Best and Worst Habit ---", color=Fore.YELLOW, style=Style.BRIGHT)
    try:
        best_habit, worst_habit = analysis.calculate_best_worst_habit(db_name)
        if best_habit and worst_habit:
            table = [
                [f"{Fore.GREEN}Best{Style.RESET_ALL}", f"{Fore.GREEN}{best_habit.name}{Style.RESET_ALL}", f"{Fore.GREEN}{best_habit.streak}{Style.RESET_ALL}"],
                [f"{Fore.RED}Worst{Style.RESET_ALL}", f"{Fore.RED}{worst_habit.name}{Style.RESET_ALL}", f"{Fore.RED}{worst_habit.streak}{Style.RESET_ALL}"]
            ]
            headers = [f"{Fore.CYAN}Type{Style.RESET_ALL}", f"{Fore.CYAN}Name{Style.RESET_ALL}", f"{Fore.CYAN}Streak{Style.RESET_ALL}"]
            print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
        else:
            show_colored_message("No streaks found for any active habits yet. Keep tracking!", color=Fore.RED)
    except Exception as e:
        show_colored_message(f"An error occurred: {e}", color=Fore.RED)
    press_enter_to_continue()

def analyze_goal_progress(db_name: str):
    """Handles displaying goal progress for all goals."""
    show_colored_message("\n--- Goal Progress ---", color=Fore.YELLOW, style=Style.BRIGHT)

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
        f"{Fore.CYAN}Goal ID{Style.RESET_ALL}",
        f"{Fore.CYAN}Habit{Style.RESET_ALL}",
        f"{Fore.CYAN}Period (days){Style.RESET_ALL}",
        f"{Fore.CYAN}Target{Style.RESET_ALL}",
        f"{Fore.CYAN}Progress{Style.RESET_ALL}",
        f"{Fore.CYAN}Status{Style.RESET_ALL}"
    ]
    print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

def analyze_completion_history(db_name: str):
    """Handles displaying completion history."""
    show_colored_message("\n--- Completion History ---", color=Fore.YELLOW, style=Style.BRIGHT)
    habits = db.get_all_habits(active_only=True, db_name=db_name)
    selected_habit = _handle_habit_selection(habits, "Select a habit to view its completion history:", "No active habits found to analyze.")
    if not selected_habit:
        return
    completion_history = analysis.get_completion_history(selected_habit.id, db_name)
    if not completion_history:
        show_colored_message("No completions recorded yet for this habit.", color=Fore.YELLOW)
    else:
        table = [[i+1, dt.strftime('%Y-%m-%d %H:%M')] for i, dt in enumerate(completion_history)]
        headers = [f"{Fore.CYAN}# {Style.RESET_ALL}", f"{Fore.CYAN}Completion Date/Time{Style.RESET_ALL}"]
        print(tabulate(table, headers=headers, tablefmt="grid", stralign="center"))
    press_enter_to_continue()

"""
Enhanced Demo for Momentum Hub with Rich, InquirerPy, and Plotly

This file simulates how advanced libraries could enhance the Momentum Hub CLI:
- Rich: For rich text formatting, tables, and progress bars
- InquirerPy: For modern, styled prompts and selections
- Plotly: For interactive data visualization (charts for habit analysis)

Run this file to see the enhancements in action with mock data.
"""

import csv
import datetime
import random

import plotly.graph_objects as go
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Mock data for demonstration (simulating habit data) - using predefined habits
mock_habits = [
    {
        "name": "Change beddings",
        "frequency": "weekly",
        "streak": 7,
        "completion_rate": 0.5,
        "category": "Health",
    },
    {
        "name": "Code",
        "frequency": "daily",
        "streak": 28,
        "completion_rate": 1.0,
        "category": "Productivity",
    },
    {
        "name": "Study",
        "frequency": "daily",
        "streak": 23,
        "completion_rate": 0.89,
        "category": "Learning",
    },
    {
        "name": "Meditate",
        "frequency": "daily",
        "streak": 15,
        "completion_rate": 0.95,
        "category": "Mindfulness",
    },
    {
        "name": "Blog",
        "frequency": "weekly",
        "streak": 7,
        "completion_rate": 1.0,
        "category": "Productivity",
    },
]

mock_completion_history = {
    "Change beddings": [
        datetime.date.today() - datetime.timedelta(weeks=i)
        for i in range(7)
    ],
    "Code": [
        datetime.date.today() - datetime.timedelta(days=i)
        for i in range(28)
    ],
    "Study": [
        datetime.date.today() - datetime.timedelta(days=i)
        for i in range(28)
        if i not in [26, 25, 24]  # Skip 3 days for misses
    ],
    "Meditate": [
        datetime.date.today() - datetime.timedelta(days=i)
        for i in range(15)
    ],
    "Blog": [
        datetime.date.today() - datetime.timedelta(weeks=i)
        for i in range(7)
    ],
}

console = Console()


def enhanced_startup_message():
    """Enhanced startup message using Rich."""
    title = Text("Momentum Hub", style="bold magenta")
    subtitle = Text("Enhanced CLI Habit Tracker", style="italic cyan")
    panel = Panel.fit(
        f"{title}\n{subtitle}\n\nWelcome! Let's build better habits together.",
        border_style="green",
    )
    console.print(panel)


def enhanced_view_habits():
    """View habits using Rich table instead of tabulate."""
    table = Table(title="Your Habits", show_header=True, header_style="bold blue")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Frequency", style="magenta")
    table.add_column("Streak", justify="right", style="green")
    table.add_column("Completion Rate", justify="right", style="yellow")
    table.add_column("Category", style="red")

    for habit in mock_habits:
        table.add_row(
            habit["name"],
            habit["frequency"],
            str(habit["streak"]),
            f"{habit['completion_rate']:.1%}",
            habit["category"],
        )

    console.print(table)


def enhanced_analyze_streaks():
    """Analyze streaks with Rich progress bars."""
    console.print("\n[bold green]Analyzing Streaks...[/bold green]")
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        task = progress.add_task(
            "Calculating longest streaks...", total=len(mock_habits)
        )
        for habit in mock_habits:
            progress.update(
                task, advance=1, description=f"Processing {habit['name']}..."
            )

    # Display results in a table
    table = Table(title="Longest Streaks", show_header=True, header_style="bold blue")
    table.add_column("Habit", style="cyan")
    table.add_column("Current Streak", justify="right", style="green")
    table.add_column("Longest Streak", justify="right", style="yellow")

    for habit in mock_habits:
        longest = habit["streak"] + random.randint(0, 5)  # Mock longest streak
        table.add_row(habit["name"], str(habit["streak"]), str(longest))

    console.print(table)


def enhanced_main_menu():
    """Main menu using InquirerPy for modern prompts."""
    choice = inquirer.select(
        message="What would you like to do? Let's keep the momentum going!",
        choices=[
            Choice("view", name="View Habits"),
            Choice("add", name="Add New Habit"),
            Choice("log", name="Log Completion"),
            Choice("stats", name="View Detailed Stats"),
            Choice("analyze", name="Analyze Habits"),
            Choice("visualize", name="Visualize Progress"),
            Choice("export", name="Export Data"),
            Separator(),
            Choice("exit", name="Exit"),
        ],
        default="view",
    ).execute()

    actions = {
        "view": enhanced_view_habits,
        "add": enhanced_add_habit,
        "log": enhanced_log_completion,
        "stats": enhanced_view_detailed_stats,
        "analyze": enhanced_analyze_streaks,
        "visualize": visualize_completion_rates,
        "export": enhanced_export_data,
        "exit": lambda: console.print(
            "[green]Thank you for using Momentum Hub![/green]"
        ),
    }

    if choice in actions:
        actions[choice]()


def visualize_completion_rates():
    """Visualize completion rates using Plotly."""
    console.print("\n[bold blue]Generating Completion Rate Chart...[/bold blue]")

    habits = [h["name"] for h in mock_habits]
    rates = [h["completion_rate"] for h in mock_habits]

    fig = go.Figure(
        data=[
            go.Bar(
                x=habits,
                y=rates,
                marker_color=["skyblue", "lightgreen", "lightcoral", "gold"],
                text=[f"{rate:.1%}" for rate in rates],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Habit Completion Rates (Last 30 Days)",
        xaxis_title="Habits",
        yaxis_title="Completion Rate",
        yaxis=dict(range=[0, 1]),
        showlegend=False,
    )

    fig.show()  # This would display the interactive chart in a browser window

    console.print(
        "[green]Interactive chart displayed! (In a real app, this would open an interactive visualization in your browser.)[/green]"
    )


def visualize_streak_history():
    """Visualize streak history over time using Plotly."""
    console.print("\n[bold blue]Generating Streak History Chart...[/bold blue]")

    fig = go.Figure()

    for habit_name, dates in mock_completion_history.items():
        if dates:
            # Convert dates to days since start
            start_date = min(dates)
            days = [(d - start_date).days for d in dates]
            cumulative = list(range(1, len(days) + 1))

            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=cumulative,
                    mode="lines+markers",
                    name=habit_name,
                    line=dict(width=2),
                )
            )

    fig.update_layout(
        title="Habit Completion Streaks Over Time",
        xaxis_title="Days Since First Completion",
        yaxis_title="Cumulative Completions",
        showlegend=True,
    )

    fig.show()

    console.print("[green]Interactive streak history chart displayed![/green]")


def enhanced_add_habit():
    """Add a new habit using InquirerPy inputs."""
    console.print("\n[bold cyan]Adding a New Habit[/bold cyan]")

    name = inquirer.text(message="Enter habit name:").execute()
    if not name:
        console.print("[red]Habit name cannot be empty.[/red]")
        return

    frequency = inquirer.select(
        message="Select frequency:",
        choices=[
            Choice("daily", name="Daily"),
            Choice("weekly", name="Weekly"),
            Choice("monthly", name="Monthly"),
        ],
        default="daily",
    ).execute()

    category = inquirer.text(
        message="Enter category (e.g., Health, Learning):"
    ).execute()
    if not category:
        category = "General"

    # Add to mock data
    new_habit = {
        "name": name,
        "frequency": frequency,
        "streak": 0,
        "completion_rate": 0.0,
        "category": category,
    }
    mock_habits.append(new_habit)
    mock_completion_history[name] = []

    console.print(f"[green]Habit '{name}' added successfully![/green]")


def enhanced_log_completion():
    """Log a completion for a selected habit."""
    if not mock_habits:
        console.print("[red]No habits available. Add a habit first.[/red]")
        return

    console.print("\n[bold cyan]Logging Completion[/bold cyan]")

    habit_choices = [Choice(h["name"], name=h["name"]) for h in mock_habits]
    habit_name = inquirer.select(
        message="Select habit to log completion:", choices=habit_choices
    ).execute()

    # Simple date input (in real app, use date picker)
    date_str = inquirer.text(
        message="Enter date (YYYY-MM-DD) or press Enter for today:"
    ).execute()
    if not date_str:
        completion_date = datetime.date.today()
    else:
        try:
            completion_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]Invalid date format. Using today.[/red]")
            completion_date = datetime.date.today()

    # Add to history
    if habit_name not in mock_completion_history:
        mock_completion_history[habit_name] = []
    mock_completion_history[habit_name].append(completion_date)

    # Update streak and rate (mock update)
    habit = next(h for h in mock_habits if h["name"] == habit_name)
    habit["streak"] += 1
    habit["completion_rate"] = min(1.0, habit["completion_rate"] + 0.05)

    console.print(
        f"[green]Completion logged for '{habit_name}' on {completion_date}![/green]"
    )


def enhanced_view_detailed_stats():
    """View detailed statistics for a selected habit."""
    if not mock_habits:
        console.print("[red]No habits available.[/red]")
        return

    console.print("\n[bold cyan]Detailed Habit Statistics[/bold cyan]")

    habit_choices = [Choice(h["name"], name=h["name"]) for h in mock_habits]
    habit_name = inquirer.select(
        message="Select habit for details:", choices=habit_choices
    ).execute()

    habit = next(h for h in mock_habits if h["name"] == habit_name)
    history = mock_completion_history.get(habit_name, [])

    # Calculate stats
    total_completions = len(history)
    if history:
        first_completion = min(history)
        last_completion = max(history)
        days_since_start = (datetime.date.today() - first_completion).days + 1
        avg_completions_per_day = total_completions / days_since_start
    else:
        first_completion = None
        last_completion = None
        avg_completions_per_day = 0

    # Rich panel with details
    details = f"""
Name: {habit['name']}
Frequency: {habit['frequency']}
Category: {habit['category']}
Current Streak: {habit['streak']}
Completion Rate: {habit['completion_rate']:.1%}
Total Completions: {total_completions}
Average per Day: {avg_completions_per_day:.2f}
First Completion: {first_completion if first_completion else 'None'}
Last Completion: {last_completion if last_completion else 'None'}
"""

    panel = Panel.fit(
        details.strip(), title=f"Stats for {habit_name}", border_style="blue"
    )
    console.print(panel)

    # Mini chart for recent completions
    if history:
        console.print(
            "\n[bold yellow]Recent Completion Trend (last 30 days):[/bold yellow]"
        )
        recent_dates = [d for d in history if (datetime.date.today() - d).days <= 30]

        # Create histogram data
        days = [d.day for d in recent_dates]
        fig = go.Figure(
            data=[go.Histogram(x=days, nbinsx=30, marker_color="skyblue", opacity=0.7)]
        )

        fig.update_layout(
            title=f"Completion Days for {habit_name}",
            xaxis_title="Day of Month",
            yaxis_title="Completions",
            bargap=0.1,
        )

        fig.show()
        console.print("[green]Interactive mini chart displayed![/green]")


def enhanced_export_data():
    """Export habit data to a CSV file."""
    console.print("\n[bold cyan]Exporting Data[/bold cyan]")

    filename = inquirer.text(
        message="Enter filename (without .csv):", default="habits_export"
    ).execute()
    if not filename:
        filename = "habits_export"

    filepath = f"{filename}.csv"

    with open(filepath, "w", newline="") as csvfile:
        fieldnames = [
            "name",
            "frequency",
            "streak",
            "completion_rate",
            "category",
            "total_completions",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for habit in mock_habits:
            total_completions = len(mock_completion_history.get(habit["name"], []))
            row = habit.copy()
            row["total_completions"] = total_completions
            writer.writerow(row)

    console.print(f"[green]Data exported to '{filepath}' successfully![/green]")


def demo_enhanced_features():
    """Run the full demo."""
    enhanced_startup_message()

    while True:
        enhanced_main_menu()
        if (
            inquirer.confirm(message="Continue exploring?", default=True).execute()
            == False
        ):
            break


if __name__ == "__main__":
    demo_enhanced_features()

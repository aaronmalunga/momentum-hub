# Momentum Hub

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/momentum-hub/ci.yml)](https://github.com/yourusername/momentum-hub/actions)

A powerful, modern CLI habit tracker designed to help you build and maintain daily and weekly habits. Track your progress, analyze patterns, set goals, and stay motivated with rich analytics and an intuitive interface.

## ✨ Key Features

- **📊 Advanced Analytics**: Track streaks, completion rates, and visualize progress with calendar views and detailed statistics
- **🎯 Goal Setting**: Set specific targets for your habits (e.g., complete 30 times in 30 days)
- **🏷️ Smart Categorization**: Organize habits into colored categories for better organization
- **📈 Rich Visualizations**: Interactive charts and progress indicators (with enhanced UI options)
- **💾 Data Export**: Export your data to CSV for external analysis
- **🎮 Demo Mode**: Try the app instantly with pre-populated demo data (isolated from your real data)
- **🔄 Habit Management**: Create, update, delete, and reactivate habits with ease
- **📅 Completion Tracking**: Log completions with timestamps and maintain detailed history
- **🎨 Modern CLI**: Beautiful, interactive interface with colors, tables, and ASCII art

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Install from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/momentum-hub.git
cd momentum-hub

# Install the package
pip install .
```

### Install in Development Mode
```bash
# For development/contribution
pip install -e .[dev]
```

## 🎯 Quick Start

1. **Launch the app**:
   ```bash
   momentum
   # or
   python momentum_main.py
   ```

2. **Create your first habit**:
   - Choose "Create a new habit" from the main menu
   - Enter habit name, frequency (daily/weekly), and optional details

3. **Log completions**:
   - Select "Mark a habit as completed" to record progress
   - Watch your streaks grow!

4. **View analytics**:
   - Choose "Analyze habits" to see detailed statistics and trends

## 🎮 Demo Mode

Experience Momentum Hub instantly without setup:

```bash
# Launch with demo data (isolated database)
python momentum_main.py --demo
```

Demo mode includes:
- Pre-populated habits across different categories
- Sample completion data
- Goal examples
- Safe exploration without affecting your real data

The demo database (`momentum_demo.db`) is completely separate from your main data.

## 📖 Advanced Usage

### Command Line Options
```bash
# Use custom database file
python momentum_main.py --db my_habits.db

# Launch demo mode
python momentum_main.py --demo

# Get help
python momentum_main.py --help
```

### Core Workflows

#### Habit Management
- **Create**: Add new habits with custom frequencies, reminders, and categories
- **Update**: Modify habit details, frequencies, or settings
- **Delete/Reactivate**: Soft delete habits and bring them back when ready
- **Categorize**: Group habits by themes (Health, Productivity, Learning, etc.)

#### Analytics & Insights
- **Streak Tracking**: Monitor current and longest streaks
- **Completion Rates**: View success rates over time periods
- **Calendar Views**: Visual calendar showing completion patterns
- **Best/Worst Analysis**: Identify your most and least successful habits
- **Goal Progress**: Track progress toward specific targets

#### Data Management
- **Export to CSV**: Download habits, completions, or analytics data
- **Backup Safety**: Automatic backup creation before destructive operations
- **Category Analysis**: View statistics grouped by categories

### Example Session
```
Welcome to Momentum Hub!
Your personal habit tracker.

What would you like to do?
❯ Create a new habit
  Mark a habit as completed
  View habits
  Analyze habits
  Create goal
  Exit
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/momentum-hub.git
   cd momentum-hub
   ```

3. **Set up development environment**:
   ```bash
   pip install -e .[dev]
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

6. **Make your changes and add tests**

7. **Run the full test suite**:
   ```bash
   pytest --cov=src
   ```

8. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Use type hints where appropriate
- Keep the CLI user-friendly and intuitive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Homepage](https://github.com/yourusername/momentum-hub)
- [Documentation](https://github.com/yourusername/momentum-hub#readme)
- [Issues](https://github.com/yourusername/momentum-hub/issues)
- [Repository](https://github.com/yourusername/momentum-hub.git)

## 🙏 Acknowledgments

Built with modern Python libraries including:
- [Questionary](https://github.com/tmbo/questionary) - Interactive prompts
- [Colorama](https://github.com/tartley/colorama) - Cross-platform colors
- [Tabulate](https://github.com/astanin/python-tabulate) - Beautiful tables
- [PyFiglet](https://github.com/pwaller/pyfiglet) - ASCII art

---

**Start building better habits today with Momentum Hub!** 🚀

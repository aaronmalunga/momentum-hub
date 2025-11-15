# Momentum Hub

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/momentum-hub/ci.yml)](https://github.com/yourusername/momentum-hub/actions)

![Momentum Hub Banner](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/ChatGPT%20Image%20Jul%2012,%202025,%2001_31_30%20PM.png)

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

## 📸 Screenshots

### Main Menu Interface
![Main Menu Interface](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Main%20menu%20interface.png)
*The main menu showing all available options for habit management, analytics, and data operations.*

### Habit Creation Form
![Habit Creation Form](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Habit%20creation%20form.png)
*Interactive form for creating new habits with frequency selection, reminders, and category assignment.*

### Analytics Dashboard
![Analytics Dashboard 1](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Analytics%20dash1.png)
*Comprehensive analytics view showing habit statistics, completion rates, and progress tracking.*

![Analytics Dashboard 2](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Analytics%20dash2.png)
*Detailed analytics including streak tracking and performance metrics.*

### List All Habits View
![List All Habits](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/list%20all%20habits.png)
*Overview of all habits with their current status, streaks, and completion information.*

### CSV Export Functionality
![CSV Export](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/csv%20export.png)
*Data export interface allowing users to download habits, completions, and analytics data.*

## 🎮 Demo Mode

Experience Momentum Hub instantly without setup:

```bash
# Launch with demo data (isolated database)
python momentum_main.py --demo
```

![Demo Mode Welcome](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Main%20menu%20interface.png)
*The demo mode welcome screen showing pre-populated data and available options.*

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

### 📚 Documentation
- **[API Documentation](docs/api.md)**: Comprehensive API reference for developers
- **[Usage Guide](USAGE.md)**: Advanced usage patterns and reviewer workflows

### 🏗️ Architecture Overview

Momentum Hub follows a clean, modular architecture designed for maintainability and extensibility:

#### **Core Components:**
- **`momentum_main.py`**: Application entry point and CLI argument parsing
- **`momentum_cli.py`**: Main CLI interface and menu system
- **`momentum_db.py`**: Database operations and data persistence layer
- **`habit.py`**: Core habit model with business logic
- **`goal.py`**: Goal management and progress tracking
- **`category.py`**: Category system for habit organization

#### **CLI Modules:**
- **`cli_habit_management.py`**: Habit CRUD operations
- **`cli_goal_management.py`**: Goal creation and management
- **`cli_category_management.py`**: Category organization
- **`cli_analysis.py`**: Analytics and reporting features
- **`cli_export.py`**: Data export functionality

#### **Supporting Modules:**
- **`habit_analysis.py`**: Advanced analytics calculations
- **`seed_data.py`**: Demo data generation
- **`cli_utils.py`**: Shared CLI utilities and helpers
- **`error_manager.py`**: Centralized error handling

### 🔍 Key Design Patterns

#### **Data Flow:**
```
CLI Input → Validation → Business Logic → Database → Response
```

#### **Error Handling:**
- Centralized error management with user-friendly messages
- Graceful degradation for edge cases
- Comprehensive logging for debugging

#### **Database Design:**
- SQLite with proper indexing for performance
- ACID compliance for data integrity
- Migration-safe schema design

### 📊 Performance Characteristics

- **Startup Time**: < 2 seconds (typical)
- **Database Operations**: Optimized queries with proper indexing
- **Memory Usage**: Minimal footprint suitable for CLI applications
- **Concurrent Access**: SQLite locking handles single-user scenarios

### 🛠️ Customization & Extensibility

#### **Adding New Habit Types:**
1. Extend the `Habit` class in `habit.py`
2. Update frequency validation in `cli_utils.py`
3. Add corresponding CLI handlers

#### **Custom Analytics:**
1. Extend `habit_analysis.py` with new calculation methods
2. Add CLI menu options in `cli_analysis.py`
3. Update display formatting as needed

#### **Database Schema Extensions:**
1. Modify table definitions in `momentum_db.py`
2. Add migration logic for existing databases
3. Update model classes accordingly

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

![Command Line Options](https://github.com/aaronmalunga/momentum-hub/raw/main/diagrams/Screenshots/Main%20py%20menu.png)
*Example of the main menu interface showing available command options.*

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

### 📋 Pull Request Process
1. Ensure all tests pass and coverage remains above 80%
2. Update documentation for any new features
3. Add appropriate type hints
4. Follow commit message conventions
5. Request review from maintainers

### 🐛 Issue Reporting
- Use the issue templates provided
- Include steps to reproduce
- Provide system information (OS, Python version)
- Attach relevant screenshots if applicable

### 💡 Feature Requests
- Check existing issues first
- Provide detailed use cases
- Consider backward compatibility
- Include mockups if proposing UI changes

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/test_habit.py

# Run tests in verbose mode
pytest -v
```

### Test Coverage
The project maintains high test coverage (~85%) across all core modules including:
- Core habit functionality
- Database operations
- CLI interfaces
- Analysis features
- Export functionality

### Code Quality
- **Pre-commit hooks**: Automated code formatting and linting
- **Type hints**: Comprehensive type annotations throughout the codebase
- **PEP 8 compliance**: Consistent code style and formatting

## 🔧 Development Setup

### Prerequisites
- Python 3.10+
- Git
- Virtual environment (recommended)

### Setup Steps
```bash
# Clone repository
git clone https://github.com/yourusername/momentum-hub.git
cd momentum-hub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run initial tests
pytest
```

### Code Formatting
```bash
# Format code with pre-commit
pre-commit run --all-files

# Or manually format
black .
isort .
```

## ⚠️ Limitations and Future Improvements

As a CLI-based habit tracker developed for a school assignment, Momentum Hub has some inherent limitations while providing a solid foundation for habit tracking:

### Current Limitations
- **CLI-Only Interface**: As required for the assignment, the app is command-line only, which may limit accessibility for users preferring graphical interfaces
- **Local Data Storage**: Uses SQLite database stored locally, requiring manual backup and limiting multi-device synchronization
- **Single-User Design**: Built for individual use without multi-user or social features
- **Performance Considerations**: SQLite is suitable for personal use but may require optimizations for very large datasets

### Potential Future Enhancements
- **Web/Mobile Interfaces**: Browser-based or mobile app versions for broader accessibility
- **Cloud Synchronization**: Multi-device data syncing with cloud storage
- **Social Features**: Habit sharing, challenges, and community interactions
- **Advanced Analytics**: AI-powered insights, predictive analytics, and personalized recommendations
- **Gamification**: Achievement systems, streaks rewards, and motivational elements
- **Integrations**: Calendar apps, fitness trackers, and productivity tools

These limitations are acknowledged as part of the assignment constraints and design choices. The app successfully demonstrates comprehensive CLI application development while maintaining excellent code quality and user experience within its scope.

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

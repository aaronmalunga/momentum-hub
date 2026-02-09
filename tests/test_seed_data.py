import os
from unittest.mock import patch

import pytest

import momentum_hub.momentum_db as db
from momentum_hub.seed_data import (
    create_default_categories,
    create_demo_habits,
    create_demo_with_history,
    prompt_for_demo_habits,
)


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_seed.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


class TestCreateDemoHabits:
    def test_create_demo_habits_creates_expected_data(self, tmp_db_path):
        """Test that create_demo_habits creates the expected categories and habits."""
        create_demo_habits(tmp_db_path)

        # Check categories were created
        categories = db.get_all_categories(db_name=tmp_db_path)
        assert len(categories) == 3

        category_names = [cat.name for cat in categories]
        assert "Health & Fitness" in category_names
        assert "Personal Development" in category_names
        assert "Productivity" in category_names

        # Check habits were created
        habits = db.get_all_habits(db_name=tmp_db_path)
        assert len(habits) == 5

        habit_names = [h.name for h in habits]
        assert "Change beddings" in habit_names
        assert "Code" in habit_names
        assert "Study" in habit_names

        # Check goals were created
        goals = db.get_all_goals(db_name=tmp_db_path)
        assert len(goals) == 3

        # Verify habit-category associations
        for habit in habits:
            assert habit.category_id is not None

    def test_create_demo_habits_with_existing_data(self, tmp_db_path):
        """Test that create_demo_habits works even with existing data."""
        # Add some existing data
        from momentum_hub.category import Category
        from momentum_hub.goal import Goal
        from momentum_hub.habit import Habit

        existing_cat = Category(name="Existing", description="Existing category")
        cat_id = db.add_category(existing_cat, tmp_db_path)

        existing_habit = Habit(name="Existing Habit", frequency="daily")
        habit_id = db.add_habit(existing_habit, tmp_db_path)

        # Create demo data
        create_demo_habits(tmp_db_path)

        # Should have existing + demo data
        categories = db.get_all_categories(db_name=tmp_db_path)
        habits = db.get_all_habits(db_name=tmp_db_path)

        assert len(categories) >= 4  # existing + 3 demo
        assert len(habits) >= 4  # existing + 3 demo


class TestPromptForDemoHabits:
    def test_prompt_for_demo_habits_accepts_yes(self):
        """Test that prompt_for_demo_habits returns True when user says yes."""
        with (
            patch("builtins.input", return_value="yes"),
            patch("momentum_hub.seed_data.print"),
        ):
            result = prompt_for_demo_habits()
            assert result is True

    def test_prompt_for_demo_habits_accepts_y(self):
        """Test that prompt_for_demo_habits returns True when user says y."""
        with (
            patch("builtins.input", return_value="y"),
            patch("momentum_hub.seed_data.print"),
        ):
            result = prompt_for_demo_habits()
            assert result is True

    def test_prompt_for_demo_habits_accepts_no(self):
        """Test that prompt_for_demo_habits returns False when user says no."""
        with (
            patch("builtins.input", return_value="no"),
            patch("momentum_hub.seed_data.print"),
        ):
            result = prompt_for_demo_habits()
            assert result is False

    def test_prompt_for_demo_habits_accepts_n(self):
        """Test that prompt_for_demo_habits returns False when user says n."""
        with (
            patch("builtins.input", return_value="n"),
            patch("momentum_hub.seed_data.print"),
        ):
            result = prompt_for_demo_habits()
            assert result is False

    def test_prompt_for_demo_habits_handles_invalid_input(self):
        """Test that prompt_for_demo_habits handles invalid input and retries."""
        with (
            patch("builtins.input", side_effect=["invalid", "yes"]),
            patch("momentum_hub.seed_data.print"),
        ):
            result = prompt_for_demo_habits()
            assert result is True


class TestCreateDefaultCategories:
    def test_create_default_categories_creates_expected_data(self, tmp_db_path):
        """Test that create_default_categories creates the expected categories."""
        create_default_categories(tmp_db_path)

        # Check categories were created
        categories = db.get_all_categories(db_name=tmp_db_path)
        assert len(categories) == 8

        category_names = [cat.name for cat in categories]
        expected_names = [
            "Health & Fitness",
            "Personal Development",
            "Productivity",
            "Mindfulness & Wellness",
            "Social & Relationships",
            "Finance & Money",
            "Creativity & Hobbies",
            "Home & Environment",
        ]
        for name in expected_names:
            assert name in category_names

        # Verify category details
        for cat in categories:
            assert cat.is_active is True
            assert cat.created_at is not None
            if cat.name == "Health & Fitness":
                assert (
                    cat.description == "Habits related to physical health and exercise"
                )
                assert cat.color == "#FF6B6B"
            elif cat.name == "Personal Development":
                assert cat.description == "Habits for learning and self-improvement"
                assert cat.color == "#4ECDC4"
            elif cat.name == "Productivity":
                assert (
                    cat.description == "Habits to improve efficiency and organization"
                )
                assert cat.color == "#45B7D1"
            elif cat.name == "Mindfulness & Wellness":
                assert cat.description == "Habits for mental health and relaxation"
                assert cat.color == "#96CEB4"
            elif cat.name == "Social & Relationships":
                assert (
                    cat.description
                    == "Habits for building and maintaining relationships"
                )
                assert cat.color == "#FFEAA7"
            elif cat.name == "Finance & Money":
                assert cat.description == "Habits for financial planning and management"
                assert cat.color == "#DDA0DD"
            elif cat.name == "Creativity & Hobbies":
                assert (
                    cat.description
                    == "Habits for creative expression and leisure activities"
                )
                assert cat.color == "#98D8C8"
            elif cat.name == "Home & Environment":
                assert (
                    cat.description
                    == "Habits for maintaining home and environmental care"
                )
                assert cat.color == "#F7DC6F"

    def test_create_default_categories_with_existing_data(self, tmp_db_path):
        """Test that create_default_categories works even with existing data."""
        # Add some existing data
        from momentum_hub.category import Category

        existing_cat = Category(name="Existing", description="Existing category")
        cat_id = db.add_category(existing_cat, tmp_db_path)

        # Create default categories
        create_default_categories(tmp_db_path)

        # Should have existing + default data
        categories = db.get_all_categories(db_name=tmp_db_path)
        assert len(categories) == 9  # existing + 8 default


class TestCreateDemoWithHistory:
    def test_create_demo_with_history_creates_expected_data(self, tmp_db_path):
        """Test that create_demo_with_history creates demo data with history."""
        create_demo_with_history(tmp_db_path)

        # Check categories were created
        categories = db.get_all_categories(db_name=tmp_db_path)
        assert len(categories) == 3

        # Check habits were created
        habits = db.get_all_habits(db_name=tmp_db_path)
        assert len(habits) == 5

        # Check that completions were added
        total_completions = 0
        for habit in habits:
            completions = db.get_completions(habit.id, db_name=tmp_db_path)
            total_completions += len(completions)

        # Should have at least one completion per habit (5 total)
        assert total_completions == 5

        # Check that streaks were updated
        for habit in habits:
            assert habit.streak == 1  # Each habit should have a streak of 1

    def test_create_demo_with_history_with_existing_data(self, tmp_db_path):
        """Test that create_demo_with_history works with existing data."""
        # Add some existing data
        from momentum_hub.category import Category
        from momentum_hub.habit import Habit

        # Pre-create one of the demo categories
        existing_cat = Category(
            name="Health & Fitness",
            description="Existing health category",
            color="#FF0000",
        )
        cat_id = db.add_category(existing_cat, tmp_db_path)

        existing_habit = Habit(name="Existing Habit", frequency="daily")
        habit_id = db.add_habit(existing_habit, tmp_db_path)

        # Create demo data with history
        create_demo_with_history(tmp_db_path)

        # Should have existing + demo data
        habits = db.get_all_habits(db_name=tmp_db_path)
        assert len(habits) >= 6  # existing + 5 demo

        # Check completions for demo habits (not existing)
        demo_habits = [h for h in habits if h.name != "Existing Habit"]
        total_completions = 0
        for habit in demo_habits:
            completions = db.get_completions(habit.id, db_name=tmp_db_path)
            total_completions += len(completions)

        assert total_completions == 5  # One completion per demo habit

    @patch("momentum_hub.seed_data.db.add_completion")
    @patch("momentum_hub.seed_data.db.update_streak")
    def test_create_demo_with_history_completion_failure(
        self, mock_update_streak, mock_add_completion, tmp_db_path
    ):
        """Test that create_demo_with_history handles completion failures gracefully."""
        # Mock add_completion to fail for the first call, succeed for others
        mock_add_completion.side_effect = [
            Exception("Duplicate completion"),
            None,
            None,
            None,
            None,
        ]

        create_demo_with_history(tmp_db_path)

        # Should have called add_completion 5 times (once per habit)
        assert mock_add_completion.call_count == 5

        # Should have called update_streak 4 times (for successful completions)
        assert mock_update_streak.call_count == 4


class TestMainBlock:
    def test_main_block_creates_test_database(self, tmp_path):
        """Test the main block creates and populates a test database."""
        test_db = tmp_path / "test_main.db"
        db_name = str(test_db)

        # Run the main block logic
        if os.path.exists(db_name):
            os.remove(db_name)

        db.init_db(db_name)
        create_demo_habits(db_name)

        # Verify data was created
        habits = db.get_all_habits(db_name=db_name)
        categories = db.get_all_categories(db_name=db_name)

        assert len(habits) == 5
        assert len(categories) == 3

        # Cleanup
        db.close_all_connections()
        if os.path.exists(db_name):
            os.remove(db_name)

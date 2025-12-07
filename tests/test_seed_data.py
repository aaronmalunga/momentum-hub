import os
from unittest.mock import patch

import pytest

import momentum_db as db
from seed_data import (
    create_default_categories,
    create_demo_habits,
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
        from category import Category
        from goal import Goal
        from habit import Habit

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
        with patch("builtins.input", return_value="yes"), patch("seed_data.print"):
            result = prompt_for_demo_habits()
            assert result is True

    def test_prompt_for_demo_habits_accepts_y(self):
        """Test that prompt_for_demo_habits returns True when user says y."""
        with patch("builtins.input", return_value="y"), patch("seed_data.print"):
            result = prompt_for_demo_habits()
            assert result is True

    def test_prompt_for_demo_habits_accepts_no(self):
        """Test that prompt_for_demo_habits returns False when user says no."""
        with patch("builtins.input", return_value="no"), patch("seed_data.print"):
            result = prompt_for_demo_habits()
            assert result is False

    def test_prompt_for_demo_habits_accepts_n(self):
        """Test that prompt_for_demo_habits returns False when user says n."""
        with patch("builtins.input", return_value="n"), patch("seed_data.print"):
            result = prompt_for_demo_habits()
            assert result is False

    def test_prompt_for_demo_habits_handles_invalid_input(self):
        """Test that prompt_for_demo_habits handles invalid input and retries."""
        with (
            patch("builtins.input", side_effect=["invalid", "yes"]),
            patch("seed_data.print"),
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
        from category import Category

        existing_cat = Category(name="Existing", description="Existing category")
        cat_id = db.add_category(existing_cat, tmp_db_path)

        # Create default categories
        create_default_categories(tmp_db_path)

        # Should have existing + default data
        categories = db.get_all_categories(db_name=tmp_db_path)
        assert len(categories) == 9  # existing + 8 default


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

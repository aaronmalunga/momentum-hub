from unittest.mock import MagicMock, patch

import pytest

import momentum_hub.momentum_db as db
from momentum_hub.category import Category
from momentum_hub.cli_category_management import (
    assign_habit_to_category,
    create_category,
    delete_category,
    manage_categories,
    update_category,
    view_categories,
)
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_cli_category.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def sample_data(tmp_db_path):
    # Create sample categories
    cat1 = Category(name="Health", description="Health habits", color="#FF0000")
    cat2 = Category(name="Productivity", description="Work habits", color="#00FF00")
    cat_id1 = db.add_category(cat1, tmp_db_path)
    cat_id2 = db.add_category(cat2, tmp_db_path)

    # Create sample habits
    h1 = Habit(name="Exercise", frequency="daily")
    h2 = Habit(name="Read", frequency="daily")
    hid1 = db.add_habit(h1, tmp_db_path)
    hid2 = db.add_habit(h2, tmp_db_path)

    return tmp_db_path, cat_id1, cat_id2, hid1, hid2


class TestCreateCategory:
    def test_create_category_success(self, tmp_db_path):
        with (
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_text.side_effect = lambda *args, **kwargs: MagicMock(
                ask=MagicMock(
                    return_value=["Test Category", "Test Description", "#FF5733"][
                        mock_text.call_count - 1
                    ]
                )
            )

            create_category(tmp_db_path)

            categories = db.get_all_categories(db_name=tmp_db_path)
            assert len(categories) == 1
            assert categories[0].name == "Test Category"
            assert categories[0].description == "Test Description"
            assert categories[0].color == "#FF5733"

    def test_create_category_cancel_name(self, tmp_db_path):
        with (
            patch("questionary.text") as mock_text,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_text.return_value = MagicMock(ask=MagicMock(return_value=None))

            create_category(tmp_db_path)

            mock_show.assert_called_with(
                "Category creation cancelled.", color="\x1b[33m"
            )

    def test_create_category_empty_name(self, tmp_db_path):
        with (
            patch("questionary.text") as mock_text,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                return MagicMock(
                    ask=MagicMock(
                        return_value=[
                            "",
                            "Test Category",
                            "Test Description",
                            "#FF5733",
                        ][call_count - 1]
                    )
                )

            mock_text.side_effect = side_effect

            create_category(tmp_db_path)

            categories = db.get_all_categories(db_name=tmp_db_path)
            assert len(categories) == 1
            # Check that the error message was called for the empty name
            mock_show.assert_any_call(
                "Category name cannot be empty.", color="\x1b[31m"
            )
            # And that the success message was called
            mock_show.assert_any_call(
                "Category 'Test Category' created successfully with ID: 1",
                color="\x1b[32m",
                style="\x1b[1m",
            )


class TestViewCategories:
    def test_view_categories_with_data(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
            patch("builtins.print"),
        ):

            view_categories(tmp_db_path)

    def test_view_categories_empty(self, tmp_db_path):
        with (
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            view_categories(tmp_db_path)

            mock_show.assert_called_with(
                "No active categories found.", color="\x1b[31m"
            )


class TestUpdateCategory:
    def test_update_category_success(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                return MagicMock(
                    ask=MagicMock(
                        return_value=[
                            "Updated Health",
                            "Updated Description",
                            "#0000FF",
                        ][call_count - 1]
                    )
                )

            mock_text.side_effect = side_effect

            update_category(tmp_db_path)

            category = db.get_category(cat_id1, tmp_db_path)
            assert category.name == "Updated Health"
            assert category.description == "Updated Description"
            assert category.color == "#0000FF"

    def test_update_category_cancel(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(ask=MagicMock(return_value="Cancel"))

            update_category(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")

    def test_update_category_no_categories(self, tmp_db_path):
        with (
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            update_category(tmp_db_path)

            mock_show.assert_called_with(
                "No active categories found to update.", color="\x1b[31m"
            )

    def test_update_category_invalid_selection(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="invalid. selection")
            )

            update_category(tmp_db_path)

            mock_show.assert_called_with("Invalid selection.", color="\x1b[31m")

    def test_update_category_cancel_name(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            mock_text.return_value = MagicMock(ask=MagicMock(return_value=None))

            update_category(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")

    def test_update_category_cancel_description(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return MagicMock(ask=MagicMock(return_value="Updated Name"))
                else:
                    return MagicMock(ask=MagicMock(return_value=None))

            mock_text.side_effect = side_effect

            update_category(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")

    def test_update_category_cancel_color(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return MagicMock(ask=MagicMock(return_value="Updated Name"))
                elif call_count == 2:
                    return MagicMock(ask=MagicMock(return_value="Updated Description"))
                else:
                    return MagicMock(ask=MagicMock(return_value=None))

            mock_text.side_effect = side_effect

            update_category(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")


class TestDeleteCategory:
    def test_delete_category_success(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            mock_confirm.return_value = MagicMock(ask=MagicMock(return_value=True))

            delete_category(tmp_db_path)

            category = db.get_category(cat_id1, tmp_db_path)
            assert category is None or not category.is_active

    def test_delete_category_with_habits(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        # Assign habit to category
        habit = db.get_habit(hid1, tmp_db_path)
        habit.category_id = cat_id1
        db.update_habit(habit, tmp_db_path)

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            mock_confirm.return_value = MagicMock(ask=MagicMock(return_value=True))

            delete_category(tmp_db_path)

            # Check habit was removed from category
            updated_habit = db.get_habit(hid1, tmp_db_path)
            assert updated_habit.category_id is None

    def test_delete_category_cancel(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )
            mock_confirm.return_value = MagicMock(ask=MagicMock(return_value=False))

            delete_category(tmp_db_path)

            mock_show.assert_called_with("Deletion cancelled.", color="\x1b[33m")

    def test_delete_category_cancel_selection(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(ask=MagicMock(return_value="Cancel"))

            delete_category(tmp_db_path)

            mock_show.assert_called_with("Deletion cancelled.", color="\x1b[33m")

    def test_delete_category_invalid_selection(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="invalid. selection")
            )

            delete_category(tmp_db_path)

            mock_show.assert_called_with("Invalid selection.", color="\x1b[31m")


class TestAssignHabitToCategory:
    def test_assign_habit_to_category_success(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch(
                "momentum_hub.cli_category_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.select") as mock_select,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid1, tmp_db_path)
            mock_handle.return_value = habit
            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value=f"{cat_id1}. Health")
            )

            assign_habit_to_category(tmp_db_path)

            updated_habit = db.get_habit(hid1, tmp_db_path)
            assert updated_habit.category_id == cat_id1

    def test_assign_habit_remove_from_category(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        # First assign habit to category
        habit = db.get_habit(hid1, tmp_db_path)
        habit.category_id = cat_id1
        db.update_habit(habit, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_category_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.select") as mock_select,
            patch("momentum_hub.cli_category_management.show_colored_message"),
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_handle.return_value = habit
            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Remove from category")
            )

            assign_habit_to_category(tmp_db_path)

            updated_habit = db.get_habit(hid1, tmp_db_path)
            assert updated_habit.category_id is None

    def test_assign_habit_no_habits(self, tmp_db_path):
        with (
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            assign_habit_to_category(tmp_db_path)

            mock_show.assert_called_with("No active habits found.", color="\x1b[31m")

    def test_assign_habit_no_categories(self, tmp_db_path):
        # Create a habit but no categories
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)
        habit = db.get_habit(hid, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_category_management._handle_habit_selection"
            ) as mock_handle,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            mock_handle.return_value = habit

            assign_habit_to_category(tmp_db_path)

            mock_show.assert_called_with(
                "No active categories found. Create a category first!", color="\x1b[31m"
            )

    def test_assign_habit_cancel_selection(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch(
                "momentum_hub.cli_category_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid1, tmp_db_path)
            mock_handle.return_value = habit
            mock_select.return_value = MagicMock(ask=MagicMock(return_value="Cancel"))

            assign_habit_to_category(tmp_db_path)

            mock_show.assert_called_with("Assignment cancelled.", color="\x1b[33m")

    def test_assign_habit_invalid_selection(self, sample_data):
        tmp_db_path, cat_id1, cat_id2, hid1, hid2 = sample_data

        with (
            patch(
                "momentum_hub.cli_category_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.show_colored_message"
            ) as mock_show,
            patch("momentum_hub.cli_category_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid1, tmp_db_path)
            mock_handle.return_value = habit
            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="invalid. selection")
            )

            assign_habit_to_category(tmp_db_path)

            mock_show.assert_called_with("Invalid selection.", color="\x1b[31m")


class TestManageCategories:
    def test_manage_categories_create(self, tmp_db_path):
        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.CategoryManager.create_category"
            ) as mock_create,
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Create a new category")
            )

            manage_categories(tmp_db_path)

            mock_create.assert_called_once_with()

    def test_manage_categories_view(self, tmp_db_path):
        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.CategoryManager.view_categories"
            ) as mock_view,
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="View all categories")
            )

            manage_categories(tmp_db_path)

            mock_view.assert_called_once_with()

    def test_manage_categories_update(self, tmp_db_path):
        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.CategoryManager.update_category"
            ) as mock_update,
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Update a category")
            )

            manage_categories(tmp_db_path)

            mock_update.assert_called_once_with()

    def test_manage_categories_delete(self, tmp_db_path):
        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.CategoryManager.delete_category"
            ) as mock_delete,
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Delete a category")
            )

            manage_categories(tmp_db_path)

            mock_delete.assert_called_once_with()

    def test_manage_categories_assign(self, tmp_db_path):
        with (
            patch("questionary.select") as mock_select,
            patch(
                "momentum_hub.cli_category_management.CategoryManager.assign_habit_to_category"
            ) as mock_assign,
        ):

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Assign habit to category")
            )

            manage_categories(tmp_db_path)

            mock_assign.assert_called_once_with()

    def test_manage_categories_back(self, tmp_db_path):
        with patch("questionary.select") as mock_select:

            mock_select.return_value = MagicMock(
                ask=MagicMock(return_value="Back to Main Menu")
            )

            manage_categories(tmp_db_path)

            # Should not raise any exceptions

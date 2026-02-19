import datetime
from unittest.mock import MagicMock, patch

import pytest

import momentum_hub.momentum_db as db
from momentum_hub.cli_habit_management import (
    create_new_habit,
    delete_habit,
    mark_habit_completed,
    reactivate_habit,
    update_habit,
)
from momentum_hub.habit import Habit


class TestCreateNewHabit:
    """Tests CLI: create habit flow."""

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.add_habit")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.db.get_category")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_success(
        self,
        mock_press,
        mock_show,
        mock_get_cat,
        mock_update,
        mock_get_cats,
        mock_add,
        mock_select,
        mock_text,
    ):
        # Mock inputs
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(ask=MagicMock(return_value="20:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="daily")),
            MagicMock(ask=MagicMock(return_value="1. Test Category")),
        ]
        mock_get_cats.return_value = [MagicMock(id=1, name="Test Category")]
        mock_add.return_value = 1
        mock_get_cat.return_value = MagicMock(name="Test Category")

        create_new_habit("test.db")

        # Verify habit creation
        mock_add.assert_called_once()
        habit_arg = mock_add.call_args[0][0]
        assert habit_arg.name == "Test Habit"
        assert habit_arg.frequency == "daily"
        assert habit_arg.notes == "Some notes"
        assert habit_arg.reminder_time == "08:00"
        assert habit_arg.evening_reminder_time == "20:00"

        # Verify category update
        mock_update.assert_called_once()

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.add_habit")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_no_category(
        self, mock_press, mock_show, mock_get_cats, mock_add, mock_select, mock_text
    ):
        # Mock inputs
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(ask=MagicMock(return_value="20:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="daily")),
            MagicMock(ask=MagicMock(return_value="No category")),
        ]
        mock_get_cats.return_value = [MagicMock(id=1, name="Test Category")]
        mock_add.return_value = 1

        create_new_habit("test.db")

        # Verify habit creation without category
        mock_add.assert_called_once()
        habit_arg = mock_add.call_args[0][0]
        assert habit_arg.name == "Test Habit"
        assert habit_arg.frequency == "daily"

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_cancel_name(self, mock_press, mock_show, mock_text):
        mock_text.return_value = MagicMock(ask=MagicMock(return_value=None))

        create_new_habit("test.db")

        mock_show.assert_called_with("Habit creation cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_empty_name(self, mock_press, mock_show, mock_text):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="")),
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(ask=MagicMock(return_value="20:00")),
        ]
        with patch(
            "momentum_hub.cli_habit_management.questionary.select"
        ) as mock_select:
            mock_select.side_effect = [
                MagicMock(ask=MagicMock(return_value="daily")),
                MagicMock(ask=MagicMock(return_value="No category")),
            ]

            create_new_habit("test.db")

            # Should show error for empty name and continue
            mock_show.assert_any_call("Habit name cannot be empty.", color="\x1b[31m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_cancel_frequency(
        self, mock_press, mock_show, mock_select, mock_text
    ):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
        ]
        mock_select.return_value = MagicMock(ask=MagicMock(return_value=None))

        create_new_habit("test.db")

        mock_show.assert_called_with("Habit creation cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_cancel_notes(
        self, mock_press, mock_show, mock_select, mock_text
    ):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value=None)),  # Cancel at notes
        ]
        mock_select.return_value = MagicMock(ask=MagicMock(return_value="daily"))

        create_new_habit("test.db")

        mock_show.assert_called_with("Habit creation cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_cancel_reminder_time(
        self, mock_press, mock_show, mock_select, mock_text
    ):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value=None)),  # Cancel at reminder_time
        ]
        mock_select.return_value = MagicMock(ask=MagicMock(return_value="daily"))

        create_new_habit("test.db")

        mock_show.assert_called_with("Habit creation cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_cancel_evening_reminder_time(
        self, mock_press, mock_show, mock_select, mock_text
    ):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(
                ask=MagicMock(return_value=None)
            ),  # Cancel at evening_reminder_time
        ]
        mock_select.return_value = MagicMock(ask=MagicMock(return_value="daily"))

        create_new_habit("test.db")

        mock_show.assert_called_with("Habit creation cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.add_habit")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_no_category(
        self, mock_press, mock_show, mock_get_cats, mock_add, mock_select, mock_text
    ):
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(ask=MagicMock(return_value="20:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="daily")),
            MagicMock(ask=MagicMock(return_value="No category")),
        ]
        mock_get_cats.return_value = [MagicMock(id=1, name="Test Category")]
        mock_add.return_value = 1

        create_new_habit("test.db")

        # Verify no category update
        with patch("momentum_hub.cli_habit_management.db.update_habit") as mock_update:
            mock_update.assert_not_called()

    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.add_habit")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_create_new_habit_invalid_category_choice(
        self,
        mock_press,
        mock_show,
        mock_get_cats,
        mock_add,
        mock_select,
        mock_text,
    ):
        # Mock inputs
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="Test Habit")),
            MagicMock(ask=MagicMock(return_value="Some notes")),
            MagicMock(ask=MagicMock(return_value="08:00")),
            MagicMock(ask=MagicMock(return_value="20:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="daily")),
            MagicMock(
                ask=MagicMock(return_value="invalid.category.choice")
            ),  # Invalid choice
        ]
        mock_get_cats.return_value = [MagicMock(id=1, name="Test Category")]
        mock_add.return_value = 1

        create_new_habit("test.db")

        # Verify habit was created with category_id=None due to parsing failure
        mock_add.assert_called_once()
        args, kwargs = mock_add.call_args
        habit = args[0]
        assert habit.category_id is None


class TestMarkHabitCompleted:
    """Tests CLI: mark habit as completed."""

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.db.add_completion")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.db.update_streak")
    @patch("momentum_hub.cli_habit_management.db.get_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    @patch("momentum_hub.cli_habit_management.get_completion_encouragement")
    def test_mark_habit_completed_success(
        self,
        mock_enc,
        mock_press,
        mock_show,
        mock_get_habit,
        mock_update_streak,
        mock_update_habit,
        mock_add_comp,
        mock_select,
        mock_get_habits,
    ):
        habit = MagicMock()
        habit.id = 1
        habit.name = "Test Habit"
        habit.frequency = "daily"
        habit.streak = 6
        mock_get_habits.return_value = [habit]
        mock_select.return_value = habit
        mock_get_habit.return_value = MagicMock(streak=7)
        mock_enc.return_value = "Great job!"

        mark_habit_completed("test.db")

        mock_add_comp.assert_called_once()
        mock_update_habit.assert_called_once()
        mock_update_streak.assert_called_once()
        mock_show.assert_any_call(
            "'Test Habit' marked as completed! Current streak: 7",
            color="\x1b[32m",
            style="\x1b[1m",
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_mark_habit_completed_no_habits(
        self, mock_press, mock_show, mock_select, mock_get_habits
    ):
        mock_get_habits.return_value = []
        mock_select.return_value = None

        mark_habit_completed("test.db")

        # Should show header message but not proceed further
        mock_show.assert_called_once_with(
            "\n--- Mark Habit as Completed ---", color="\x1b[33m", style="\x1b[1m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.db.add_completion")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.db.update_streak")
    @patch("momentum_hub.cli_habit_management.db.get_habit")
    @patch("momentum_hub.cli_habit_management.get_completion_encouragement")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_mark_habit_completed_database_error(
        self,
        mock_press,
        mock_show,
        mock_enc,
        mock_get_habit,
        mock_update_streak,
        mock_update_habit,
        mock_add_comp,
        mock_select,
        mock_get_habits,
    ):
        habit = MagicMock()
        habit.id = 1
        habit.name = "Test Habit"
        habit.frequency = "daily"
        habit.streak = 6
        mock_get_habits.return_value = [habit]
        mock_select.return_value = habit
        mock_get_habit.return_value = MagicMock(streak=7)
        mock_enc.return_value = "Great job!"
        # Simulate database error
        mock_add_comp.side_effect = ValueError("Database error")

        mark_habit_completed("test.db")

        # Should show error message
        mock_show.assert_any_call(
            "Cannot mark 'Test Habit' as completed: Database error",
            color="\x1b[31m",
            style="\x1b[1m",
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.db.add_completion")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.db.update_streak")
    @patch("momentum_hub.cli_habit_management.db.get_habit")
    @patch("momentum_hub.cli_habit_management.get_completion_encouragement")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_mark_habit_completed_with_encouragement(
        self,
        mock_press,
        mock_show,
        mock_enc,
        mock_get_habit,
        mock_update_streak,
        mock_update_habit,
        mock_add_comp,
        mock_select,
        mock_get_habits,
    ):
        habit = MagicMock()
        habit.id = 1
        habit.name = "Test Habit"
        habit.frequency = "daily"
        habit.streak = 6
        mock_get_habits.return_value = [habit]
        mock_select.return_value = habit
        mock_get_habit.return_value = MagicMock(streak=7)
        mock_enc.return_value = "Great job!"

        mark_habit_completed("test.db")

        mock_add_comp.assert_called_once()
        mock_update_habit.assert_called_once()
        mock_update_streak.assert_called_once()
        # Should show encouragement message
        mock_show.assert_any_call("Great job!", color="\x1b[36m", style="\x1b[1m")


class TestDeleteHabit:
    """Tests CLI: delete habit flow."""

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.confirm")
    @patch("momentum_hub.cli_habit_management.db.delete_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_success(
        self,
        mock_press,
        mock_show,
        mock_delete,
        mock_confirm,
        mock_select,
        mock_get_habits,
    ):
        habit = MagicMock()
        habit.id = 1
        habit.name = "Test Habit"
        mock_get_habits.return_value = [habit]
        mock_select.return_value = habit
        mock_confirm.return_value = MagicMock(ask=MagicMock(return_value=True))

        delete_habit("test.db")

        mock_delete.assert_called_once_with(1, "test.db")
        mock_show.assert_any_call(
            "Habit 'Test Habit' deleted (deactivated) successfully!", color="\x1b[32m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_no_habits(self, mock_press, mock_show, mock_get_habits):
        mock_get_habits.return_value = []

        delete_habit("test.db")

        mock_show.assert_called_with(
            "No active habits found to delete.", color="\x1b[31m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.confirm")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_cancel_confirm(
        self, mock_press, mock_show, mock_confirm, mock_select, mock_get_habits
    ):
        habit = MagicMock(id=1, name="Test Habit")
        mock_get_habits.return_value = [habit]
        mock_select.return_value = habit
        mock_confirm.return_value = MagicMock(ask=MagicMock(return_value=False))

        delete_habit("test.db")

        delete_habit("test.db")

        mock_show.assert_any_call("Deletion cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_delete_habit_cancel_selection(
        self, mock_press, mock_show, mock_select, mock_get_habits
    ):
        mock_get_habits.return_value = [MagicMock(id=1, name="Test Habit")]
        mock_select.return_value = None  # User cancels habit selection

        delete_habit("test.db")

        # Should not proceed with deletion
        mock_show.assert_called_once_with(
            "\n--- Delete Habit ---", color="\x1b[33m", style="\x1b[1m"
        )


class TestReactivateHabit:
    """Tests CLI: reactivate habit flow."""

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.reactivate_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_reactivate_habit_success(
        self, mock_press, mock_show, mock_reactivate, mock_select, mock_get_habits
    ):
        habit = MagicMock()
        habit.id = 1
        habit.name = "Test Habit"
        habit.frequency = "daily"
        habit.is_active = False
        mock_get_habits.return_value = [habit]
        mock_select.return_value = MagicMock(
            ask=MagicMock(return_value="1. Test Habit (daily)")
        )

        reactivate_habit("test.db")

        mock_reactivate.assert_called_once_with(1, "test.db")
        mock_show.assert_any_call(
            "Habit 'Test Habit' reactivated successfully!", color="\x1b[32m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_reactivate_habit_no_deleted_habits(
        self, mock_press, mock_show, mock_get_habits
    ):
        mock_get_habits.return_value = []

        reactivate_habit("test.db")

        mock_show.assert_called_with(
            "No deleted habits found to reactivate.", color="\x1b[31m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_reactivate_habit_cancel(
        self, mock_press, mock_show, mock_select, mock_get_habits
    ):
        habit = MagicMock(id=1, name="Test Habit", frequency="daily", is_active=False)
        mock_get_habits.return_value = [habit]
        mock_select.return_value = MagicMock(ask=MagicMock(return_value="Cancel"))

        reactivate_habit("test.db")

        mock_show.assert_called_with("Reactivation cancelled.", color="\x1b[33m")


class TestUpdateHabit:
    """Tests CLI: update habit flow."""

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.get_category")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_success(
        self,
        mock_press,
        mock_show,
        mock_update,
        mock_get_cat,
        mock_get_cats,
        mock_select,
        mock_text,
        mock_handle,
        mock_get_habits,
    ):
        habit = MagicMock(
            id=1,
            name="Old Name",
            frequency="daily",
            notes="Old notes",
            reminder_time="07:00",
            evening_reminder_time="19:00",
            category_id=None,
        )
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="New Name")),
            MagicMock(ask=MagicMock(return_value="New notes")),
            MagicMock(ask=MagicMock(return_value="09:00")),
            MagicMock(ask=MagicMock(return_value="21:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="weekly")),
            MagicMock(ask=MagicMock(return_value="No category")),
        ]
        mock_get_cats.return_value = []

        update_habit("test.db")

        # Verify edit_habit was called with new values
        habit.edit_habit.assert_called_once_with(
            name="New Name",
            frequency="weekly",
            notes="New notes",
            reminder_time="09:00",
            evening_reminder_time="21:00",
        )
        mock_update.assert_called_once_with(habit, "test.db")

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_no_habits(
        self, mock_press, mock_show, mock_handle, mock_get_habits
    ):
        mock_get_habits.return_value = []
        mock_handle.return_value = None

        update_habit("test.db")

        mock_show.assert_called_with(
            "No active habits found. Let's create one!", color="\x1b[31m"
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_cancel_name(
        self, mock_press, mock_show, mock_text, mock_handle, mock_get_habits
    ):
        habit = MagicMock(id=1, name="Test Habit")
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.return_value = MagicMock(ask=MagicMock(return_value=None))

        update_habit("test.db")

        mock_show.assert_any_call("Update cancelled.", color="\x1b[33m")

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_empty_reminder_time(
        self,
        mock_press,
        mock_show,
        mock_update,
        mock_get_cats,
        mock_text,
        mock_select,
        mock_handle,
        mock_get_habits,
    ):
        habit = MagicMock(
            id=1,
            name="Test Habit",
            frequency="daily",
            notes="Notes",
            reminder_time="08:00",
            evening_reminder_time="20:00",
            category_id=None,
            edit_habit=MagicMock(),
        )
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="New Name")),
            MagicMock(ask=MagicMock(return_value="New notes")),
            MagicMock(ask=MagicMock(return_value="")),  # Empty reminder_time
            MagicMock(ask=MagicMock(return_value="21:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="weekly")),
            MagicMock(ask=MagicMock(return_value="No category")),
        ]
        mock_get_cats.return_value = []

        update_habit("test.db")

        # Verify edit_habit was called with reminder_time=None
        habit.edit_habit.assert_called_once_with(
            name="New Name",
            frequency="weekly",
            notes="New notes",
            reminder_time=None,
            evening_reminder_time="21:00",
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_empty_evening_reminder_time(
        self,
        mock_press,
        mock_show,
        mock_update,
        mock_get_cats,
        mock_text,
        mock_select,
        mock_handle,
        mock_get_habits,
    ):
        habit = MagicMock(
            id=1,
            name="Test Habit",
            frequency="daily",
            notes="Notes",
            reminder_time="08:00",
            evening_reminder_time="20:00",
            category_id=None,
            edit_habit=MagicMock(),
        )
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="New Name")),
            MagicMock(ask=MagicMock(return_value="New notes")),
            MagicMock(ask=MagicMock(return_value="09:00")),
            MagicMock(ask=MagicMock(return_value="")),  # Empty evening_reminder_time
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="weekly")),
            MagicMock(ask=MagicMock(return_value="No category")),
        ]
        mock_get_cats.return_value = []

        update_habit("test.db")

        # Verify edit_habit was called with evening_reminder_time=None
        habit.edit_habit.assert_called_once_with(
            name="New Name",
            frequency="weekly",
            notes="New notes",
            reminder_time="09:00",
            evening_reminder_time=None,
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.get_category")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_keep_current_category(
        self,
        mock_press,
        mock_show,
        mock_update,
        mock_get_cat,
        mock_get_cats,
        mock_text,
        mock_select,
        mock_handle,
        mock_get_habits,
    ):
        habit = MagicMock(
            id=1,
            name="Test Habit",
            frequency="daily",
            notes="Notes",
            reminder_time="08:00",
            evening_reminder_time="20:00",
            category_id=1,
            edit_habit=MagicMock(),
        )
        category = MagicMock(id=1, name="Test Category")
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="New Name")),
            MagicMock(ask=MagicMock(return_value="New notes")),
            MagicMock(ask=MagicMock(return_value="09:00")),
            MagicMock(ask=MagicMock(return_value="21:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="weekly")),
            MagicMock(ask=MagicMock(return_value=f"Keep current ({category.name})")),
        ]
        mock_get_cats.return_value = [category]
        mock_get_cat.return_value = category

        update_habit("test.db")

        # Verify category_id remains unchanged
        assert habit.category_id == 1
        habit.edit_habit.assert_called_once_with(
            name="New Name",
            frequency="weekly",
            notes="New notes",
            reminder_time="09:00",
            evening_reminder_time="21:00",
        )

    @patch("momentum_hub.cli_habit_management.db.get_all_habits")
    @patch("momentum_hub.cli_habit_management._handle_habit_selection")
    @patch("momentum_hub.cli_habit_management.questionary.select")
    @patch("momentum_hub.cli_habit_management.questionary.text")
    @patch("momentum_hub.cli_habit_management.db.get_all_categories")
    @patch("momentum_hub.cli_habit_management.db.update_habit")
    @patch("momentum_hub.cli_habit_management.show_colored_message")
    @patch("momentum_hub.cli_habit_management.press_enter_to_continue")
    def test_update_habit_invalid_category_choice(
        self,
        mock_press,
        mock_show,
        mock_update,
        mock_get_cats,
        mock_text,
        mock_select,
        mock_handle,
        mock_get_habits,
    ):
        habit = MagicMock(
            id=1,
            name="Test Habit",
            frequency="daily",
            notes="Notes",
            reminder_time="08:00",
            evening_reminder_time="20:00",
            category_id=None,
            edit_habit=MagicMock(),
        )
        mock_get_habits.return_value = [habit]
        mock_handle.return_value = habit
        mock_text.side_effect = [
            MagicMock(ask=MagicMock(return_value="New Name")),
            MagicMock(ask=MagicMock(return_value="New notes")),
            MagicMock(ask=MagicMock(return_value="09:00")),
            MagicMock(ask=MagicMock(return_value="21:00")),
        ]
        mock_select.side_effect = [
            MagicMock(ask=MagicMock(return_value="weekly")),
            MagicMock(
                ask=MagicMock(return_value="invalid.category.choice")
            ),  # Invalid choice
        ]
        mock_get_cats.return_value = []

        update_habit("test.db")

        # Verify category_id remains None due to parsing failure
        assert habit.category_id is None
        habit.edit_habit.assert_called_once_with(
            name="New Name",
            frequency="weekly",
            notes="New notes",
            reminder_time="09:00",
            evening_reminder_time="21:00",
        )

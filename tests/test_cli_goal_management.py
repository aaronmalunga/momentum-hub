import datetime
from unittest.mock import MagicMock, patch

import pytest

import momentum_hub.momentum_db as db
from momentum_hub.cli_goal_management import (
    create_goal,
    delete_goal,
    manage_goals,
    update_goal,
    view_goals,
)
from momentum_hub.goal import Goal
from momentum_hub.habit import Habit


@pytest.fixture
def tmp_db_path(tmp_path):
    db_file = tmp_path / "test_cli_goal.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name


@pytest.fixture
def sample_data(tmp_db_path):
    # Create sample habit
    h = Habit(name="Test Habit", frequency="daily")
    hid = db.add_habit(h, tmp_db_path)

    # Create sample goal
    goal = Goal(habit_id=hid, target_period_days=28, target_completions=25)
    goal_id = db.add_goal(goal, tmp_db_path)

    return tmp_db_path, hid, goal_id


class TestCreateGoal:
    def test_create_goal_success(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="30")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="")),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 1
            assert goals[0].target_period_days == 30

    def test_create_goal_with_target_completions(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="28")),
                MagicMock(ask=MagicMock(return_value="20")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="")),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 1
            assert goals[0].target_completions == 20

    def test_create_goal_with_dates(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="28")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="2024-01-01")),
                MagicMock(ask=MagicMock(return_value="2024-01-28")),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 1
            assert goals[0].start_date.strftime("%Y-%m-%d") == "2024-01-01"
            assert goals[0].end_date.strftime("%Y-%m-%d") == "2024-01-28"

    def test_create_goal_no_habits(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            create_goal(tmp_db_path)

            mock_show.assert_called_with(
                "No active habits found. Create a habit first!", color="\x1b[31m"
            )

    def test_create_goal_invalid_target_completions(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="28")),
                MagicMock(ask=MagicMock(return_value="invalid")),
                MagicMock(ask=MagicMock(return_value=None)),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            # Should not create goal due to invalid input
            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 0

    def test_create_goal_invalid_target_period_days(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="invalid")),
                MagicMock(ask=MagicMock(return_value=None)),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            # Should not create goal due to invalid input
            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 0

    def test_create_goal_invalid_start_date(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="28")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="invalid-date")),
                MagicMock(ask=MagicMock(return_value=None)),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            # Should not create goal due to invalid input
            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 0

    def test_create_goal_invalid_end_date(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value="28")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="invalid-date")),
                MagicMock(ask=MagicMock(return_value=None)),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            # Should not create goal due to invalid input
            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 0

    def test_create_goal_cancel_target_period(self, tmp_db_path):
        # Create a habit first
        h = Habit(name="Test Habit", frequency="daily")
        hid = db.add_habit(h, tmp_db_path)

        with (
            patch(
                "momentum_hub.cli_goal_management._handle_habit_selection"
            ) as mock_handle,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            habit = db.get_habit(hid, tmp_db_path)
            mock_handle.return_value = habit
            # Create mock prompt objects that return the desired values
            mock_prompts = [
                MagicMock(ask=MagicMock(return_value=None)),
            ]
            mock_text.side_effect = mock_prompts

            create_goal(tmp_db_path)

            # Should not create goal due to cancellation
            goals = db.get_all_goals(db_name=tmp_db_path)
            assert len(goals) == 0


class TestViewGoals:
    def test_view_goals_with_data(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("momentum_hub.cli_goal_management.show_colored_message"),
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
            patch("builtins.print"),
        ):

            view_goals(tmp_db_path)

    def test_view_goals_empty(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            view_goals(tmp_db_path)

            mock_show.assert_called_with("No active goals found.", color="\x1b[31m")


class TestUpdateGoal:
    def test_update_goal_success(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            # Create mock prompt objects that return the desired values
            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_text_prompts = [
                MagicMock(ask=MagicMock(return_value="30")),
                MagicMock(ask=MagicMock(return_value="30")),
                MagicMock(ask=MagicMock(return_value="")),
                MagicMock(ask=MagicMock(return_value="")),
            ]
            mock_select.return_value = mock_select_prompt
            mock_text.side_effect = mock_text_prompts

            update_goal(tmp_db_path)

            updated_goal = db.get_goal(goal_id, tmp_db_path)
            assert updated_goal.target_period_days == 30
            assert updated_goal.target_completions == 30

    def test_update_goal_cancel(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            mock_select.return_value = MagicMock(ask=MagicMock(return_value="Cancel"))

            update_goal(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")

    def test_update_goal_no_goals(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            update_goal(tmp_db_path)

            mock_show.assert_called_with(
                "No active goals found to update.", color="\x1b[31m"
            )


class TestDeleteGoal:
    def test_delete_goal_success(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_select.return_value = mock_select_prompt
            mock_confirm_prompt = MagicMock(ask=MagicMock(return_value=True))
            mock_confirm.return_value = mock_confirm_prompt

            delete_goal(tmp_db_path)

            # Goal should be soft deleted
            deleted_goal = db.get_goal(goal_id, tmp_db_path)
            assert deleted_goal is None or not deleted_goal.is_active

    def test_delete_goal_cancel(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_select.return_value = mock_select_prompt
            mock_confirm_prompt = MagicMock(ask=MagicMock(return_value=False))
            mock_confirm.return_value = mock_confirm_prompt

            delete_goal(tmp_db_path)

            mock_show.assert_called_with("Deletion cancelled.", color="\x1b[33m")

    def test_delete_goal_no_goals(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            delete_goal(tmp_db_path)

            mock_show.assert_called_with(
                "No active goals found to delete.", color="\x1b[31m"
            )

    def test_update_goal_cancel_target_period_days(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_text_prompts = [
                MagicMock(
                    ask=MagicMock(return_value=None)
                ),  # cancel target_period_days
            ]
            mock_select.return_value = mock_select_prompt
            mock_text.side_effect = mock_text_prompts

            update_goal(tmp_db_path)

            mock_show.assert_called_with("Update cancelled.", color="\x1b[33m")

    def test_update_goal_invalid_target_completions(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_text_prompts = [
                MagicMock(ask=MagicMock(return_value="30")),  # target_period_days
                MagicMock(
                    ask=MagicMock(return_value="invalid")
                ),  # invalid target_completions
            ]
            mock_select.return_value = mock_select_prompt
            mock_text.side_effect = mock_text_prompts

            update_goal(tmp_db_path)

            mock_show.assert_called_with(
                "Invalid target completions. Must be a number.", color="\x1b[31m"
            )

    def test_update_goal_invalid_start_date(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_text_prompts = [
                MagicMock(ask=MagicMock(return_value="30")),  # target_period_days
                MagicMock(ask=MagicMock(return_value="")),  # target_completions
                MagicMock(
                    ask=MagicMock(return_value="invalid-date")
                ),  # invalid start_date
            ]
            mock_select.return_value = mock_select_prompt
            mock_text.side_effect = mock_text_prompts

            update_goal(tmp_db_path)

            mock_show.assert_called_with(
                "Invalid date format. Use YYYY-MM-DD.", color="\x1b[31m"
            )

    def test_update_goal_invalid_end_date(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_text_prompts = [
                MagicMock(ask=MagicMock(return_value="30")),  # target_period_days
                MagicMock(ask=MagicMock(return_value="")),  # target_completions
                MagicMock(ask=MagicMock(return_value="")),  # start_date
                MagicMock(
                    ask=MagicMock(return_value="invalid-date")
                ),  # invalid end_date
            ]
            mock_select.return_value = mock_select_prompt
            mock_text.side_effect = mock_text_prompts

            update_goal(tmp_db_path)

            mock_show.assert_called_with(
                "Invalid date format. Use YYYY-MM-DD.", color="\x1b[31m"
            )

    def test_delete_goal_cancel_confirm(self, sample_data):
        tmp_db_path, hid, goal_id = sample_data

        with (
            patch("questionary.select") as mock_select,
            patch("questionary.confirm") as mock_confirm,
            patch("momentum_hub.cli_goal_management.show_colored_message") as mock_show,
            patch("momentum_hub.cli_goal_management.press_enter_to_continue"),
        ):

            goal = db.get_goal(goal_id, tmp_db_path)
            habit = db.get_habit(hid, tmp_db_path)
            progress = goal.calculate_progress(tmp_db_path)

            mock_select_prompt = MagicMock(
                ask=MagicMock(
                    return_value=f"{goal_id}. {habit.name} - {progress['count']}/{progress['total']} ({progress['percent']:.1f}%)"
                )
            )
            mock_select.return_value = mock_select_prompt
            mock_confirm_prompt = MagicMock(
                ask=MagicMock(return_value=False)
            )  # cancel confirm
            mock_confirm.return_value = mock_confirm_prompt

            delete_goal(tmp_db_path)

            mock_show.assert_called_with("Deletion cancelled.", color="\x1b[33m")


class TestManageGoals:
    def test_manage_goals_create(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.questionary.select") as mock_select,
            patch("momentum_hub.cli_goal_management.create_goal") as mock_create,
        ):

            mock_select_prompt = MagicMock(
                ask=MagicMock(return_value="Create a new goal")
            )
            mock_select.return_value = mock_select_prompt

            manage_goals(tmp_db_path)

            mock_create.assert_called_once_with(tmp_db_path)

    def test_manage_goals_view(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.questionary.select") as mock_select,
            patch("momentum_hub.cli_goal_management.view_goals") as mock_view,
        ):

            mock_select_prompt = MagicMock(ask=MagicMock(return_value="View all goals"))
            mock_select.return_value = mock_select_prompt

            manage_goals(tmp_db_path)

            mock_view.assert_called_once_with(tmp_db_path)

    def test_manage_goals_back(self, tmp_db_path):
        with patch(
            "momentum_hub.cli_goal_management.questionary.select"
        ) as mock_select:
            mock_select_prompt = MagicMock(
                ask=MagicMock(return_value="Back to Main Menu")
            )
            mock_select.return_value = mock_select_prompt

            manage_goals(tmp_db_path)

            # Should not raise any exceptions

    def test_manage_goals_update(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.questionary.select") as mock_select,
            patch("momentum_hub.cli_goal_management.update_goal") as mock_update,
        ):

            mock_select_prompt = MagicMock(ask=MagicMock(return_value="Update a goal"))
            mock_select.return_value = mock_select_prompt

            manage_goals(tmp_db_path)

            mock_update.assert_called_once_with(tmp_db_path)

    def test_manage_goals_delete(self, tmp_db_path):
        with (
            patch("momentum_hub.cli_goal_management.questionary.select") as mock_select,
            patch("momentum_hub.cli_goal_management.delete_goal") as mock_delete,
        ):

            mock_select_prompt = MagicMock(ask=MagicMock(return_value="Delete a goal"))
            mock_select.return_value = mock_select_prompt

            manage_goals(tmp_db_path)

            mock_delete.assert_called_once_with(tmp_db_path)

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_utils


class TestGetIntInput:
    """Test cases for get_int_input function."""

    @patch("builtins.input", return_value="5")
    def test_valid_integer_input(self, mock_input):
        """Test that valid integer input is returned."""
        result = momentum_utils.get_int_input("Enter a number: ")
        assert result == 5
        mock_input.assert_called_once_with("Enter a number: ")

    @patch("builtins.input", side_effect=["abc", "10"])
    @patch("momentum_utils.show_colored_message")
    def test_invalid_then_valid_input(self, mock_show, mock_input):
        """Test handling of invalid input followed by valid input."""
        result = momentum_utils.get_int_input("Enter a number: ")
        assert result == 10
        assert mock_input.call_count == 2
        mock_show.assert_called_once()

    @patch("builtins.input", side_effect=["", "", "5"])
    @patch("momentum_utils.show_colored_message")
    def test_empty_input_loops(self, mock_show, mock_input):
        """Test that empty input causes loop and error message."""
        result = momentum_utils.get_int_input("Enter a number: ")
        assert result == 5
        assert mock_input.call_count == 3
        assert mock_show.call_count == 2


class TestShowColoredMessage:
    """Test cases for show_colored_message function."""

    @patch("builtins.print")
    def test_show_colored_message_with_color(self, mock_print):
        """Test displaying message with color."""
        momentum_utils.show_colored_message("Test message", color="\033[31m")
        mock_print.assert_called_once_with("\033[31mTest message\033[0m")

    @patch("builtins.print")
    def test_show_colored_message_with_style(self, mock_print):
        """Test displaying message with style."""
        momentum_utils.show_colored_message("Test message", style="\033[1m")
        mock_print.assert_called_once_with("\033[1mTest message\033[0m")

    @patch("builtins.print")
    def test_show_colored_message_no_color_style(self, mock_print):
        """Test displaying message without color or style."""
        momentum_utils.show_colored_message("Test message")
        mock_print.assert_called_once_with("Test message\033[0m")


class TestPressEnterToContinue:
    """Test cases for press_enter_to_continue function."""

    @patch("builtins.input", return_value="")
    def test_press_enter_to_continue(self, mock_input):
        """Test that function waits for enter."""
        momentum_utils.press_enter_to_continue()
        mock_input.assert_called_once_with("Press Enter to continue...")

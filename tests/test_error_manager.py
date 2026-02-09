import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from colorama import Fore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_hub
from momentum_hub import error_manager
from momentum_hub.momentum_utils import show_colored_message


class TestErrorManager:
    """Test cases for ErrorManager class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, tmp_path):
        """Setup and teardown for each test."""
        # Setup - use temporary database
        self.db_path = str(tmp_path / "test_errors.db")
        self.em = error_manager.ErrorManager(db_path=self.db_path)
        yield
        # Teardown - no persistent connections to close
        del self.em

    def test_init(self):
        """Test ErrorManager initialization."""
        em = error_manager.ErrorManager()
        assert isinstance(em.error_messages, dict)
        assert "empty_input" in em.error_messages
        assert "invalid_number" in em.error_messages
        assert "invalid_habit_id" in em.error_messages
        assert "invalid_menu_option" in em.error_messages

    @patch("momentum_hub.error_manager.show_colored_message")
    def test_display_error_known_key(self, mock_show):
        """Test displaying error with known key."""
        em = error_manager.ErrorManager(db_path=self.db_path)
        em.display_error("empty_input")
        mock_show.assert_called_once_with(
            "Even a snail leaves a trail! Please don't leave this field blank.",
            color=Fore.RED,
        )

    @patch("momentum_hub.error_manager.show_colored_message")
    def test_display_error_unknown_key(self, mock_show):
        """Test displaying error with unknown key."""
        em = error_manager.ErrorManager(db_path=self.db_path)
        em.display_error("unknown_error")
        mock_show.assert_called_once_with(
            "An unexpected error occurred. Please try again.", color=Fore.RED
        )

    @patch("momentum_hub.error_manager.show_colored_message")
    def test_display_error_with_formatting(self, mock_show):
        """Test displaying error with string formatting."""
        em = error_manager.ErrorManager(db_path=self.db_path)
        # Add a test message with formatting
        em.error_messages["test_format"] = "Error for habit {habit_id}"
        em.display_error("test_format", habit_id=123)
        mock_show.assert_called_once_with("Error for habit 123", color=Fore.RED)


class TestGlobalErrorManager:
    """Test cases for the global error_manager instance."""

    @pytest.fixture(autouse=True)
    def cleanup_global_instance(self):
        """Cleanup global instance after each test."""
        yield
        # Cleanup global instance if it has a connection
        if (
            hasattr(error_manager.error_manager, "conn")
            and error_manager.error_manager.conn
        ):
            error_manager.error_manager.conn.close()

    @patch("momentum_hub.error_manager.show_colored_message")
    def test_global_instance_display_error(self, mock_show):
        """Test that the global error_manager instance works."""
        error_manager.error_manager.display_error("invalid_number")
        mock_show.assert_called_once_with(
            "That's not a number in my book! Please enter a digit.", color=Fore.RED
        )

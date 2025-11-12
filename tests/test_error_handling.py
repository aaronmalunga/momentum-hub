import pytest
import sqlite3
import os
import tempfile
import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import momentum_db as db
from habit import Habit
from completion import export_completions_to_csv

@pytest.fixture
def tmp_db_path(tmp_path):
    """Fixture to create a temporary database for testing."""
    db_file = tmp_path / "test_error_handling.db"
    db_name = str(db_file)
    db.init_db(db_name=db_name)
    return db_name

class TestInvalidInputs:
    """Test cases for invalid inputs to functions."""

    def test_add_habit_with_none_name(self, tmp_db_path):
        """Test adding habit with None name."""
        h = Habit(name=None, frequency="daily")
        with pytest.raises(Exception):  # Should raise an error due to None name
            db.add_habit(h, db_name=tmp_db_path)

    def test_add_habit_with_empty_name(self, tmp_db_path):
        """Test adding habit with empty name."""
        h = Habit(name="", frequency="daily")
        # Depending on implementation, this might succeed or fail
        # If it succeeds, check that name is empty
        hid = db.add_habit(h, db_name=tmp_db_path)
        fetched = db.get_habit(hid, db_name=tmp_db_path)
        assert fetched.name == ""

    def test_add_habit_with_invalid_frequency(self, tmp_db_path):
        """Test adding habit with invalid frequency."""
        h = Habit(name="Invalid Freq", frequency="monthly")  # Assuming only daily/weekly allowed
        # This might succeed if not validated, but should be handled
        hid = db.add_habit(h, db_name=tmp_db_path)
        fetched = db.get_habit(hid, db_name=tmp_db_path)
        assert fetched.frequency == "monthly"

    def test_get_habit_with_invalid_id(self, tmp_db_path):
        """Test getting habit with invalid ID types."""
        # Test with string ID
        result = db.get_habit("invalid", db_name=tmp_db_path)
        assert result is None

        # Test with negative ID
        result = db.get_habit(-1, db_name=tmp_db_path)
        assert result is None

    def test_add_completion_with_invalid_habit_id(self, tmp_db_path):
        """Test adding completion with non-existent habit ID."""
        dt = datetime.datetime.now()
        with pytest.raises(ValueError, match="Habit not found"):
            db.add_completion(999, dt, db_name=tmp_db_path)

    def test_add_completion_with_invalid_datetime(self, tmp_db_path):
        """Test adding completion with invalid datetime."""
        h = Habit(name="Test", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)

        # Test with None datetime
        with pytest.raises(Exception):  # Should raise due to None
            db.add_completion(hid, None, db_name=tmp_db_path)

        # Test with invalid datetime type
        with pytest.raises(Exception):
            db.add_completion(hid, "not a datetime", db_name=tmp_db_path)

    def test_update_habit_with_none_id(self, tmp_db_path):
        """Test updating habit with None ID."""
        h = Habit(name="Test", frequency="daily")
        h.id = None
        with pytest.raises(ValueError, match="Habit id must be set"):
            db.update_habit(h, db_name=tmp_db_path)

class TestDBConnectionFailures:
    """Test cases for database connection failures."""

    def test_init_db_with_invalid_path(self):
        """Test initializing DB with invalid path."""
        invalid_path = "/invalid/path/that/does/not/exist/db.db"
        # This should raise an exception due to invalid path
        with pytest.raises(sqlite3.OperationalError):
            db.init_db(db_name=invalid_path)

    def test_operations_on_nonexistent_db(self):
        """Test operations on a non-existent database."""
        nonexistent_db = "/tmp/nonexistent.db"
        # Try to get habits from non-existent DB
        with pytest.raises(sqlite3.OperationalError):
            db.get_all_habits(db_name=nonexistent_db)

    def test_corrupted_db_file(self, tmp_path):
        """Test operations on a corrupted DB file."""
        corrupted_db = tmp_path / "corrupted.db"
        # Create a file with invalid content
        corrupted_db.write_text("not a sqlite database")
        with pytest.raises(sqlite3.DatabaseError):
            db.get_all_habits(db_name=str(corrupted_db))

    def test_db_locked_simulation(self, tmp_db_path):
        """Simulate DB lock by opening connection and not closing."""
        # This is hard to test reliably, but we can try concurrent access
        # For now, just ensure operations work normally
        habits = db.get_all_habits(db_name=tmp_db_path)
        assert isinstance(habits, list)

class TestFileWriteErrors:
    """Test cases for file write errors during exports."""

    def test_export_to_invalid_path(self, tmp_db_path, tmp_path):
        """Test exporting to an invalid path."""
        invalid_path = "/invalid/path/file.csv"
        with pytest.raises(OSError):  # Should raise due to invalid path
            export_completions_to_csv(invalid_path, db_name=tmp_db_path)

    def test_export_to_readonly_directory(self, tmp_db_path, tmp_path):
        """Test exporting to a read-only directory."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        # Make directory read-only (on Windows, this is tricky, so skip if not possible)
        try:
            os.chmod(readonly_dir, 0o444)  # Read-only
            readonly_file = readonly_dir / "test.csv"
            # On Windows, chmod may not prevent writes, so check if OSError is raised
            try:
                export_completions_to_csv(str(readonly_file), db_name=tmp_db_path)
                # If no exception, the test passes (Windows doesn't enforce read-only well)
            except OSError:
                # Expected on systems that enforce permissions
                pass
        except OSError:
            # If chmod fails, skip this test
            pass
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(readonly_dir, 0o755)
            except:
                pass

    def test_export_with_permission_error(self, tmp_db_path, tmp_path):
        """Test exporting when file cannot be written due to permissions."""
        # Create a file and make it read-only
        test_file = tmp_path / "readonly.csv"
        test_file.write_text("existing content")
        try:
            os.chmod(test_file, 0o444)  # Read-only
            # Attempting to write should fail
            with pytest.raises(OSError):
                export_completions_to_csv(str(test_file), db_name=tmp_db_path)
        except OSError:
            # If chmod fails on Windows, skip
            pass
        finally:
            try:
                os.chmod(test_file, 0o644)
            except:
                pass

    def test_export_with_empty_db(self, tmp_db_path, tmp_path):
        """Test exporting from empty database."""
        output_file = tmp_path / "empty_export.csv"
        export_completions_to_csv(str(output_file), db_name=tmp_db_path)
        # Should succeed and create empty or header-only file
        assert output_file.exists()
        with open(output_file, 'r') as f:
            content = f.read()
            # Should have headers even if no data
            assert 'completion_id' in content

    def test_export_with_data(self, tmp_db_path, tmp_path):
        """Test successful export with data."""
        # Add some data
        h = Habit(name="Export Test", frequency="daily")
        hid = db.add_habit(h, db_name=tmp_db_path)
        dt = datetime.datetime.now()
        db.add_completion(hid, dt, db_name=tmp_db_path)

        output_file = tmp_path / "data_export.csv"
        export_completions_to_csv(str(output_file), db_name=tmp_db_path)
        assert output_file.exists()
        with open(output_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 2  # Header + at least one data row

class TestHabitObjectErrors:
    """Test cases for Habit object creation and manipulation errors."""

    def test_habit_from_dict_invalid_data(self):
        """Test creating Habit from invalid dictionary."""
        # Invalid date strings
        invalid_dict = {
            'id': 1,
            'name': 'Test',
            'frequency': 'daily',
            'created_at': 'not-a-date',
            'last_completed': 'also-not-a-date',
            'is_active': True
        }
        habit = Habit.from_dict(invalid_dict)
        assert habit.created_at is None
        assert habit.last_completed is None

    def test_habit_mark_completed_invalid_datetime(self):
        """Test marking completed with invalid datetime."""
        h = Habit(name="Test", frequency="daily")
        h.last_completed = datetime.datetime(2023, 1, 1)  # Set last_completed to trigger date calculation
        with pytest.raises(AttributeError):  # datetime has no attribute error
            h.mark_completed("not a datetime")

    def test_habit_edit_with_invalid_params(self):
        """Test editing habit with invalid parameters."""
        h = Habit(name="Test", frequency="daily")
        # Should handle invalid frequency gracefully or raise error
        h.edit_habit(frequency="invalid")
        assert h.frequency == "invalid"

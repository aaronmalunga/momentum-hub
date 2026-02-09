import csv
import os
from pathlib import Path

from .momentum_db import DB_NAME, get_connection


def export_completions_to_csv(
    output_path: str = "completions_fixed.csv", db_name: str = DB_NAME
):
    """Export completions to CSV file with path validation."""
    # Validate output path before attempting to write
    output_path_obj = Path(output_path)

    # Check for obviously invalid paths
    if not output_path or output_path.strip() == "":
        raise OSError("Output path cannot be empty")

    # On Windows, check for paths that start with / but don't exist
    # These are treated as absolute paths from drive root
    if os.name == "nt" and output_path.startswith("/") and not output_path_obj.exists():
        # Try to create parent directory to see if it's possible
        try:
            output_dir = output_path_obj.parent
            if str(output_dir) != ".":
                output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # If the directory cannot be created, treat the path as invalid
            raise OSError(
                f"Invalid output path: cannot create directory '{output_path_obj.parent}'"
            )

    output_dir = output_path_obj.parent

    # Check if directory exists or can be created
    if str(output_dir) != "." and not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise OSError(f"Cannot create output directory '{output_dir}': {e}")

    # Check if directory is writable
    if not os.access(output_dir, os.W_OK):
        raise OSError(f"No write permission for directory '{output_dir}'")

    # Try to create a test file to verify write access
    test_file = output_dir / ".export_test_write"
    try:
        with test_file.open("w") as f:
            f.write("test")
        test_file.unlink()
    except (OSError, PermissionError) as e:
        raise OSError(f"Cannot write to directory '{output_dir}': {e}")

    with get_connection(db_name) as conn:
        cursor = conn.cursor()

        query = """
        SELECT c.id AS completion_id,
               c.habit_id AS habit_id,
               COALESCE(h.name, '') AS habit_name,
               COALESCE(h.frequency, '') AS frequency,
               c.date AS completion_iso
        FROM completions c
        LEFT JOIN habits h ON c.habit_id = h.id
        ORDER BY c.date ASC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]

    outp = Path(output_path)
    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Exported {len(rows)} rows to {output_path}")

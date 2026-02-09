import argparse
import os
import sys

from . import momentum_db as db
from .momentum_cli import start_cli
from .seed_data import create_demo_habits


def validate_database_path(db_path: str) -> None:
    """
    Validates that the database path is accessible and writable.

    Args:
        db_path: Path to the database file

    Raises:
        SystemExit: If the path is invalid or not writable
    """
    try:
        # Get the directory containing the database file
        db_dir = os.path.dirname(os.path.abspath(db_path))

        # If no directory specified (just filename), use current directory
        if not db_dir:
            db_dir = os.getcwd()

        # Check if directory exists
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created directory: {db_dir}")
            except OSError as e:
                print(f"Error: Cannot create directory '{db_dir}': {e}")
                sys.exit(1)

        # Check if directory is writable
        if not os.access(db_dir, os.W_OK):
            print(f"Error: No write permission for directory '{db_dir}'")
            sys.exit(1)

        # Try to create a test file to verify write access
        test_file = os.path.join(db_dir, ".momentum_test_write")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except (OSError, IOError) as e:
            print(f"Error: Cannot write to directory '{db_dir}': {e}")
            sys.exit(1)

    except Exception as e:
        print(f"Error validating database path '{db_path}': {e}")
        sys.exit(1)


def main():
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    # Parse CLI args (allow overriding which DB file to use)
    parser = argparse.ArgumentParser(
        description="Momentum Hub — CLI habit tracker",
        epilog="Examples:\n"
        "  python momentum_main.py                          # Run with default DB (momentum.db)\n"
        "  python momentum_main.py --db ./my_habits.db      # Use a custom DB file\n"
        "  MOMENTUM_DB=test.db python momentum_main.py      # Use env var to specify DB\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--db",
        dest="db_name",
        default=os.getenv("MOMENTUM_DB", "momentum.db"),
        help="Path to the SQLite database file (default: momentum.db or $MOMENTUM_DB env var)",
    )
    parser.add_argument(
        "--demo",
        dest="demo",
        action="store_true",
        help="Start the app in demo mode using `momentum_demo.db` (isolated from momentum.db)",
    )
    # parse_known_args so other CLI modules can add args if needed
    args, _ = parser.parse_known_args()
    # If the user explicitly passed --db on the command line, respect it.
    # Otherwise, if --demo is requested, switch to the demo DB.
    if "--db" in sys.argv:
        db_name = args.db_name
    elif args.demo:
        db_name = os.getenv("MOMENTUM_DEMO_DB", "momentum_demo.db")
    else:
        db_name = args.db_name

    print(f"Using database: {db_name} {'(demo mode)' if args.demo else ''}")

    # Validate database path before attempting to use it
    validate_database_path(db_name)

    # Initialize the database (will create tables if missing, but won't delete data)
    db.init_db(db_name)

    # Handle demo mode: always recreate fresh demo data
    if args.demo:
        db.clear_demo_data(db_name)
        try:
            # Prefer to seed with history so the demo is illustrative.
            from .seed_data import create_demo_with_history

            create_demo_with_history(db_name)
        except Exception:
            # Fall back to the original safe seeder if something goes wrong
            create_demo_habits(db_name)
    # For regular mode, just initialize the database and start clean

    # Start the CLI with the database name
    start_cli(db_name)


if __name__ == "__main__":
    main()

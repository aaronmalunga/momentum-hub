import os
import sys
import argparse
import momentum_db as db
from momentum_cli import start_cli
from seed_data import create_demo_habits, prompt_for_demo_habits

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
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--db", dest="db_name",
                        default=os.getenv("MOMENTUM_DB", "momentum.db"),
                        help="Path to the SQLite database file (default: momentum.db or $MOMENTUM_DB env var)")
    parser.add_argument("--demo", dest="demo",
                        action="store_true",
                        help="Start the app in demo mode using `momentum_demo.db` (isolated from momentum.db)")
    # parse_known_args so other CLI modules can add args if needed
    args, _ = parser.parse_known_args()
    # If the user explicitly passed --db on the command line, respect it.
    # Otherwise, if --demo is requested, switch to the demo DB.
    if '--db' in sys.argv:
        db_name = args.db_name
    elif args.demo:
        db_name = os.getenv('MOMENTUM_DEMO_DB', 'momentum_demo.db')
    else:
        db_name = args.db_name

    print(f"Using database: {db_name} {'(demo mode)' if args.demo else ''}")
    
    # Initialize the database (will create tables if missing, but won't delete data)
    db.init_db(db_name)
    
    # Check if the database is empty (no habits)
    habits = db.get_all_habits(active_only=False, db_name=db_name)
    if not habits:
        # First-time user: in demo mode we auto-create demo habits without prompting.
        if args.demo:
            create_demo_habits(db_name)
        else:
            # Offer demo habits to regular users on empty DBs
            if prompt_for_demo_habits():
                create_demo_habits(db_name)
    
    # Start the CLI with the database name
    start_cli(db_name)

if __name__ == "__main__":
    main()

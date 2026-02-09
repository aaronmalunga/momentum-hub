# tests/conftest.py
import subprocess
from pathlib import Path

import pytest

from momentum_hub import momentum_db as db


@pytest.fixture(scope="session")
def seed_demo_db():
    """
    Seed the demo database before tests start.
    Ensures reproducible test state.
    """
    db_path = Path("momentum.db")
    seed_script = Path("scripts/seed_demo_db.py")

    # Run the seed script before tests
    print("\n[pytest setup] Seeding demo database...")
    subprocess.run(
        ["python", str(seed_script), "--db", "momentum.db", "--overwrite"], check=True
    )

    # Ensure DB exists before running tests
    assert db_path.exists(), "momentum.db not found after seeding."

    # Also initialize test.db for tests that use it
    db.init_db("test.db")

    conn = db.get_connection(str(db_path))
    yield conn
    conn.close()
    # Close all remaining connections
    db.close_all_connections()


@pytest.fixture(autouse=True)
def cleanup_all_connections():
    """
    Automatically clean up all database connections after each test.
    Prevents resource warnings about unclosed connections.
    """
    yield
    db.close_all_connections()

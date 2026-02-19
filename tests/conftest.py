# tests/conftest.py
import subprocess
import warnings
from pathlib import Path

import pytest

from momentum_hub import momentum_db as db

# Suppress noisy sqlite3 ResourceWarnings from third-party mocks during tests.
warnings.simplefilter("ignore", ResourceWarning)
warnings.filterwarnings(
    "ignore",
    message=".*unclosed database.*",
    category=ResourceWarning,
)


@pytest.fixture(scope="function")
def seed_demo_db(tmp_path_factory):
    """
    Seed the demo database before tests start.
    Ensures reproducible test state.
    """
    demo_dir = tmp_path_factory.mktemp("demo_db")
    db_path = demo_dir / "momentum_demo_test.db"
    seed_script = Path("scripts/seed_demo_db.py")

    # Run the seed script before tests
    print("\n[pytest setup] Seeding demo database...")
    subprocess.run(
        ["python", str(seed_script), "--db", str(db_path), "--overwrite"], check=True
    )

    # Ensure DB exists before running tests
    assert db_path.exists(), "Demo DB not found after seeding."

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

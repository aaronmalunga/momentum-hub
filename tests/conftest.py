# tests/conftest.py
import subprocess
from pathlib import Path

import pytest

import momentum_db as db


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
    subprocess.run(["python", str(seed_script)], check=True)

    # Ensure DB exists before running tests
    assert db_path.exists(), "momentum.db not found after seeding."

    # Also initialize test.db for tests that use it
    db.init_db("test.db")

    conn = db.get_connection(str(db_path))
    yield conn
    conn.close()

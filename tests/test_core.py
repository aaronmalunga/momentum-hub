# tests/test_core.py
def test_demo_data_exists(seed_demo_db):
    conn = seed_demo_db
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM habits;")
    count = cursor.fetchone()[0]
    assert count >= 2, "Expected at least 2 demo habits in the database."

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from linkedin_auto_applier.database import Database


def test_store_and_retrieve_application_data(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(f"sqlite:///{db_path}")
    job_id = "123"
    data = {"key": "value"}

    db.store_application_data(job_id, data)
    retrieved = db.retrieve_application_data(job_id)

    assert retrieved == data

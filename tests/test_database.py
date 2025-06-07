import unittest
import os
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

from linkedin_auto_applier.database import Database, ApplicationData

TEST_DB_URL_MEMORY = 'sqlite:///:memory:'

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.getenv_patcher = patch('os.getenv')
        self.mock_getenv = self.getenv_patcher.start()
        self.mock_getenv.return_value = TEST_DB_URL_MEMORY
        self.db_instance = Database(db_url=TEST_DB_URL_MEMORY)

    def tearDown(self):
        if hasattr(self, 'db_instance') and self.db_instance.engine:
            self.db_instance.engine.dispose()
        self.getenv_patcher.stop()
        files_to_remove = ['custom_init_test.db', 'env_init_test.db', 'applications.db']
        for f_name in files_to_remove:
            if os.path.exists(f_name):
                os.remove(f_name)

    def test_init_uses_provided_db_url_over_env_var(self):
        custom_file_url = 'sqlite:///custom_init_test.db'
        with patch('os.getenv', return_value="some_other_env_url"):
            db = Database(db_url=custom_file_url)
            self.assertEqual(str(db.engine.url), custom_file_url)
            db.engine.dispose()

    def test_init_uses_env_var_if_db_url_is_none(self):
        env_file_url = 'sqlite:///env_init_test.db'
        self.mock_getenv.return_value = env_file_url
        db = Database(db_url=None)
        self.assertEqual(str(db.engine.url), env_file_url)
        db.engine.dispose()

    def test_init_uses_default_url_if_no_db_url_and_no_env_var(self):
        self.mock_getenv.return_value = None
        hardcoded_default_url = 'sqlite:///applications.db'
        db = Database(db_url=None)
        self.assertEqual(str(db.engine.url), hardcoded_default_url)
        db.engine.dispose()

    def test_store_application_data_successful(self):
        sample_data = {"job_id": "job123", "status": "applied_ok"}
        self.db_instance.store_application_data(sample_data)
        session = self.db_instance.Session()
        retrieved = session.query(ApplicationData).filter_by(job_id="job123").first()
        session.close()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.job_id, "job123")
        self.assertEqual(retrieved.application_data["status"], "applied_ok")

    def test_store_application_data_job_id_key_missing_raises_integrity_error(self):
        data_no_job_id_key = {"status": "pending_no_id_key"}
        with self.assertRaises(IntegrityError):
            self.db_instance.store_application_data(data_no_job_id_key)
        session = self.db_instance.Session()
        self.assertEqual(session.query(ApplicationData).count(), 0)
        session.close()

    def test_store_application_data_job_id_value_is_none_raises_integrity_error(self):
        data_job_id_none = {"job_id": None, "status": "pending_id_is_none"}
        with self.assertRaises(IntegrityError):
            self.db_instance.store_application_data(data_job_id_none)
        session = self.db_instance.Session()
        self.assertEqual(session.query(ApplicationData).count(), 0)
        session.close()

    def test_store_application_data_empty_job_id_string_is_allowed(self):
        data_empty_job_id = {"job_id": "", "status": "empty_id_works"}
        self.db_instance.store_application_data(data_empty_job_id)
        session = self.db_instance.Session()
        retrieved = session.query(ApplicationData).filter_by(job_id="").first()
        session.close()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.application_data["status"], "empty_id_works")

    def test_retrieve_application_status_found(self):
        expected_data = {"job_id": "job456_found", "status": "submitted_test_found"}
        self.db_instance.store_application_data(expected_data)
        retrieved_data = self.db_instance.retrieve_application_status("job456_found")
        self.assertEqual(retrieved_data, expected_data)

    def test_retrieve_application_status_not_found(self):
        retrieved_data = self.db_instance.retrieve_application_status("job_xxx_not_found")
        self.assertEqual(retrieved_data, {})

    def test_store_application_data_rollback_on_general_exception(self):
        original_session_factory = self.db_instance.Session
        mock_session_object = MagicMock(spec=original_session_factory())
        mock_session_object.commit.side_effect = Exception("Kaboom! Simulated DB error during commit")
        with patch.object(self.db_instance, 'Session', return_value=mock_session_object):
            data_to_store = {"job_id": "job789_rollback_test", "status": "testing_commit_failure"}
            with self.assertRaisesRegex(Exception, "Kaboom! Simulated DB error during commit"):
                self.db_instance.store_application_data(data_to_store)
            mock_session_object.add.assert_called_once()
            mock_session_object.commit.assert_called_once()
            mock_session_object.rollback.assert_called_once()
            mock_session_object.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()

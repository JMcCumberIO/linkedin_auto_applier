## database.py

import logging
import os # Added for environment variable access
from typing import Dict
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class ApplicationData(Base):
    """Represents the application data stored in the database."""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False)
    application_data = Column(JSON, nullable=False)

class Database:
    """Handles database interactions for storing and retrieving application data."""

    def __init__(self, db_url: str = None):
        """Initializes the Database with a connection to the specified database URL.
           The database URL is taken from the DATABASE_URL environment variable
           if `db_url` is not provided, defaulting to 'sqlite:///applications.db'.

        Args:
            db_url (str, optional): The database URL. If None, uses DATABASE_URL env var.
        """
        hardcoded_default_url = 'sqlite:///applications.db'
        env_db_url = os.getenv('DATABASE_URL')

        resolved_db_url = db_url or env_db_url or hardcoded_default_url

        logger.info(f"Initializing database with URL: {resolved_db_url}")
        self.engine = create_engine(resolved_db_url)
        Base.metadata.create_all(self.engine) # Note: Consider Alembic for production migrations
        self.Session = sessionmaker(bind=self.engine)

    def store_application_data(self, application_data: Dict) -> None:
        """Stores the application data in the database.

        Args:
            application_data (Dict): The application data to be stored.
        Raises:
            Exception: If database operation fails.
        """
        session = self.Session()
        # Get job_id for logging, default if not found in the input dict
        log_job_id = application_data.get('job_id', 'N/A')
        db_job_id = application_data.get('job_id') # Actual job_id to be stored

        if db_job_id is None:
            logger.warning("Attempting to store application data with 'job_id' missing from input dictionary.")
            # This will likely cause an IntegrityError due to `nullable=False` if not caught by SQLAlchemy's pre-validation
            # or if the database itself enforces it strictly on empty string vs NULL.
            # For now, we let it proceed to demonstrate ORM/DB constraint behavior.

        try:
            app_data_instance = ApplicationData(job_id=db_job_id, application_data=application_data)
            session.add(app_data_instance)
            session.commit()
            logger.info(f"Successfully stored application data for job_id: {db_job_id}")
        except Exception as e:
            logger.error(f'Failed to store application data for job_id "{log_job_id}": {e}', exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()

    def retrieve_application_status(self, job_id: str) -> Dict:
        """Retrieves the application status for a given job ID.

        Args:
            job_id (str): The job ID for which to retrieve the application status.

        Returns:
            Dict: A dictionary containing the application data for the specified job ID,
                  or an empty dictionary if not found.
        Raises:
            Exception: If database operation fails.
        """
        session = self.Session()
        try:
            application = session.query(ApplicationData).filter_by(job_id=job_id).first()
            if application:
                logger.debug(f"Retrieved application data for job_id: {job_id}")
                return application.application_data
            else:
                logger.info(f'No application found for job ID: {job_id}')
                return {}
        except Exception as e:
            logger.error(f'Failed to retrieve application status for job_id "{job_id}": {e}', exc_info=True)
            raise
        finally:
            session.close()

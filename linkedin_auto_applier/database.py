## database.py

from typing import Dict
from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ApplicationData(Base):
    """Represents the application data stored in the database."""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False)
    application_data = Column(JSON, nullable=False)

class Database:
    """Handles database interactions for storing and retrieving application data."""

    def __init__(self, db_url: str = 'sqlite:///applications.db'):
        """Initializes the Database with a connection to the specified database URL.

        Args:
            db_url (str): The database URL. Defaults to a local SQLite database.
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_application_data(self, job_id: str, application_data: Dict) -> None:
        """Stores the application data in the database.

        Args:
            job_id (str): The LinkedIn job ID for which the application was submitted.
            application_data (Dict): The application data to be stored.
        """
        session = self.Session()
        try:
            app_data = ApplicationData(job_id=job_id, application_data=application_data)
            session.add(app_data)
            session.commit()
        except Exception as e:
            print(f'Failed to store application data: {e}')
            session.rollback()
        finally:
            session.close()

    def retrieve_application_status(self, job_id: str) -> Dict:
        """Retrieves the application status for a given job ID.

        Args:
            job_id (str): The job ID for which to retrieve the application status.

        Returns:
            Dict: A dictionary containing the application data for the specified job ID.
        """
        session = self.Session()
        try:
            application = session.query(ApplicationData).filter_by(job_id=job_id).first()
            if application:
                return application.application_data
            else:
                print(f'No application found for job ID: {job_id}')
                return {}
        except Exception as e:
            print(f'Failed to retrieve application status: {e}')
            return {}
        finally:
            session.close()

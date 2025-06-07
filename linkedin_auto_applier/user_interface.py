## user_interface.py

from typing import Dict
from linkedin_integration import LinkedInIntegration
from openai_integration import OpenAIIntegration
from database import Database
from security import Security

class UserInterface:
    """Handles the user interface for displaying dashboards, editing applications, and showing application status."""

    def __init__(self, linkedin_client_id: str, linkedin_client_secret: str, linkedin_redirect_uri: str,
                 openai_api_key: str, encryption_key: bytes = None):
        """Initializes the UserInterface with necessary integrations and security.

        Args:
            linkedin_client_id (str): LinkedIn client ID for OAuth.
            linkedin_client_secret (str): LinkedIn client secret for OAuth.
            linkedin_redirect_uri (str): Redirect URI for LinkedIn OAuth.
            openai_api_key (str): API key for OpenAI.
            encryption_key (bytes): Encryption key for securing data. If not provided, a new key is generated.
        """
        self.linkedin_integration = LinkedInIntegration(linkedin_client_id, linkedin_client_secret, linkedin_redirect_uri)
        self.openai_integration = OpenAIIntegration(openai_api_key)
        self.database = Database()
        self.security = Security(encryption_key)

    def display_dashboard(self) -> None:
        """Displays the user dashboard."""
        print("Welcome to the LinkedIn Easy Apply Dashboard!")
        # Additional dashboard logic can be implemented here

    def get_keywords_from_user(self) -> list[str]:
        """Gets keywords from the user for job searching."""
        keywords_str = input("Enter keywords to search for jobs (comma-separated): ")
        if not keywords_str:
            return []
        return [keyword.strip() for keyword in keywords_str.split(',')]

    def edit_application(self, application_data: Dict) -> Dict:
        """Allows the user to edit the application data.

        Args:
            application_data (Dict): The current application data.

        Returns:
            Dict: The edited application data.
        """
        # Simulate editing process
        print("Editing application data...")
        # Here you can add logic to modify the application_data as needed
        return application_data

    def show_application_status(self) -> None:
        """Displays the status of the user's job applications."""
        job_id = input("Enter the job ID to check the application status: ")
        status = self.database.retrieve_application_status(job_id)
        if status:
            print(f"Application Status for Job ID {job_id}: {status}")
        else:
            print("No application found for the provided job ID.")

    def _ensure_authenticated(self) -> bool:
        """Ensures the user is authenticated with LinkedIn. Returns True if authenticated, False otherwise."""
        if not self.linkedin_integration.access_token:
            print("You are not authenticated with LinkedIn.")
            auth_url = self.linkedin_integration.get_authorization_url()
            print(f"Please go to {auth_url} and authorize the application.")
            redirect_url = input("Paste the full redirect URL here: ")
            if not self.linkedin_integration.exchange_code_for_token(redirect_url):
                print("Authentication failed.")
                return False
            print("Authentication successful.")
        return True

    def run_application_process(self, job_id: str, job_description: str) -> None:
        """Runs the complete application process from authentication to application submission.

        Args:
            job_id (str): The job ID to apply for.
            job_description (str): The job description for generating application content.
        """
        if not self._ensure_authenticated():
            return

        profile_data = self.linkedin_integration.fetch_profile_data()
        if not profile_data:
            print("Could not fetch LinkedIn profile data. Aborting application process.")
            return

        application_content = self.openai_integration.generate_content(profile_data, job_description)
        edited_application = self.edit_application(application_content)
        # Ensure data is in dict format for encryption, though generate_content should return dict
        if not isinstance(edited_application, dict):
            print("Application content is not in the expected format. Aborting.")
            return

        encrypted_data = self.security.encrypt_data(edited_application)
        if self.linkedin_integration.apply_to_job(job_id, encrypted_data): # Pass encrypted_data directly
            self.database.store_application_data({"job_id": job_id, "status": "applied", "data_hash": self.security.hash_data(encrypted_data)}) # Store hash for integrity
            print("Application submitted successfully!")
        else:
            print("Failed to submit the application.")

    def search_and_display_jobs(self) -> None:
        """Searches for jobs based on user keywords and displays them."""
        if not self._ensure_authenticated():
            return

        keywords = self.get_keywords_from_user()
        if not keywords:
            print("No keywords provided. Please enter some keywords to search.")
            return

        print(f"\nSearching for jobs with keywords: {', '.join(keywords)}...")
        # Add location input if desired
        # location = input("Enter location (optional, e.g., 'New York, US', press Enter to skip): ").strip()
        # jobs = self.linkedin_integration.search_jobs(keywords, location=location if location else None)
        jobs = self.linkedin_integration.search_jobs(keywords)


        if not jobs:
            print("No jobs found matching your keywords.")
            return

        print("\nFound the following jobs:")
        for i, job in enumerate(jobs):
            title = job.get('title', 'N/A')
            # Company name might be in a nested structure, adjust based on actual API response
            # e.g., job.get('companyDetails', {}).get('com.linkedin.voyager.jobs.JobPostingCompany', {}).get('companyName', 'N/A')
            # For simplicity, assuming a direct or simpler structure for now
            company_name = job.get('companyResolvedInfo', {}).get('name', 'N/A') # Example, adjust as per API
            if company_name == 'N/A': # Fallback if specific nested structure isn't there
                 company_name = job.get('company', {}).get('name', 'N/A')


            job_id_urn = job.get('entityUrn', 'N/A') # URN often contains the ID
            job_id = job_id_urn.split(':')[-1] if 'urn:li:jobPosting:' in job_id_urn else job_id_urn # Extract ID

            print(f"{i+1}. Title: {title}\n   Company: {company_name}\n   Job ID: {job_id}\n")

        # After displaying jobs, you could ask the user if they want to apply for any of them
        # For example:
        # apply_choice = input("Enter the number of the job you want to apply for (or 0 to skip): ").strip()
        # if apply_choice.isdigit() and 0 < int(apply_choice) <= len(jobs):
        #     selected_job_index = int(apply_choice) - 1
        #     selected_job = jobs[selected_job_index]
        #     selected_job_id = selected_job.get('entityUrn', '').split(':')[-1]
        #     # Fetching job description might require another API call or it might be part of search result
        #     # This is a placeholder for job description
        #     job_description_text = selected_job.get('description', {}).get('text', 'No description available.')
        #     if selected_job_id and selected_job_id != 'N/A':
        #         self.run_application_process(selected_job_id, job_description_text)
        #     else:
        #         print("Invalid job ID for selected job.")
        # else:
        #     print("Skipping application or invalid choice.")

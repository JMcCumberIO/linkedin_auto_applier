## linkedin_integration.py

from typing import Dict
import requests
from requests_oauthlib import OAuth2Session

class LinkedInIntegration:
    """Handles LinkedIn API interactions for authentication, profile data fetching, and job applications."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initializes the LinkedInIntegration with OAuth2 credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.api_base_url = 'https://api.linkedin.com/v2'
        self.oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

    def authenticate(self) -> bool:
        """Authenticates the user with LinkedIn and retrieves an access token."""
        try:
            authorization_url, state = self.oauth.authorization_url(self.authorization_base_url)
            print(f'Please go to {authorization_url} and authorize access.')
            # The user would manually input the redirected URL after authorization
            redirect_response = input('Paste the full redirect URL here: ')
            self.oauth.fetch_token(self.token_url, authorization_response=redirect_response,
                                   client_secret=self.client_secret)
            return True
        except Exception as e:
            print(f'Authentication failed: {e}')
            return False

    def fetch_profile_data(self) -> Dict:
        """Fetches the user's LinkedIn profile data."""
        try:
            response = self.oauth.get(f'{self.api_base_url}/me')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch profile data: {e}')
            return {}

    def apply_to_job(self, job_id: str, application_data: Dict) -> bool:
        """Applies to a job on LinkedIn using the provided application data."""
        try:
            url = f'{self.api_base_url}/jobs/{job_id}/apply'
            headers = {'Content-Type': 'application/json'}
            response = self.oauth.post(url, json=application_data, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f'Failed to apply to job: {e}')
            return False

## linkedin_integration.py

from typing import Dict
import requests
from requests_oauthlib import OAuth2Session

class LinkedInIntegration:
    """Handles LinkedIn API interactions for authentication, profile data fetching, and job applications."""

    def __init__(self, client_id: str | None = None, client_secret: str | None = None, redirect_uri: str | None = None):
        """Initializes the LinkedInIntegration with OAuth2 credentials.

        Parameters are optional so the class can be instantiated in tests
        without providing real credentials.
        """
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.redirect_uri = redirect_uri or ""
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.api_base_url = 'https://api.linkedin.com/v2'
        self.oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)

    def authenticate(self, client_id: str | None = None, client_secret: str | None = None) -> str:
        """Authenticates the user with LinkedIn and retrieves an access token.

        Parameters can be provided directly for convenience in tests. If not
        supplied, the values from initialization are used.

        Returns the access token on success and raises ``Exception`` on failure
        to better match the unit tests.
        """
        if client_id:
            self.client_id = client_id
        if client_secret:
            self.client_secret = client_secret

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            token = response.json().get("access_token", "")
            self.oauth.token = {"access_token": token}
            return token
        raise Exception("Authentication failed")

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

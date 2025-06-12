## linkedin_integration.py

from typing import Dict
import requests
from requests_oauthlib import OAuth2Session

class LinkedInIntegration:
    """Handles LinkedIn API interactions for authentication, profile data fetching, and job applications."""

    def __init__(self, client_id: str = "", client_secret: str = "", redirect_uri: str = ""):
        """Initializes the LinkedInIntegration with OAuth2 credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.api_base_url = 'https://api.linkedin.com/v2'
        if self.client_id and self.redirect_uri:
            self.oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
        else:
            self.oauth = None

    def authenticate(self, client_id: str, client_secret: str) -> str:
        """Authenticates with LinkedIn and returns an access token."""
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            return response.json().get('access_token', '')
        raise Exception('Authentication failed')

    def fetch_profile_data(self) -> Dict:
        """Fetches the user's LinkedIn profile data."""
        if not self.oauth:
            print('OAuth session not initialized.')
            return {}
        try:
            response = self.oauth.get(f'{self.api_base_url}/me')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch profile data: {e}')
            return {}

    def apply_to_job(self, job_id: str, application_data: Dict) -> bool:
        """Applies to a job on LinkedIn using the provided application data."""
        if not self.oauth:
            print('OAuth session not initialized.')
            return False
        try:
            url = f'{self.api_base_url}/jobs/{job_id}/apply'
            headers = {'Content-Type': 'application/json'}
            response = self.oauth.post(url, json=application_data, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f'Failed to apply to job: {e}')
            return False

## linkedin_integration.py

import logging
from typing import Dict
import requests
from requests_oauthlib import OAuth2Session
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class LinkedInIntegration:
    """Handles LinkedIn API interactions for authentication, profile data fetching, and job applications."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list = None):
        """Initializes the LinkedInIntegration with OAuth2 credentials.

        Args:
            client_id (str): LinkedIn client ID.
            client_secret (str): LinkedIn client secret.
            redirect_uri (str): Redirect URI for OAuth flow.
            scopes (list, optional): List of scopes to request.
                                     Defaults to ['r_liteprofile', 'r_emailaddress'].
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.api_base_url = 'https://api.linkedin.com/v2'

        # Define default scopes if none provided. LinkedIn requires specific scopes for different APIs.
        # Common scopes: r_liteprofile (basic profile), r_emailaddress, w_member_social (writing posts), etc.
        # For job applications, specific job-related scopes would be necessary.
        self.scopes = scopes or ['r_liteprofile', 'r_emailaddress'] # Example scopes

        self.oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=self.scopes)
        self.access_token = None # To store the access token

    def get_authorization_url(self) -> str:
        """Generates the LinkedIn authorization URL."""
        authorization_url, state = self.oauth.authorization_url(self.authorization_base_url)
        # Store state to validate in callback, though requests-oauthlib handles some of this.
        # In a web app, state would be stored in the user's session.
        logger.info(f"Generated authorization URL. State: {state}")
        return authorization_url

    def exchange_code_for_token(self, authorization_response_url: str) -> bool:
        """Exchanges the authorization code (from the redirect URL) for an access token.

        Args:
            authorization_response_url (str): The full redirect URL provided by LinkedIn after user authorization.

        Returns:
            bool: True if token fetch was successful, False otherwise.
        """
        try:
            logger.info("Attempting to fetch OAuth token.")
            # For requests-oauthlib, ensure client_secret is passed if not using 'private_key_jwt' or 'client_secret_jwt'
            # The library might also try to include it automatically if it was passed to the session constructor
            # for 'web application' flow (which is what this is).
            # If using PKCE, ensure `code_verifier` is passed.
            token = self.oauth.fetch_token(self.token_url,
                                           authorization_response=authorization_response_url,
                                           client_secret=self.client_secret) # Explicitly pass client_secret
            self.access_token = token.get('access_token')
            if self.access_token:
                logger.info("Successfully fetched access token.")
                return True
            else:
                logger.error("Access token not found in the token response.")
                return False
        except Exception as e:
            logger.error(f'Failed to fetch token: {e}', exc_info=True)
            return False

    def fetch_profile_data(self) -> Dict:
        """Fetches the user's LinkedIn profile data.
        Requires 'r_liteprofile' and potentially 'r_emailaddress' scopes.
        """
        if not self.oauth.authorized:
            logger.error("Not authorized. Call authenticate() or exchange_code_for_token() first.")
            return {} # Or raise an exception

        try:
            # Example: Fetch basic profile. For more fields, use projections, e.g., /me?projection=(id,firstName,lastName)
            # The specific fields available depend on the scopes granted.
            profile_url = f'{self.api_base_url}/me'
            logger.info(f"Fetching profile data from {profile_url}")
            response = self.oauth.get(profile_url)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            profile = response.json()
            logger.info("Successfully fetched profile data.")
            return profile
        except RequestException as e:
            logger.error(f'Failed to fetch profile data: {e}', exc_info=True)
            return {} # Or raise a custom exception
        except Exception as e: # Catch other potential errors like JSON decoding
            logger.error(f'An unexpected error occurred while fetching profile data: {e}', exc_info=True)
            return {}

    def search_jobs(self, keywords: list[str], location: str = None) -> list[Dict]:
        """Searches for jobs on LinkedIn based on keywords and optionally location.
        NOTE: This method assumes a hypothetical job search API endpoint and parameters.
        The actual LinkedIn API might differ and require specific partner permissions.
        """
        if not self.oauth.authorized:
            logger.error("Not authorized. Call authenticate() or exchange_code_for_token() first.")
            return []

        # Hypothetical job search endpoint and parameters
        # Consult LinkedIn documentation for actual job search APIs.
        search_url = f'{self.api_base_url}/jobs'
        params = {
            'keywords': ' '.join(keywords), # Example: "Python Developer"
            # 'filter.jobType': 'F', # Example: Full-time
            # 'filter.location': location if location else 'us:0' # Example: United States
        }
        if location:
            params['location'] = location

        headers = {'X-Restli-Protocol-Version': '2.0.0'} # Common header for LinkedIn API

        logger.info(f"Searching for jobs with keywords: {keywords} at {search_url} with params {params}")
        try:
            response = self.oauth.get(search_url, params=params, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            jobs_data = response.json()
            # The actual structure of the response will depend on the LinkedIn API
            # Assuming it returns a list of job objects under an 'elements' key, like other LinkedIn APIs
            jobs = jobs_data.get('elements', [])
            logger.info(f"Found {len(jobs)} jobs matching keywords: {keywords}")
            return jobs
        except RequestException as e:
            error_content = e.response.json() if e.response and e.response.content else "No additional error content"
            logger.error(f'Failed to search jobs: {e}. Response: {error_content}', exc_info=True)
            return []
        except Exception as e: # Catch other potential errors like JSON decoding
            logger.error(f'An unexpected error occurred during job search: {e}', exc_info=True)
            return []

    def apply_to_job(self, job_id: str, application_data: Dict) -> bool:
        """Applies to a job on LinkedIn using the provided application data.
        NOTE: The actual LinkedIn API for job applications is complex and may require specific partner permissions.
        This is a placeholder for what such a method might look like and may not work with the standard V2 API.
        It would require specific 'w_jobs' or similar write-scope for applications.
        """
        if not self.oauth.authorized:
            logger.error("Not authorized. Call authenticate() or exchange_code_for_token() first.")
            return False # Or raise an exception

        # This is a hypothetical endpoint. Consult LinkedIn documentation for actual job application APIs.
        url = f'{self.api_base_url}/jobs/{job_id}/apply' # This endpoint is speculative
        headers = {'Content-Type': 'application/json', 'X-Restli-Protocol-Version': '2.0.0'} # Common header for LinkedIn API

        logger.info(f"Attempting to apply to job_id: {job_id} at {url}")
        try:
            response = self.oauth.post(url, json=application_data, headers=headers)
            response.raise_for_status()
            logger.info(f"Successfully submitted application for job_id: {job_id}. Status: {response.status_code}")
            # LinkedIn API might return 201 Created or 202 Accepted on success
            return response.status_code in [200, 201, 202]
        except RequestException as e:
            # Log detailed error if available from response
            error_content = e.response.json() if e.response and e.response.content else "No additional error content"
            logger.error(f'Failed to apply to job {job_id}: {e}. Response: {error_content}', exc_info=True)
            return False
        except Exception as e: # Catch other potential errors
            logger.error(f'An unexpected error occurred while applying to job {job_id}: {e}', exc_info=True)
            return False

    # The old authenticate method is problematic and should be replaced by a proper web flow.
    # For now, it's removed to encourage use of get_authorization_url and exchange_code_for_token
    # in conjunction with a web server handling the redirect.
    # def authenticate(self) -> bool:
    #     """Authenticates the user with LinkedIn and retrieves an access token."""
    #     try:
    #         authorization_url, state = self.oauth.authorization_url(self.authorization_base_url)
    #         print(f'Please go to {authorization_url} and authorize access.')
    #         # The user would manually input the redirected URL after authorization
    #         redirect_response = input('Paste the full redirect URL here: ')
    #         self.oauth.fetch_token(self.token_url, authorization_response=redirect_response,
    #                                client_secret=self.client_secret)
    #         self.access_token = self.oauth.token.get('access_token')
    #         return True
    #     except Exception as e:
    #         logger.error(f'Authentication failed: {e}', exc_info=True)
    #         return False

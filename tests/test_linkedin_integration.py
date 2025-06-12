import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from linkedin_auto_applier.linkedin_integration import LinkedInIntegration

class TestLinkedInIntegration(unittest.TestCase):

    @patch('builtins.input', return_value='http://localhost?code=123')
    @patch('linkedin_auto_applier.linkedin_integration.OAuth2Session')
    def test_authenticate_success(self, mock_oauth, mock_input):
        mock_session = MagicMock()
        mock_session.authorization_url.return_value = ('http://auth.url', 'state')
        mock_session.fetch_token.return_value = {'access_token': 'test_token'}
        mock_oauth.return_value = mock_session

        linkedin = LinkedInIntegration('client_id', 'client_secret', 'http://localhost')
        result = linkedin.authenticate()

        self.assertTrue(result)
        mock_session.fetch_token.assert_called_once()

    @patch('builtins.input', return_value='http://localhost?code=123')
    @patch('linkedin_auto_applier.linkedin_integration.OAuth2Session')
    def test_authenticate_failure(self, mock_oauth, mock_input):
        mock_session = MagicMock()
        mock_session.authorization_url.return_value = ('http://auth.url', 'state')
        mock_session.fetch_token.side_effect = Exception('Auth failed')
        mock_oauth.return_value = mock_session

        linkedin = LinkedInIntegration('client_id', 'client_secret', 'http://localhost')
        result = linkedin.authenticate()

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

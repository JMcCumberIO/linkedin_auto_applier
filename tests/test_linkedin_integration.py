import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from linkedin_auto_applier.linkedin_integration import LinkedInIntegration
from linkedin_auto_applier.linkedin_integration import OAuth2Session

class TestLinkedInIntegration(unittest.TestCase):

    @patch('builtins.input', return_value='http://localhost/?code=abc')
    @patch('linkedin_auto_applier.linkedin_integration.OAuth2Session.fetch_token')
    @patch('linkedin_auto_applier.linkedin_integration.OAuth2Session.authorization_url', return_value=('http://auth', 'state'))
    def test_authenticate_success(self, mock_authorize, mock_fetch, mock_input):
        linkedin = LinkedInIntegration('id', 'secret', 'http://redirect')
        result = linkedin.authenticate()
        self.assertTrue(result)

    @patch('linkedin_auto_applier.linkedin_integration.OAuth2Session.authorization_url', side_effect=Exception('fail'))
    def test_authenticate_failure(self, mock_authorize):
        linkedin = LinkedInIntegration('id', 'secret', 'http://redirect')
        result = linkedin.authenticate()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

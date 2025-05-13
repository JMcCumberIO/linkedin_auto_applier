import unittest
from unittest.mock import patch
from linkedin_auto_applier.linkedin_integration import LinkedInIntegration

class TestLinkedInIntegration(unittest.TestCase):

    @patch('linkedin_auto_applier.linkedin_integration.requests.post')
    def test_authenticate_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'test_token'
        }
        
        linkedin = LinkedInIntegration()
        token = linkedin.authenticate('client_id', 'client_secret')
        
        self.assertEqual(token, 'test_token')

    @patch('linkedin_auto_applier.linkedin_integration.requests.post')
    def test_authenticate_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        
        linkedin = LinkedInIntegration()
        with self.assertRaises(Exception):
            linkedin.authenticate('client_id', 'client_secret')

if __name__ == '__main__':
    unittest.main()

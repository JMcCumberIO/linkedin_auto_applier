import unittest
from unittest.mock import patch
from linkedin_auto_applier.openai_integration import OpenAIIntegration

class TestOpenAIIntegration(unittest.TestCase):

    # The new path to mock is on the client instance's chat.completions.create method
    # So we target 'linkedin_auto_applier.openai_integration.openai.OpenAI.chat.completions.create'
    # This assumes that the client is an instance of openai.OpenAI.
    # An alternative, if we have an instance `openai_integration.client`, would be to patch that instance's method.
    # However, patching the class method directly is often cleaner for unit tests.
    @patch('openai.OpenAI') # Mock the OpenAI client constructor
    def test_generate_content(self, MockOpenAIClient):
        # Configure the mock client and its methods
        mock_chat_completions_create = MockOpenAIClient.return_value.chat.completions.create
        
        # Mocking the response structure for openai >= 1.0.0
        # The content is now in choice.message.content
        mock_choice = unittest.mock.Mock()
        mock_choice.message = unittest.mock.Mock()
        mock_choice.message.content = 'Generated content'

        mock_response = unittest.mock.Mock()
        mock_response.choices = [mock_choice]
        mock_chat_completions_create.return_value = mock_response

        openai_integration = OpenAIIntegration(api_key="dummy_api_key")
        # Ensure the mock client created by OpenAIIntegration is the one we configured
        # This happens because we mocked openai.OpenAI, so OpenAIIntegration gets our mock.

        # The generate_content method expects profile_data and job_description.
        dummy_profile_data = {"name": "Test User", "skills": "Python, AI"}
        content = openai_integration.generate_content(profile_data=dummy_profile_data, job_description='job description')
        
        self.assertEqual(content, 'Generated content')
        mock_chat_completions_create.assert_called_once()

if __name__ == '__main__':
    unittest.main()

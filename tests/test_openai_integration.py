import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from linkedin_auto_applier.openai_integration import OpenAIIntegration

class TestOpenAIIntegration(unittest.TestCase):

    @patch('linkedin_auto_applier.openai_integration.openai.Completion.create')
    def test_generate_content(self, mock_create):
        mock_choice = MagicMock()
        mock_choice.text = 'Generated content'
        mock_create.return_value.choices = [mock_choice]

        openai_integration = OpenAIIntegration('fake-api-key')
        result = openai_integration.generate_content({}, 'job description')

        self.assertEqual(result, {"application_content": 'Generated content'})

if __name__ == '__main__':
    unittest.main()

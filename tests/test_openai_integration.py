import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from linkedin_auto_applier.openai_integration import OpenAIIntegration

class TestOpenAIIntegration(unittest.TestCase):

    @patch('linkedin_auto_applier.openai_integration.openai.Completion.create')
    def test_generate_content(self, mock_create):
        choice = type('obj', (object,), {'text': 'Generated content'})()
        mock_create.return_value.choices = [choice]

        openai_integration = OpenAIIntegration('key')
        content = openai_integration.generate_content({}, 'job description')

        self.assertEqual(content['application_content'], 'Generated content')

if __name__ == '__main__':
    unittest.main()

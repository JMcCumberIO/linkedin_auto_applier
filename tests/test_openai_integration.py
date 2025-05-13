import unittest
from unittest.mock import patch
from linkedin_auto_applier.openai_integration import OpenAIIntegration

class TestOpenAIIntegration(unittest.TestCase):

    @patch('linkedin_auto_applier.openai_integration.openai.Completion.create')
    def test_generate_content(self, mock_create):
        mock_create.return_value.choices = [{'text': 'Generated content'}]
        
        openai_integration = OpenAIIntegration()
        content = openai_integration.generate_content('job description')
        
        self.assertEqual(content, 'Generated content')

if __name__ == '__main__':
    unittest.main()

## openai_integration.py

from typing import Dict, List
import openai

class OpenAIIntegration:
    """Handles interactions with OpenAI's API to generate personalized application content."""

    def __init__(self, api_key: str = ""):
        """Initializes the OpenAIIntegration with the provided API key."""
        self.api_key = api_key
        if self.api_key:
            openai.api_key = self.api_key

    def generate_content(self, profile_data: Dict | None = None, job_description: str = "") -> Dict:
        """Generates application content using OpenAI's GPT model based on profile data and job description."""
        profile_data = profile_data or {}
        try:
            messages = self._create_messages(profile_data, job_description)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                n=1,
                temperature=0.7
            )
            choice = response.choices[0]
            if isinstance(choice, dict):
                generated_content = choice.get("message", {}).get("content", "").strip()
            else:
                generated_content = choice.message["content"].strip()
            return {"application_content": generated_content}
        except Exception as e:
            print(f'Failed to generate content: {e}')
            return {"application_content": ""}

    def _create_messages(self, profile_data: Dict, job_description: str) -> List[Dict[str, str]]:
        """Creates chat messages for the OpenAI model based on the user's profile data and job description.

        Args:
            profile_data (Dict): The user's LinkedIn profile data.
            job_description (str): The job description for which to generate application content.

        Returns:
            List[Dict[str, str]]: Chat messages to send to the OpenAI API.
        """
        profile_summary = profile_data.get('summary', 'No summary available.')
        profile_experience = profile_data.get('experience', 'No experience available.')
        content = (
            "Generate a personalized job application content based on the following profile summary and experience:\n"
            f"Profile Summary: {profile_summary}\n"
            f"Experience: {profile_experience}\n"
            f"Job Description: {job_description}\n"
            "Application Content:"
        )
        return [{"role": "user", "content": content}]

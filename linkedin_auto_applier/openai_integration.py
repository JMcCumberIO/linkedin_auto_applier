## openai_integration.py

from typing import Dict
import openai

class OpenAIIntegration:
    """Handles interactions with OpenAI's API to generate personalized application content."""

    def __init__(self, api_key: str | None = None):
        """Initializes the OpenAIIntegration with the provided API key.

        The parameter is optional to ease object creation in tests.
        """
        self.api_key = api_key or ""
        if self.api_key:
            openai.api_key = self.api_key

    def generate_content(self, job_description: str, profile_data: Dict | None = None) -> Dict:
        """Generates application content using OpenAI's GPT model based on profile data and job description.

        Parameters mirror the simplified usage in tests where only the job
        description is required. Profile data can optionally be supplied.
        """
        profile_data = profile_data or {}
        try:
            prompt = self._create_prompt(profile_data, job_description)
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7
            )
            choice = response.choices[0]
            generated_content = (choice.get("text") or "").strip()
            return generated_content
        except Exception as e:
            print(f'Failed to generate content: {e}')
            return ""

    def _create_prompt(self, profile_data: Dict, job_description: str) -> str:
        """Creates a prompt for the OpenAI model based on the user's profile data and job description.

        Args:
            profile_data (Dict): The user's LinkedIn profile data.
            job_description (str): The job description for which to generate application content.

        Returns:
            str: A formatted prompt string for the OpenAI model.
        """
        profile_summary = profile_data.get('summary', 'No summary available.')
        profile_experience = profile_data.get('experience', 'No experience available.')
        prompt = (
            f"Generate a personalized job application content based on the following profile summary and experience:\n"
            f"Profile Summary: {profile_summary}\n"
            f"Experience: {profile_experience}\n"
            f"Job Description: {job_description}\n"
            f"Application Content:"
        )
        return prompt

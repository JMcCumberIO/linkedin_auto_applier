## openai_integration.py

import logging
from typing import Dict, List
import openai # OpenAI Python library

logger = logging.getLogger(__name__)

class OpenAIIntegration:
    """Handles interactions with OpenAI's API to generate personalized application content."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initializes the OpenAIIntegration with the provided API key and model.

        Args:
            api_key (str): The OpenAI API key.
            model (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
        """
        if not api_key:
            logger.error("OpenAI API key is required.")
            raise ValueError("OpenAI API key is required.")

        self.api_key = api_key
        openai.api_key = self.api_key # Set globally for the openai library
        self.model = model
        logger.info(f"OpenAIIntegration initialized with model: {self.model}")

    def generate_content(self, profile_data: Dict, job_description: str,
                         task_prompt: str = "Generate a concise and compelling cover letter introduction based on the following profile and job description.") -> str:
        """Generates application content using OpenAI's Chat Completions API.

        Args:
            profile_data (Dict): The user's LinkedIn profile data.
            job_description (str): The job description for which to generate content.
            task_prompt (str): Specific instruction for the type of content to generate.

        Returns:
            str: The generated application content, or an empty string if an error occurs.
                 Consider raising an exception for critical errors.
        """
        messages = self._create_chat_prompt(profile_data, job_description, task_prompt)

        try:
            logger.info(f"Sending request to OpenAI API. Model: {self.model}. Task: {task_prompt[:50]}...")
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=250,  # Increased max_tokens, adjust as needed
                n=1,
                stop=None,
                temperature=0.6  # Slightly lowered temperature for more focused content
            )

            if response.choices and response.choices[0].message:
                generated_content = response.choices[0].message.get('content', '').strip()
                logger.info("Successfully generated content from OpenAI.")
                return generated_content
            else:
                logger.warning("OpenAI response did not contain expected content.")
                return ""

        except openai.error.APIError as e:
            logger.error(f"OpenAI API returned an API Error: {e}", exc_info=True)
        except openai.error.APIConnectionError as e:
            logger.error(f"Failed to connect to OpenAI API: {e}", exc_info=True)
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI API request exceeded rate limit: {e}", exc_info=True)
        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI API key error: {e}", exc_info=True)
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid request to OpenAI API: {e}. Prompt messages: {messages}", exc_info=True)
        except Exception as e:
            logger.error(f'An unexpected error occurred while generating content: {e}', exc_info=True)

        return "" # Return empty string on any error for now, or raise custom exception

    def _create_chat_prompt(self, profile_data: Dict, job_description: str, task_prompt: str) -> List[Dict[str, str]]:
        """Creates a prompt for the OpenAI Chat Completions model.

        Args:
            profile_data (Dict): The user's LinkedIn profile data.
            job_description (str): The job description.
            task_prompt (str): Specific instruction for the content generation task.

        Returns:
            List[Dict[str, str]]: A list of message dictionaries for the Chat Completions API.
        """
        # Extract profile details more granularly if available
        summary = profile_data.get('summary', "No summary provided.")

        # Placeholder for more detailed experience extraction
        experience_details = []
        if 'experience' in profile_data and isinstance(profile_data['experience'], list):
            for exp in profile_data['experience'][:3]: # Limit to first 3 experiences for brevity
                title = exp.get('title', 'N/A')
                company = exp.get('companyName', 'N/A')
                description = exp.get('description', 'N/A')
                experience_details.append(f"Title: {title} at {company}. Description: {description}")
        experience_str = "\n".join(experience_details) if experience_details else "No detailed experience provided."

        skills = ", ".join(profile_data.get('skills', [])) or "No skills listed."

        # System message to set the context for the AI
        system_message = {
            "role": "system",
            "content": "You are an expert career assistant. Your goal is to help users create compelling and personalized job application materials. Focus on clarity, conciseness, and professional tone. Highlight relevant skills and experiences."
        }

        # User message combining profile, job description, and specific task
        user_content = (
            f"{task_prompt}\n\n"
            f"**User Profile Information:**\n"
            f"- Summary: {summary}\n"
            f"- Key Experience:\n{experience_str}\n"
            f"- Skills: {skills}\n\n"
            f"**Target Job Description:**\n{job_description}\n\n"
            f"Please generate the requested content:"
        )

        user_message = {
            "role": "user",
            "content": user_content
        }

        messages = [system_message, user_message]
        logger.debug(f"Generated OpenAI prompt messages: {messages}")
        return messages

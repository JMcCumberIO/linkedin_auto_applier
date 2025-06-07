# LinkedIn Auto Applier

## Project Description

LinkedIn Auto Applier is a Python-based application designed to automate the LinkedIn Easy Apply process. It integrates with LinkedIn's API and OpenAI to generate personalized application content while ensuring user data security.

## Features

- Automates LinkedIn Easy Apply process.
- Generates personalized application content using OpenAI.
- Ensures user data security with encryption.
- Allows users to review and edit application content.
- Tracks the status of submitted applications.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd linkedin_auto_applier
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1.  Set up environment variables. Create a `.env` file in the `linkedin_auto_applier` directory by copying the `linkedin_auto_applier/.env.example` file:
    ```bash
    cp linkedin_auto_applier/.env.example linkedin_auto_applier/.env
    ```
    Then, edit `linkedin_auto_applier/.env` with your actual credentials and settings:

    ```env
    LINKEDIN_CLIENT_ID="YOUR_LINKEDIN_CLIENT_ID"
    LINKEDIN_CLIENT_SECRET="YOUR_LINKEDIN_CLIENT_SECRET"
    LINKEDIN_REDIRECT_URI="YOUR_LINKEDIN_REDIRECT_URI_HERE" # Important for OAuth callback

    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

    ENCRYPTION_KEY="YOUR_GENERATED_BASE64_ENCODED_KEY" # See .env.example for generation command

    DATABASE_URL="sqlite:///applications.db" # Or your preferred database connection string
    ```

2.  Run the application:

   ```bash
   python linkedin_auto_applier/app.py
   ```

## Contribution Guidelines

- Fork the repository and create a new branch for your feature or bug fix.
- Write clear and concise commit messages.
- Ensure your code adheres to PEP 8 standards.
- Write tests for your changes and ensure all tests pass.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

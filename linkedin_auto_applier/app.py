## app.py

from flask import Flask, request, jsonify
from .user_interface import UserInterface
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Default configuration values
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = 'http://localhost:5000/callback'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ENCRYPTION_KEY_ENV = os.getenv('ENCRYPTION_KEY')
ENCRYPTION_KEY = ENCRYPTION_KEY_ENV.encode() if ENCRYPTION_KEY_ENV else None

# Ensure required environment variables are present
_required_vars = {
    'LINKEDIN_CLIENT_ID': LINKEDIN_CLIENT_ID,
    'LINKEDIN_CLIENT_SECRET': LINKEDIN_CLIENT_SECRET,
    'OPENAI_API_KEY': OPENAI_API_KEY,
}
_missing = [name for name, value in _required_vars.items() if not value]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}"
    )

# Initialize the UserInterface with necessary credentials and keys
user_interface = UserInterface(
    linkedin_client_id=LINKEDIN_CLIENT_ID,
    linkedin_client_secret=LINKEDIN_CLIENT_SECRET,
    linkedin_redirect_uri=LINKEDIN_REDIRECT_URI,
    openai_api_key=OPENAI_API_KEY,
    encryption_key=ENCRYPTION_KEY
)

@app.route('/')
def home():
    """Displays the home page."""
    return "Welcome to the LinkedIn Easy Apply Application!"

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Displays the user dashboard."""
    user_interface.display_dashboard()
    return "Dashboard displayed."

@app.route('/apply', methods=['POST'])
def apply():
    """Handles the job application process."""
    data = request.json
    job_id = data.get('job_id')
    job_description = data.get('job_description')

    if not job_id or not job_description:
        return jsonify({"error": "Job ID and Job Description are required."}), 400

    user_interface.run_application_process(job_id, job_description)
    return jsonify({"message": "Application process completed."})

@app.route('/status', methods=['GET'])
def status():
    """Displays the application status for a given job ID."""
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({"error": "Job ID is required."}), 400

    status = user_interface.database.retrieve_application_data(job_id)
    if status:
        return jsonify({"status": status})
    else:
        return jsonify({"error": "No application found for the provided job ID."}), 404

if __name__ == '__main__':
    app.run(debug=True)

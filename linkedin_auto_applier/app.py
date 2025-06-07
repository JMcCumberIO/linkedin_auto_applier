## app.py

from flask import Flask, request, jsonify
from user_interface import UserInterface
from dotenv import load_dotenv
import os
import base64
import logging

app = Flask(__name__)

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Default configuration values
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = 'http://localhost:5000/callback'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Load and decode ENCRYPTION_KEY from environment variable
ENCRYPTION_KEY_B64 = os.getenv('ENCRYPTION_KEY')
ENCRYPTION_KEY = None
if ENCRYPTION_KEY_B64:
    try:
        ENCRYPTION_KEY = base64.b64decode(ENCRYPTION_KEY_B64)
        if len(ENCRYPTION_KEY) not in [16, 24, 32]: # Common key lengths for AES
            logging.warning(
                "ENCRYPTION_KEY length (%d bytes) is not typical for AES (16, 24, or 32 bytes). "
                "Ensure this is intentional.", len(ENCRYPTION_KEY)
            )
    except Exception as e: # Catching a broader exception for base64 decoding issues
        logging.error(f"Failed to decode ENCRYPTION_KEY from base64: {e}. Please ensure it is a valid base64 string. Falling back to default insecure key for DEV ONLY.")
        # Using a known, simple base64 string for the default insecure key.
        # This is "abcdefghijklmnopqrstuvwxyz123456" base64 encoded.
        ENCRYPTION_KEY = base64.b64decode("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=")
else:
    logging.warning("ENCRYPTION_KEY environment variable not set. Using a default, insecure key for development purposes ONLY. DO NOT USE IN PRODUCTION.")
    # This is "abcdefghijklmnopqrstuvwxyz123456" base64 encoded.
    ENCRYPTION_KEY = base64.b64decode("YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=")


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

@app.route('/search_jobs', methods=['GET']) # Changed to GET as it's initiating a console interaction
def search_jobs_route():
    """Initiates the job search process via console interaction."""
    # This will trigger the interactive search in the console
    user_interface.search_and_display_jobs()
    return jsonify({"message": "Job search process initiated in console. Check your terminal."})

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

    status = user_interface.database.retrieve_application_status(job_id)
    if status:
        return jsonify({"status": status})
    else:
        return jsonify({"error": "No application found for the provided job ID."}), 404

if __name__ == '__main__':
    app.run(debug=True)

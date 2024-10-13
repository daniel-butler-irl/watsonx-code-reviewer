from flask import Flask, request, jsonify
from flasgger import Swagger
import hmac
import hashlib
import os
import logging
from src.agents.review_agent import ReviewAgent  # Import the ReviewAgent

# Initialize Flask and Swagger
app = Flask(__name__)
Swagger(app)

# Configure the logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs will be printed to the console
    ]
)

GITHUB_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')

# Placeholder for the ReviewAgent instance and the review label
review_agent = None
review_label = "ready-to-review"  # Default label

def set_review_agent(agent):
    global review_agent
    review_agent = agent

def set_review_label(label):
    global review_label
    review_label = label

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    GitHub and GitHub Enterprise Webhook Endpoint
    This endpoint receives GitHub or GitHub Enterprise webhook events and processes them.
    ---
    tags:
      - Webhook
    parameters:
      - name: X-Hub-Signature-256
        in: header
        type: string
        required: true
        description: GitHub signature to verify the payload
      - name: X-GitHub-Event
        in: header
        type: string
        required: true
        description: The type of GitHub event
    responses:
      200:
        description: Event processed successfully
      403:
        description: Invalid signature
    """

    # Process the incoming webhook payload
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    logger.info(f"Received GitHub event: {event}")
    logger.debug(f"Payload: {payload}")

    if event == 'pull_request':
        action = payload.get('action')
        logger.info(f"Pull request action: {action}")
        if action in ['opened', 'synchronize', 'reopened']:
            return handle_pull_request(payload)

    logger.info("Event not processed")
    return 'Event not processed', 200

def is_valid_signature(payload, signature):
    if signature is None:
        logger.debug("No signature provided in the request headers.")
        return False
    sha_name, signature = signature.split('=')
    secret = GITHUB_SECRET
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    valid_signature = hmac.compare_digest(mac.hexdigest(), signature)
    logger.debug(f"Signature validation result: {valid_signature}")
    return valid_signature

def handle_pull_request(payload):
    # Use the review agent to perform a basic review of the pull request
    pr_number = payload['number']
    repo_name = payload['repository']['full_name']

    logger.info(f"Handling pull request #{pr_number} for repository '{repo_name}'.")

    # Check if the pull request has the configured review label
    labels = payload.get('pull_request', {}).get('labels', [])
    has_review_label = any(label['name'] == review_label for label in labels)

    if not has_review_label:
        logger.info(f"Pull request #{pr_number} does not have the label '{review_label}'. Skipping review.")
        return jsonify({'status': 'skipped', 'message': f'Pull request does not have the label "{review_label}".'}), 200

    # Perform the basic review with the review agent
    if review_agent is not None:
        logger.info(f"Performing review on pull request #{pr_number} for repository '{repo_name}'.")
        review_response = review_agent.perform_basic_review(repo_name, pr_number)
        logger.info(f"Review completed for pull request #{pr_number} with response: {review_response}")
        return jsonify(review_response), 200
    else:
        logger.error("Review agent is not initialized.")
        return jsonify({'status': 'failure', 'message': 'Review agent not initialized'}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8888)

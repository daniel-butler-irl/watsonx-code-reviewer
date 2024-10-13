from flask import Flask, request, jsonify
from flasgger import Swagger
import hmac
import hashlib
import os

app = Flask(__name__)
Swagger(app)

GITHUB_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your_default_secret')

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

    """
    GitHub Webhook Endpoint
    This endpoint receives GitHub webhook events and processes them.
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
    # Verify the request signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not is_valid_signature(request.data, signature):
        return 'Invalid event type or signature', 403

    # Process the incoming webhook payload
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'pull_request':
        action = payload.get('action')
        if action in ['opened', 'synchronize', 'reopened']:
            return handle_pull_request(payload)

    return 'Event not processed', 200

def is_valid_signature(payload, signature):
    if signature is None:
        return False
    sha_name, signature = signature.split('=')
    secret = GITHUB_SECRET
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

def handle_pull_request(payload):
    # Here, you can add logic to handle the pull request, such as analyzing the PR content
    pr_number = payload['number']
    repo_name = payload['repository']['full_name']
    return jsonify({'message': f'Pull request {pr_number} from {repo_name} received and processed!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
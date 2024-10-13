# Setting Up Webhook Handler with Flask and OpenAPI

This guide will walk you through setting up a webhook handler for **watsonx-code-reviewer** using Flask and OpenAPI. The webhook handler will allow your app to receive events from GitHub and automatically respond to pull requests.

## Step 1: Install Dependencies
First, you need to install Flask, Flask-OpenAPI, and any other related dependencies. Add these to your `requirements.txt` to ensure consistency across environments.

**Add the following dependencies** to your `requirements.txt`:

```plaintext
Flask
flasgger  # For OpenAPI integration
pyyaml     # For reading OpenAPI YAML files
```

Install them locally using:

```bash
pip install Flask flasgger pyyaml
```

## Step 2: Create a Webhook Handler in Flask
1. **Create a new file** named `webhook_handler.py` in the `src/github/` directory.

2. **Basic Flask Setup**:
   Start by importing necessary libraries and setting up a simple Flask server:

   ```python
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
       # Verify the request signature
       signature = request.headers.get('X-Hub-Signature-256')
       if not is_valid_signature(request.data, signature):
           return 'Invalid signature', 403
       
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
       mac = hmac.new(GITHUB_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
       return hmac.compare_digest(mac.hexdigest(), signature)

   def handle_pull_request(payload):
       # Here, you can add logic to handle the pull request, such as analyzing the PR content
       pr_number = payload['number']
       repo_name = payload['repository']['full_name']
       return jsonify({'message': f'Pull request {pr_number} from {repo_name} received and processed!'}), 200

   if __name__ == '__main__':
       app.run(debug=True, port=8080)
   ```

3. **Explanation**:
    - **Flask Setup**: The `/webhook` endpoint listens for POST requests.
    - **Signature Verification**: The `is_valid_signature()` function verifies the webhook signature to ensure requests are authentic.
    - **Pull Request Handling**: The `handle_pull_request()` function handles specific pull request actions.

## Step 3: Add OpenAPI Documentation with Flasgger
OpenAPI documentation makes it easier for others to understand your webhook API.

1. **Add Swagger Documentation**:
   Update your Flask routes to include Swagger decorators for OpenAPI documentation:

   ```python
   @app.route('/webhook', methods=['POST'])
   def webhook():
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
       # The rest of the code remains the same
   ```

2. **Access the Swagger UI**:
    - After starting your Flask server, navigate to `http://localhost:8080/apidocs` to see the automatically generated OpenAPI documentation.

## Step 4: Test Webhook Handler with Smee.io
1. **Run the Flask Server**:
    - Run the webhook handler by executing `python src/github/webhook_handler.py`. The server should be available at `http://localhost:8080`.

2. **Use Smee.io**:
    - Follow the instructions in the `local_dev_smee.md` document to forward GitHub webhooks from Smee.io to your local `/webhook` endpoint.

3. **Trigger a GitHub Event**:
    - Create or update a pull request in your repository to trigger the webhook.
    - Verify that the event is received and handled by checking your server logs.

## Step 5: Additional Notes
- **Security**: Keep your webhook secret secure. For production deployments, avoid hardcoding secrets in your source code. Use environment variables or a secret manager like IBM Cloud Secrets Manager.
- **Error Handling**: Add more error handling for unsupported event types or invalid payload structures.

By following these steps, you will have a functional Flask webhook handler capable of receiving and processing GitHub webhook events, with OpenAPI documentation for easy reference.


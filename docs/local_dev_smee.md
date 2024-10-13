# Using Smee.io for Local Development

This guide provides detailed instructions for using [Smee.io](https://smee.io) to relay GitHub webhook events to your local development environment. Smee.io is a handy tool for developing applications that need to interact with webhooks when working behind a firewall or without public internet access.

## Why Use Smee.io?
- **Local Development**: Smee.io allows you to receive webhook events on your local machine even if it's not publicly accessible.
- **Easy Integration**: It acts as a webhook proxy that can be configured easily without additional infrastructure.

## Step 1: Set Up Smee.io
1. **Visit Smee.io**:
    - Go to [Smee.io](https://smee.io) and click the **New Channel** button.
    - You will be given a unique Smee channel URL, e.g., `https://smee.io/YOUR_CUSTOM_PATH`. This URL will act as your **Webhook URL** when configuring GitHub.

2. **Configure GitHub Webhook**:
    - When setting up your GitHub App or configuring webhook settings, use the Smee URL as the **Webhook URL**.
    - This URL will receive GitHub events and forward them to your local server.

## Step 2: Install Smee Client
For local development, you'll need to use the Smee client to forward webhooks from Smee.io to your local machine.

1. **Install Node.js** (if not already installed):
    - To install the Smee client, you need [Node.js](https://nodejs.org/). You can download and install it from their official website.

2. **Install Smee Client**:
    - Run the following command to install the Smee client globally:
      ```bash
      npm install --global smee-client
      ```

## Step 3: Forward Events to Your Local Server
1. **Run Smee Client**:
    - Use the following command to start forwarding webhook events to your local machine:
      ```bash
      smee -u https://smee.io/YOUR_CUSTOM_PATH -t http://localhost:8080/webhook
      ```
    - Replace `YOUR_CUSTOM_PATH` with your Smee channel identifier.
    - Replace `http://localhost:8080/webhook` with your local server’s URL where you want to receive the webhook events.

2. **Explanation**:
    - `-u`: The Smee.io channel URL to listen to.
    - `-t`: The target URL on your local machine where the events should be forwarded.

3. **Keep It Running**:
    - Keep the terminal window open where Smee is running to continue forwarding events.

## Step 4: Start Your Local Server
Ensure that your local server is running and configured to receive webhook events at the endpoint you specified (e.g., `/webhook`). This server should listen for POST requests and handle the GitHub events appropriately.

## Step 5: Test the Webhook
1. **Trigger Events from GitHub**:
    - Create or update a pull request in your repository to trigger a webhook event.
    - GitHub will send the webhook to the Smee.io URL, which will then be forwarded to your local server.

2. **Verify Logs**:
    - In your terminal, where the Smee client is running, you should see logs indicating that events have been received and forwarded.
    - Also, check the logs of your local server to verify that it processed the webhook successfully.

## Troubleshooting Tips
1. **Connection Issues**:
    - Ensure that the Smee client is running, and your server is reachable at the specified URL (`http://localhost:8080/webhook`).
    - Verify that your firewall or antivirus is not blocking incoming requests to your local server.

2. **Webhook Not Received**:
    - Make sure the GitHub webhook is properly configured with the correct Smee URL.
    - Verify that the webhook secret matches between your GitHub App and your local server (if using verification).

## Best Practices
1. **Use a Test Repository**:
    - When working locally, it is a good idea to use a test GitHub repository to avoid unintended changes to production repositories.

2. **Debugging Webhooks**:
    - Use the **Recent Deliveries** section under your GitHub App's settings to inspect failed or successful webhook deliveries. It provides useful information like payloads, response codes, and error messages.

## Alternatives to Smee.io
- **Ngrok**: [Ngrok](https://ngrok.com) is another popular tool that creates a secure tunnel to your local machine. It is a more advanced alternative with better security and additional features but requires a sign-up for full functionality.

By using Smee.io, you can easily develop and test webhook functionality locally without needing to expose your local server directly to the internet. This makes it a convenient and effective solution for GitHub integration development.


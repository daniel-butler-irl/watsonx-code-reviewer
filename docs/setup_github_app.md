# Setting Up the GitHub App for WatsonX Code Reviewer

This guide will walk you through the steps to create and configure a GitHub App that integrates with the WatsonX Code Reviewer to automatically review pull requests and provide feedback.

## Prerequisites

- You need **admin** access to the GitHub account or organization where you want to install the app.
- A working **GitHub account**.

## Step-by-Step Guide

### Step 1: Create a GitHub App
1. Go to [GitHub Developer Settings](https://github.com/settings/apps).
2. Click on **New GitHub App**.
3. Fill in the details:
   - **GitHub App name**: Choose a name like "WatsonX Code Reviewer".
   - **Homepage URL**: Use your project’s URL or leave it blank if you don't have one.
   - **Webhook URL**: Set this to the publicly accessible URL where the app can receive events (e.g., use **Smee.io** for local development).
   - **Webhook secret**: Enter a secret key used to verify the payloads received from GitHub.
4. **Permissions & events**:
   - Under **Permissions**, provide read and write access to **Pull requests** and read access to **Labels**.
   - Set the **Subscribe to events** option to include **Pull request** events.
5. **Where can this GitHub App be installed?**
   - Select **Any account**.

### Step 2: Generate Private Key
1. Scroll down to the **Private keys** section.
2. Click **Generate a private key**.
3. This will download a `.pem` file to your computer. Keep it safe as you'll need it to authenticate the app.

### Step 3: Install the GitHub App
1. Once the app is created, click on **Install App**.
2. Select the account or organization where you want to install it.
3. Choose the repositories you want the app to access.
4. To get the **GITHUB_INSTALLATION_ID**, go to the installed app's page, and you'll find it in the URL as a numeric value.

### Step 4: Update Configuration
- Add the following environment variables to your local environment or configuration files:
   - **GITHUB_APP_ID**: The ID of your GitHub App (found on the app's settings page).
   - **GITHUB_INSTALLATION_ID**: The installation ID (found after installing the GitHub App).
   - **GITHUB_PRIVATE_KEY**: The content of the `.pem` file you downloaded.
   - When setting the private key as an environment variable, you can use the following command to convert it to a single line:
     ```bash
     awk '{printf "%s\\n", $0}' private-key.pem
     ```

### Step 5: Use Smee.io for Local Development
- To test locally, use [Smee.io](https://smee.io) to forward GitHub webhooks to your local server.
- Create a new Smee channel and set the **Webhook URL** of your GitHub App to the generated Smee URL.
- Run the Smee client locally:
  ```bash
  npx smee-client --url <smee_url> --target http://localhost:8888/webhook
  ```

## Next Steps
- After setting up the GitHub App, make sure to start the **WatsonX Code Reviewer** to process incoming webhook events and perform pull request reviews.


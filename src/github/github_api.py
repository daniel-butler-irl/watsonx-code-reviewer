import os
import jwt
import time
import requests
from github import Github

class GitHubAPI:
    def __init__(self):
        self.api_url = os.getenv('GITHUB_API_URL', 'https://api.github.com')
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.installation_id = os.getenv('GITHUB_INSTALLATION_ID')
        self.private_key = os.getenv('GITHUB_PRIVATE_KEY')

        # Raise exceptions if required configurations are not set
        if not self.app_id:
            raise ValueError("GITHUB_APP_ID environment variable is not set")
        if not self.installation_id:
            raise ValueError("GITHUB_INSTALLATION_ID environment variable is not set")
        if not self.private_key:
            raise ValueError("GITHUB_PRIVATE_KEY environment variable is not set")

        # Use the official GitHub Python library for authenticated access
        self.github = Github(self.get_installation_token())

    def get_installation_token(self):
        # Generate a JWT for GitHub App authentication
        current_time = int(time.time())
        payload = {
            "iat": current_time,
            "exp": current_time + (10 * 60),  # Token valid for 10 minutes
            "iss": self.app_id
        }
        jwt_token = jwt.encode(payload, self.private_key, algorithm="RS256")

        # Use the JWT to get an installation access token
        url = f"{self.api_url}/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.post(url, headers=headers)
        if response.status_code != 201:
            raise Exception(f"Failed to get installation token: {response.status_code}, {response.text}")
        token = response.json().get("token")
        return token


    def post_review_comment(self, repo_full_name, pull_number, comments):
        repo = self.github.get_repo(repo_full_name)
        pull_request = repo.get_pull(pull_number)
        pull_request.create_review(body=comments, event="COMMENT")


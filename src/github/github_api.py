import os

import jwt
import time
import requests
import logging
from github import Github
from github import GithubException

logger = logging.getLogger(__name__)


class GitHubAPI:
    def __init__(self, app_id=None, installation_id=None, private_key=None, api_url="https://api.github.com"):
        # Set parameters from arguments or environment variables
        self.app_id = os.getenv('GITHUB_APP_ID', app_id)
        self.installation_id = os.getenv('GITHUB_INSTALLATION_ID', installation_id)
        self.private_key = os.getenv('GITHUB_PRIVATE_KEY',private_key)
        self.api_url = os.getenv('GITHUB_API_URL', api_url)

        # Replace \n with actual newlines for the private key
        if self.private_key:
            self.private_key = self.private_key.replace("\\n", "\n")

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

    def get_pull_request(self, repo_name, pr_number):
        repo = self.github.get_repo(repo_name)
        return repo.get_pull(pr_number)

    def get_repository(self, repo_name):
        """
        Get a repository object by name.

        :param repo_name: Full name of the repository (e.g., 'owner/repo').
        :return: Repository object.
        """
        return self.github.get_repo(repo_name)

    def get_review_comments(self, repo_name: str, pr_number: int):
        try:
            repo = self.github.get_repo(repo_name)
            pull_request = repo.get_pull(pr_number)
            comments = pull_request.get_review_comments()
            return [comment for comment in comments]
        except GithubException as e:
            logger.error(f"GitHubException occurred while fetching review comments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Exception occurred while fetching review comments: {str(e)}")
            return []

    def post_review_comment(self, repo_name, pr_number, comments) -> dict:
        try:
            logger.info(f"Attempting to post review comments on PR #{pr_number} in repository '{repo_name}'.")
            # Get repository and pull request information
            repo = self.github.get_repo(repo_name)
            pull_request = repo.get_pull(pr_number)
            commit_id = pull_request.head.sha
            commit = repo.get_commit(commit_id)

            logger.debug(f"Posting Comments: {comments}")
            # Make the request to create a review with comments
            review = pull_request.create_review(
                commit=commit,
                body="Automated code review comments.",
                event='COMMENT',
                comments=comments
            )

            if review.id is not None:
                logger.info(f"Successfully posted review comments on PR #{pr_number} in repository '{repo_name}'.")
                return {'status': 'success', 'message': 'Review comments posted successfully'}
            else:
                logger.warning(f"Unknown failure occurred while posting review comments on PR #{pr_number} in repository '{repo_name}'.")
                return {'status': 'failure', 'message': 'Unknown failure: Review ID is None'}

        except GithubException as e:
            logger.error(f"GitHubException occurred while posting a review: {str(e)}")
            logger.error(f"Exception data: {e.data}")
            if e.status == 403:
                return {'status': 'failure', 'message': 'Forbidden: You may not have permissions to post a comment.'}
            elif e.status == 422:
                logger.error(f"Validation error data: {e.data}")
                return {'status': 'failure', 'message': 'Validation failed: There may be a problem with the request payload.'}
            else:
                return {'status': 'failure', 'message': f'GitHub exception occurred: {str(e)}'}
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error("Stack trace:", exc_info=True)
            return {'status': 'failure', 'message': f'Exception occurred: {str(e)}'}

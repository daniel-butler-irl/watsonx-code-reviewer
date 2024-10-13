import logging

logger = logging.getLogger(__name__)

class ReviewAgent:
    def __init__(self, github_api):
        self.github_api = github_api

    def perform_basic_review(self, repo_name, pr_number):
        review_message = "Basic review agent triggered: Please address the issues in the code."

        logger.info(f"Starting review process for PR #{pr_number} in repository '{repo_name}'.")
        response = self.github_api.post_review_comment(repo_name, pr_number, review_message)

        if response['status'] == 'failure':
            logger.error(f"Failed to post review comment on PR #{pr_number} in repository '{repo_name}': {response['message']}")
        else:
            logger.info(f"Successfully posted review comment on PR #{pr_number} in repository '{repo_name}'.")

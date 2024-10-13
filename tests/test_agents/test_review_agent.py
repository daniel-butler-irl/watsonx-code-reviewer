import pytest
from unittest.mock import MagicMock
from src.agents.review_agent import ReviewAgent
from src.github.github_api import GitHubAPI

@pytest.fixture
def mock_github_api():
    return MagicMock(spec=GitHubAPI)

def test_perform_basic_review(mock_github_api):
    # Instantiate ReviewAgent with the mocked GitHubAPI
    agent = ReviewAgent(github_api=mock_github_api)

    # Define parameters for the review
    repo_name = "test/repo"
    pr_number = 1

    # Perform the basic review
    agent.perform_basic_review(repo_name, pr_number)

    # Verify that post_review_comment was called correctly
    review_message = "Basic review agent triggered: Please address the issues in the code."
    mock_github_api.post_review_comment.assert_called_once_with(repo_name, pr_number, review_message)

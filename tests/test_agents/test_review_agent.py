import pytest
from unittest.mock import MagicMock, patch
from review_agent import ReviewAgent
from src.github.github_api import GitHubAPI

@pytest.fixture
def mock_github_api():
    """
    Fixture to create a mocked GitHubAPI instance.
    """
    return MagicMock(spec=GitHubAPI)

def test_perform_code_review(mock_github_api):
    """
    Test that perform_code_review processes a pull request and posts review comments.
    """
    with patch('src.agents.review_agent.MarkdownReviewAgent') as MockMarkdownAgent:
        # Set up the mock markdown agent
        mock_markdown_agent = MockMarkdownAgent.return_value
        mock_markdown_agent.review.return_value = [
            {'line': 1, 'comment': 'Test comment'}
        ]

        # Instantiate ReviewAgent with the mocked GitHubAPI
        agent = ReviewAgent(github_api=mock_github_api)

        # Define parameters for the review
        repo_name = "test/repo"
        pr_number = 1

        # Mock the pull request and files
        mock_file = MagicMock()
        mock_file.filename = 'README.md'
        mock_file.decoded_content = b'# Sample Markdown content'

        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = [mock_file]

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Verify that post_review_comment was called correctly
        expected_comments = [{
            'path': 'README.md',
            'line': 1,
            'body': 'Test comment',
            'side': 'RIGHT'
        }]

        mock_github_api.post_review_comment.assert_called_once_with(repo_name, pr_number, expected_comments)

        # Assert that the result is as expected
        assert result == {'status': 'success', 'message': 'Review comments posted successfully'}

def test_perform_code_review_no_files(mock_github_api):
    """
    Test that perform_code_review handles a pull request with no files.
    """
    with patch('src.agents.review_agent.MarkdownReviewAgent'):
        agent = ReviewAgent(github_api=mock_github_api)

        repo_name = "test/repo"
        pr_number = 2

        # Mock the pull request with no files
        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = []

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Verify that post_review_comment was not called
        mock_github_api.post_review_comment.assert_not_called()

        # Assert that the result indicates no issues found
        assert result == {'status': 'success', 'message': 'No issues found'}

def test_perform_code_review_no_markdown_files(mock_github_api):
    """
    Test that perform_code_review handles a pull request with non-Markdown files.
    """
    with patch('src.agents.review_agent.MarkdownReviewAgent'):
        agent = ReviewAgent(github_api=mock_github_api)

        repo_name = "test/repo"
        pr_number = 3

        # Mock a non-Markdown file
        mock_file = MagicMock()
        mock_file.filename = 'script.py'
        mock_file.decoded_content = b'print("Hello, World!")'

        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = [mock_file]

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Verify that post_review_comment was not called
        mock_github_api.post_review_comment.assert_not_called()

        # Assert that the result indicates no issues found
        assert result == {'status': 'success', 'message': 'No issues found'}

def test_perform_code_review_markdown_no_comments(mock_github_api):
    """
    Test that perform_code_review handles Markdown files with no review comments.
    """
    with patch('src.agents.review_agent.MarkdownReviewAgent') as MockMarkdownAgent:
        # Set up the mock markdown agent to return no comments
        mock_markdown_agent = MockMarkdownAgent.return_value
        mock_markdown_agent.review.return_value = []

        agent = ReviewAgent(github_api=mock_github_api)

        repo_name = "test/repo"
        pr_number = 4

        # Mock a Markdown file
        mock_file = MagicMock()
        mock_file.filename = 'README.md'
        mock_file.decoded_content = b'# Valid Markdown content'

        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = [mock_file]

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Verify that post_review_comment was not called
        mock_github_api.post_review_comment.assert_not_called()

        # Assert that the result indicates no issues found
        assert result == {'status': 'success', 'message': 'No issues found'}

def test_perform_code_review_post_comment_exception(mock_github_api):
    """
    Test that perform_code_review handles exceptions when posting review comments.
    """
    with patch('src.agents.review_agent.MarkdownReviewAgent') as MockMarkdownAgent:
        # Set up the mock markdown agent to return comments
        mock_markdown_agent = MockMarkdownAgent.return_value
        mock_markdown_agent.review.return_value = [
            {'line': 1, 'comment': 'Test comment'}
        ]

        agent = ReviewAgent(github_api=mock_github_api)

        repo_name = "test/repo"
        pr_number = 5

        # Mock a Markdown file
        mock_file = MagicMock()
        mock_file.filename = 'README.md'
        mock_file.decoded_content = b'# Sample Markdown content'

        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = [mock_file]

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Mock post_review_comment to raise an exception
        mock_github_api.post_review_comment.side_effect = Exception('Failed to post comments')

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Verify that post_review_comment was called
        mock_github_api.post_review_comment.assert_called_once()

        # Assert that the result indicates failure
        assert result['status'] == 'failure'
        assert 'Exception occurred' in result['message']

def test_perform_code_review_exception(mock_github_api):
    """
    Test that perform_code_review handles exceptions during the review process.
    """
    agent = ReviewAgent(github_api=mock_github_api)

    repo_name = "test/repo"
    pr_number = 6

    # Mock get_pull_request to raise an exception
    mock_github_api.get_pull_request.side_effect = Exception('Repository not found')

    # Perform the code review
    result = agent.perform_code_review(repo_name, pr_number)

    # Verify that post_review_comment was not called
    mock_github_api.post_review_comment.assert_not_called()

    # Assert that the result indicates failure
    assert result['status'] == 'failure'
    assert 'Exception occurred' in result['message']
    assert 'Repository not found' in result['message']

import json
import pytest
from unittest.mock import patch, MagicMock
from src.github.webhook_handler import app, set_review_agent
from review_agent import ReviewAgent
from src.github.github_api import GitHubAPI

@pytest.fixture
def client():
    """
    Creates a test client for the Flask application.
    """
    with app.test_client() as client:
        yield client

def test_pull_request_with_ready_label(client):
    """
    Test that a pull request with the 'ready-to-review' label triggers a review.
    """
    # Prepare payload with 'ready-to-review' label
    payload = {
        'action': 'opened',
        'number': 1,
        'repository': {'full_name': 'test/repo'},
        'pull_request': {
            'labels': [{'name': 'ready-to-review'}],
        },
    }

    # Mock the ReviewAgent and set it in the webhook handler
    mock_review_agent = MagicMock(spec=ReviewAgent)
    mock_review_agent.perform_code_review.return_value = {
        'status': 'success',
        'message': 'Review completed successfully'
    }
    set_review_agent(mock_review_agent)

    # Send request to webhook endpoint
    response = client.post('/webhook', data=json.dumps(payload), headers={
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success', 'message': 'Review completed successfully'}
    mock_review_agent.perform_code_review.assert_called_once_with('test/repo', 1)

def test_pull_request_without_ready_label(client):
    """
    Test that a pull request without the 'ready-to-review' label is skipped.
    """
    # Prepare payload without 'ready-to-review' label
    payload = {
        'action': 'opened',
        'number': 2,
        'repository': {'full_name': 'test/repo'},
        'pull_request': {
            'labels': [{'name': 'other-label'}],
        },
    }

    # Send request to webhook endpoint
    response = client.post('/webhook', data=json.dumps(payload), headers={
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {
        'status': 'skipped',
        'message': 'Pull request does not have the label "ready-to-review".'
    }

def test_non_pull_request_event(client):
    """
    Test that events other than 'pull_request' are not processed.
    """
    # Prepare payload for a non-pull_request event
    payload = {'some': 'data'}

    # Send request to webhook endpoint with a different event type
    response = client.post('/webhook', data=json.dumps(payload), headers={
        'X-GitHub-Event': 'push',
        'Content-Type': 'application/json'
    })

    # Assertions
    assert response.status_code == 200  # The endpoint returns 200 even for unprocessed events
    assert response.get_data(as_text=True) == 'Event not processed'

def test_pull_request_event_no_action(client):
    """
    Test that a pull request event without a valid action is not processed.
    """
    # Prepare payload without 'action' field
    payload = {
        'number': 3,
        'repository': {'full_name': 'test/repo'},
        'pull_request': {
            'labels': [{'name': 'ready-to-review'}],
        },
    }

    # Send request to webhook endpoint
    response = client.post('/webhook', data=json.dumps(payload), headers={
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    # Assertions
    assert response.status_code == 200  # The endpoint returns 200 even if action is missing
    assert response.get_data(as_text=True) == 'Event not processed'

def test_pull_request_with_ready_label_no_review_agent(client):
    """
    Test that a pull request with the 'ready-to-review' label fails if the review agent is not initialized.
    """
    # Ensure the review agent is not initialized
    set_review_agent(None)

    # Prepare payload with 'ready-to-review' label
    payload = {
        'action': 'opened',
        'number': 4,
        'repository': {'full_name': 'test/repo'},
        'pull_request': {
            'labels': [{'name': 'ready-to-review'}],
        },
    }

    # Send request to webhook endpoint
    response = client.post('/webhook', data=json.dumps(payload), headers={
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    # Assertions
    assert response.status_code == 500
    assert response.get_json() == {
        'status': 'failure',
        'message': 'Review agent not initialized'
    }

def test_perform_code_review_no_issues_found():
    """
    Test that perform_code_review correctly handles when no issues are found.
    """
    # Instantiate ReviewAgent with a mocked GitHubAPI
    mock_github_api = MagicMock(spec=GitHubAPI)

    with patch('src.agents.review_agent.MarkdownReviewAgent') as MockMarkdownAgent:
        # Set up the mock markdown agent to return no comments
        mock_markdown_agent = MockMarkdownAgent.return_value
        mock_markdown_agent.review.return_value = []

        agent = ReviewAgent(github_api=mock_github_api)

        repo_name = "test/repo"
        pr_number = 2

        # Mock the pull request and files
        mock_file = MagicMock()
        mock_file.filename = 'README.md'

        mock_pull_request = MagicMock()
        mock_pull_request.get_files.return_value = [mock_file]
        mock_pull_request.head.sha = 'def456'

        # Mock get_pull_request to return the pull request
        mock_github_api.get_pull_request.return_value = mock_pull_request

        # Mock the repository and get_contents
        mock_repo = MagicMock()
        mock_file_content = MagicMock()
        mock_file_content.decoded_content = b'# Clean Markdown content'
        mock_repo.get_contents.return_value = mock_file_content

        # Mock get_repository to return the mock_repo
        mock_github_api.get_repository.return_value = mock_repo

        # Perform the code review
        result = agent.perform_code_review(repo_name, pr_number)

        # Assert that the result indicates no issues found
        assert result['status'] == 'success'
        assert 'No issues found' in result['message']

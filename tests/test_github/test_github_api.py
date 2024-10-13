import os
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from unittest.mock import patch, MagicMock
from src.github.github_api import GitHubAPI

def generate_test_private_key():
    # Generate a temporary RSA private key for testing
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode('utf-8')

@pytest.fixture
def github_api():
    with patch('src.github.github_api.Github') as mock_github, \
            patch('src.github.github_api.requests.post') as mock_post:

        # Ensure mock_github has a mock instance to be used in the GitHubAPI instantiation
        mock_github.return_value = MagicMock()

        # Mock the response from GitHub's access token endpoint
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'token': 'mock_installation_token'}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'GITHUB_APP_ID': '123456',
            'GITHUB_INSTALLATION_ID': '654321',
            'GITHUB_PRIVATE_KEY': generate_test_private_key()
        }):
            yield GitHubAPI()

def test_get_installation_token(github_api):
    # Call the method and check the result
    token = github_api.get_installation_token()
    assert token == 'mock_installation_token'

@patch('src.github.github_api.GitHubAPI.get_installation_token')
def test_post_review_comment(mock_get_token, github_api):
    # Mock the installation token retrieval
    mock_get_token.return_value = 'mock_installation_token'

    # Mock the GitHub API
    mock_repo = MagicMock()
    mock_pull_request = MagicMock()
    github_api.github.get_repo.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pull_request

    # Call the method to post a review comment
    github_api.post_review_comment("test/repo", 1, "This is a test review comment.")

    # Verify the expected calls
    mock_repo.get_pull.assert_called_once_with(1)
    mock_pull_request.create_review.assert_called_once_with(body="This is a test review comment.", event="COMMENT")

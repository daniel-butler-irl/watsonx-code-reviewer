import json
import pytest
import hmac
import hashlib
from src.github.webhook_handler import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_signature(client, mocker):
    # Mock GITHUB_SECRET for testing
    mocker.patch('src.github.webhook_handler.GITHUB_SECRET', 'test_secret')

    # Prepare payload and signature
    payload = json.dumps({'action': 'opened', 'number': 1, 'repository': {'full_name': 'test/repo'}}).encode()
    signature = 'sha256=' + hmac.new(b'test_secret', payload, hashlib.sha256).hexdigest()

    # Send request to webhook endpoint
    response = client.post('/webhook', data=payload, headers={
        'X-Hub-Signature-256': signature,
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 200
    assert response.get_json() == {'message': 'Pull request 1 from test/repo received and processed!'}

def test_invalid_signature(client, mocker):
    # Mock GITHUB_SECRET for testing
    mocker.patch('src.github.webhook_handler.GITHUB_SECRET', 'test_secret')

    # Prepare payload and incorrect signature
    payload = json.dumps({'action': 'opened', 'number': 1, 'repository': {'full_name': 'test/repo'}}).encode()
    signature = 'sha256=incorrect_signature'

    # Send request to webhook endpoint
    response = client.post('/webhook', data=payload, headers={
        'X-Hub-Signature-256': signature,
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 403
    assert response.data == b'Invalid event type or signature'

def test_non_pull_request_event(client):
    # Prepare payload for an unsupported event
    payload = json.dumps({'some': 'data'}).encode()

    # Send request to webhook endpoint
    response = client.post('/webhook', data=payload, headers={
        'X-GitHub-Event': 'push',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 403
    assert response.data == b'Invalid event type or signature'

def test_pull_request_event_no_action(client, mocker):
    # Mock GITHUB_SECRET for testing
    mocker.patch('src.github.webhook_handler.GITHUB_SECRET', 'test_secret')

    # Prepare payload and signature
    payload = json.dumps({'number': 1, 'repository': {'full_name': 'test/repo'}}).encode()
    signature = 'sha256=' + hmac.new(b'test_secret', payload, hashlib.sha256).hexdigest()

    # Send request to webhook endpoint
    response = client.post('/webhook', data=payload, headers={
        'X-Hub-Signature-256': signature,
        'X-GitHub-Event': 'pull_request',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 200
    assert response.data == b'Event not processed'

import pytest
import json
from datetime import datetime, timezone, timedelta
from flask import Flask
from flask.testing import FlaskClient
from unittest.mock import patch

from contest.routes import contest_bp
from contest.services import ContestService
from leaderboard.services import complete_contest



# Initialize Flask app for testing
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(contest_bp, url_prefix="/contest")
    app.config['SECRET_KEY'] = "Raghav"  # Secret key for JWT token validation

    @app.before_request
    def before_request():
        from flask import request
        request.environ['REMOTE_USER'] = "test_user"
    return app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def valid_contest_data():
    """
    Return valid contest data for testing creation.
    """
    return {
        "game_id": "' -OGZ3o9kH9PzG6Do52_P",
        "start_time": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": (datetime.now(timezone.utc).replace(hour=23, minute=59, second=59)).strftime('%Y-%m-%d %H:%M:%S'),
        "entry_fee": 10.0,
        "prize_pool": 1000,
        "status": "active",
        "id": "contest1"
    }


# --- Create contest tests ---

@patch("contest.services.ContestService.create_contest")
def test_create_contest_valid(mock_create_contest, client: FlaskClient, valid_contest_data):
    """
    Test case for successfully creating a contest without needing authorization.
    """
    mock_create_contest.return_value = "contest1"  # Mocking contest creation service call

    response = client.post(
        '/contest/create',
        json=valid_contest_data
    )
    assert response.status_code == 200
    assert 'contest_id' in response.json
    assert response.json['contest_id'] == "contest1"


# --- Join contest tests ---

@patch("contest.services.ContestService.join_contest")
def test_join_contest_valid(mock_join_contest, client: FlaskClient, valid_contest_data):
    """
    Test case for successfully joining a contest.
    """
    mock_join_contest.return_value = {'success': True}

    response_create = client.post('/contest/create', json=valid_contest_data)
    assert response_create.status_code == 200
    contest_id = response_create.json['contest_id']

    join_data = {'user_id': 'valid_user', 'contest_id': contest_id}

    response_join = client.post('/contest/join', json=join_data)
    assert response_join.status_code == 200
    assert response_join.json['success'] is True


@patch("contest.services.ContestService.join_contest")
def test_join_contest_insufficient_funds(mock_join_contest, client: FlaskClient, valid_contest_data):
    """
    Test case for failing to join a contest due to insufficient funds.
    """
    mock_join_contest.return_value = {'success': False, 'error': 'Insufficient balance.'}

    response_create = client.post('/contest/create', json=valid_contest_data)
    assert response_create.status_code == 200
    contest_id = response_create.json['contest_id']

    join_data = {'user_id': 'insufficient_funds_user', 'contest_id': contest_id}

    response_join = client.post('/contest/join', json=join_data)
    assert response_join.status_code == 400
    assert response_join.json['error'] == 'Insufficient balance.'


# --- Active contests tests ---

def test_active_contests(client: FlaskClient):
    """
    Test case to retrieve all active contests.
    """
    response = client.get('/contest/active')
    assert response.status_code == 200
    assert response.json is not None


# --- Cancel contest tests ---

@patch("contest.services.ContestService.create_contest")
@patch("contest.services.ContestService.cancel_contest")
def test_cancel_contest_valid(mock_cancel_contest, mock_create_contest, client: FlaskClient, valid_contest_data):
    """
    Test case for successfully canceling a contest.
    """
    # Mock the creation of the contest to return a specific ID
    mock_create_contest.return_value = "contest1"
    mock_cancel_contest.return_value = {'message': 'Contest canceled successfully.'}

    # Simulate creating a contest
    response_create = client.post('/contest/create', json=valid_contest_data)
    assert response_create.status_code == 200
    assert 'contest_id' in response_create.json  # Ensure contest_id is present
    contest_id = response_create.json['contest_id']

    # Simulate canceling the contest
    cancel_data = {'contest_id': contest_id}
    response_cancel = client.post('/contest/cancel', json=cancel_data)

    # Validate the response
    assert response_cancel.status_code == 200
    assert 'message' in response_cancel.json
    assert response_cancel.json['message'] == 'Contest canceled successfully.'


# --- Complete contest tests ---

@patch("leaderboard.services.complete_contest")
def test_complete_contest_valid(mock_complete_contest, client: FlaskClient, valid_contest_data):
    """
    Test case for successfully completing a contest.
    """
    mock_complete_contest.return_value = {'message': 'Contest completed successfully.'}

      # Simulate creating a contest
    response_create = client.post('/contest/create', json=valid_contest_data)
    assert response_create.status_code == 200
    assert 'contest_id' in response_create.json  # Ensure contest_id is present
    contest_id = response_create.json['contest_id']

    complete_data = {'contest_id': contest_id}

    response_complete = client.post('/contest/complete', json=complete_data)
    assert response_complete.status_code == 200
    assert 'message' in response_complete.json
    assert response_complete.json['message'] == 'Contest completed successfully.'


# --- Service Layer Test for ContestService ---

@patch("contest.services.ContestService.create_contest")
def test_create_contest_service(mock_create_contest, valid_contest_data):
    """
    Test the creation logic in the service layer.
    """
    mock_create_contest.return_value = "contest1"
    contest_service = ContestService()
    contest_id = contest_service.create_contest(valid_contest_data)
    assert contest_id == "contest1"


@patch("contest.services.ContestService.join_contest")
def test_join_contest_service(mock_join_contest, valid_contest_data):
    """
    Test the join logic in the service layer.
    """
    mock_join_contest.return_value = {'success': True}

    contest_service = ContestService()
    contest_id = contest_service.create_contest(valid_contest_data)
    join_data = {'user_id': 'valid_user', 'contest_id': contest_id}

    result = contest_service.join_contest(join_data)
    assert result['success'] is True


@patch("contest.services.ContestService.get_active_contests")
def test_get_active_contests_service(mock_get_active_contests):
    """
    Test the active contests fetching logic in the service layer.
    """
    mock_get_active_contests.return_value = [{"contest_id": "contest1", "status": "active"}]

    contest_service = ContestService()
    active_contests = contest_service.get_active_contests()
    assert len(active_contests) > 0


@patch("contest.services.ContestService.cancel_contest")
def test_cancel_contest_service(mock_cancel_contest, valid_contest_data):
    """
    Test the contest cancellation logic in the service layer.
    """
    mock_cancel_contest.return_value = {'message': 'Contest canceled successfully.'}

    contest_service = ContestService()
    contest_id = contest_service.create_contest(valid_contest_data)
    result = contest_service.cancel_contest(contest_id)
    assert result['message'] == 'Contest canceled successfully.'

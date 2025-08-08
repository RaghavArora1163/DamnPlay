from unittest.mock import patch
import pytest

import sys
import os

# Ensure project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


from flask import Flask
from flask.testing import FlaskClient
from leaderboard.routes import leaderboard_blueprint

# Initialize a test Flask application
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(leaderboard_blueprint, url_prefix="/")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Test for fetching the leaderboard
@patch("leaderboard.controllers.fetch_leaderboard")
@pytest.mark.parametrize("contest_id, expected_status, expected_response", [
    ("contest123", 200, {"contest_id": "contest123", "leaderboard": []}),  # Successful fetch
    ("invalid_contest", 404, {"error": "Leaderboard not found for the specified contest"}),  # Contest not found
])
def test_fetch_leaderboard(mock_fetch_leaderboard, client: FlaskClient, contest_id, expected_status, expected_response):
    # Mock service behavior
    if contest_id == "contest123":
        mock_fetch_leaderboard.return_value = []  # Return empty leaderboard
    else:
        mock_fetch_leaderboard.return_value = None  # Contest not found

    response = client.get(f"/leaderboard/{contest_id}")
    assert response.status_code == expected_status
    assert response.get_json() == expected_response

# Test for updating the leaderboard
@patch("leaderboard.controllers.update_leaderboard_entry")
def test_update_leaderboard(mock_update_leaderboard_entry, client: FlaskClient):
    valid_data = {
        "contest_id": "contest123",
        "user_id": "user456",
        "username": "test_user",
        "score": 100
    }
    invalid_data = {
        "contest_id": "contest123",
        "user_id": "user456"
    }

    # Mock successful update
    mock_update_leaderboard_entry.return_value = True
    response = client.post("/update_leaderboard", json=valid_data)
    assert response.status_code == 200
    assert response.get_json() == {"message": "Leaderboard updated successfully"}

    # Mock unsuccessful update (missing required fields)
    response = client.post("/update_leaderboard", json=invalid_data)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields (contest_id, user_id, username, score)"}


# Test for fetching historical leaderboard
@patch("leaderboard.controllers.fetch_historical_leaderboard")
def test_fetch_historical_leaderboard(mock_fetch_historical_leaderboard, client: FlaskClient):
    contest_id = "contest123"

    # Mock successful fetch
    mock_fetch_historical_leaderboard.return_value = [{"user_id": "user456", "score": 100}]
    response = client.get(f"/leaderboard/history/{contest_id}")
    assert response.status_code == 200
    assert response.get_json() == [{"user_id": "user456", "score": 100}]

   
# Test for completing the leaderboard
@patch("leaderboard.controllers.complete_contest")
def test_complete_leaderboard(mock_complete_contest, client: FlaskClient):
    data = {"contest_id": "contest123"}

    # Mock successful completion
    mock_complete_contest.return_value = True  # Simulate successful completion
    response = client.post("/leaderboard/complete", json=data)
    print("this is" ,response)
    assert response.status_code == 200


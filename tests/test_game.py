import pytest

import sys
import os

# Ensure project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from flask import Flask
from game.routes import validate_pagination
from game.controllers import get_all_games
from app import app  # Assuming app is the Flask instance

# Unit Tests
def test_validate_pagination():
    # Valid cases
    validate_pagination(1, 10)  # Should not raise an exception

    # Invalid cases
    with pytest.raises(ValueError, match="Page must be a positive integer."):
        validate_pagination(0, 10)
    
    with pytest.raises(ValueError, match="Limit must be a positive integer."):
        validate_pagination(1, 0)

def test_get_all_games():
    # Test with no filters and default pagination
    games = get_all_games()
    assert isinstance(games, list)

    # Test with filters and pagination
    filtered_games = get_all_games(category="Action", min_popularity=50, page=1, limit=5)
    assert all(game["category"] == "Action" for game in filtered_games)
    assert len(filtered_games) <= 5

# Integration Tests
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_list_games(client):
    # Test API with no filters
    response = client.get("/games")
    assert response.status_code == 200
    data = response.get_json()
    assert "games" in data

    # Test API with filters
    response = client.get("/games?category=Puzzle&min_popularity=30")
    assert response.status_code == 200
    data = response.get_json()
    assert "games" in data
    assert all(game["category"] == "Puzzle" for game in data["games"])

    # Test API with pagination
    response = client.get("/games?page=1&limit=5")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["games"]) <= 5
    assert "total" in data  # Optional: Check if total count is returned
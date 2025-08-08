import pytest
import sys
import os

# Ensure project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from user.services import validate_token, check_user_role
from datetime import datetime, timedelta
import jwt
import datetime

SECRET_KEY = "Raghav"

def create_mock_token(exp_delta_seconds=3600):
    """
    Helper function to create a mock JWT token.
    """
    payload = {
        "user_id": "test_user",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_delta_seconds)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_invalid_token():
    invalid_token = "invalid.token.here"
    with pytest.raises(Exception) as exc_info:
        validate_token(invalid_token)
    assert "Invalid token" in str(exc_info.value)

def test_expired_token():
    expired_token = create_mock_token(exp_delta_seconds=-1)  # Token already expired
    with pytest.raises(Exception) as exc_info:
        validate_token(expired_token)
    assert "Token has expired" in str(exc_info.value)

def test_validate_token_valid():
    payload = {"user_id": "test_user", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    decoded = validate_token(token)
    assert decoded["user_id"] == "test_user"


def test_validate_token_expired():
    payload = {"user_id": "test_user", "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    with pytest.raises(Exception):
        validate_token(token)    

def test_role_mismatch():
    user_roles = ["user"]
    required_role = "admin"
    with pytest.raises(PermissionError) as exc_info:
        check_user_role(user_roles, required_role)
    assert "Role mismatch" in str(exc_info.value)

def test_role_match():
    user_roles = ["admin", "user"]
    required_role = "admin"
    assert check_user_role(user_roles, required_role) is True

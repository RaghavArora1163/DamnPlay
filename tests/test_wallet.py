import pytest
from flask import Flask
from wallet.routes import wallet_bp
from wallet.services import (
    add_funds_service, 
    deduct_funds_service, 
    get_balance_service, 
    get_transaction_history_service,
    deduct_entry_fee, 
    credit_winnings_service
)

# Mock Firebase setup for testing
def mock_get_database_ref():
    class MockDatabaseRef:
        def __init__(self):
            self.data = {}

        def child(self, key):
            if key not in self.data:
                self.data[key] = {}
            self.current_key = key
            return self

        def get(self):
            return self.data.get(self.current_key, {})

        def update(self, updates):
            if self.current_key in self.data:
                self.data[self.current_key].update(updates)

        def push(self):
            return self

        def set(self, value):
            self.data[self.current_key] = value

    return MockDatabaseRef()

# Mock Firebase integration
@pytest.fixture(autouse=True)
def mock_services():
    global mock_db_ref
    mock_db_ref = mock_get_database_ref()

# Setup Flask app for testing
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(wallet_bp, url_prefix="/wallet")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Tests for Balance Retrieval
def test_get_balance_valid_user(client):
    user_id = "test_user"
    mock_db_ref.child(user_id).update({"balance": 100})
    response = client.get(f"/wallet/balance?user_id={user_id}")
    assert response.status_code == 200

def test_get_balance_invalid_user(client):
    response = client.get("/wallet/balance?user_id=")
    assert response.status_code == 400
    assert response.json["error"] == "User ID is required"

# Tests for Adding Funds
def test_add_funds_valid(client):
    user_id = "test_user"
    payload = {"user_id": user_id, "amount": 1000}
    mock_db_ref.child(user_id).update({"balance": 100})
    response = client.post("/wallet/add-funds", json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "Funds added successfully"

def test_add_funds_invalid(client):
    payload = {"user_id": "", "amount": -10}
    response = client.post("/wallet/add-funds", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input"

# Tests for Deducting Funds
def test_deduct_funds_valid(client):
    user_id = "test_user"
    mock_db_ref.child(user_id).update({"balance": 100})
    payload = {"user_id": user_id, "amount": 50}
    response = client.post("/wallet/deduct-funds", json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "Funds deducted successfully"

def test_deduct_funds_insufficient_balance(client):
    user_id = "test_user"
    mock_db_ref.child(user_id).update({"balance": 30})
    payload = {"user_id": user_id, "amount": 50}
    response = client.post("/wallet/deduct-funds", json=payload)
    assert response.status_code == 200

# Tests for Transaction History
def test_get_transaction_history(client):
    user_id = "test_user"
    mock_db_ref.child(user_id).child("transactions").set({
        "txn1": {"type": "deposit", "amount": 100, "timestamp": "2025-01-01T12:00:00"},
        "txn2": {"type": "withdrawal", "amount": 50, "timestamp": "2025-01-02T12:00:00"},
    })
    response = client.get(f"/wallet/transactions?user_id={user_id}")
    assert response.status_code == 200
    transactions = response.json["transactions"]
    assert len(transactions) > 0
    assert transactions[0]["amount"] == 50  # Most recent transaction first

# Tests for Contest Integration
def test_deduct_entry_fee(client):
    user_id = "test_user"
    contest_id = "contest_123"
    mock_db_ref.child(user_id).update({"balance": 100})

    result = deduct_entry_fee(user_id, contest_id, 50)
    print(result)
    assert result["success"] is True

def test_credit_winnings(client):
    user_id = "test_user"
    contest_id = "contest_123"
    mock_db_ref.child(user_id).update({"balance": 100})

    result = credit_winnings_service(user_id, contest_id, 50)
    assert result["message"] == "Winnings credited"

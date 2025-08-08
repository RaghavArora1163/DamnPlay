from flask import jsonify
from wallet.models import get_database_ref
import datetime
import re
from logging_utils import setup_logger

# Configurable daily limits
MAX_DAILY_WITHDRAWAL = 50000  # Example limit
MAX_DAILY_DEPOSIT = 50000     # Example limit

# Set up logger
logger = setup_logger("wallet_services")

# Helper function to sanitize keys
def sanitize_key(key):
    """
    Replace invalid characters in the Firebase path key with underscores.
    Firebase keys cannot include '.', '#', '$', '[', or ']' characters.
    """
    return re.sub(r'[.#$[\]]', '_', key)

# Helper function to get today's date as a string
def get_today_date():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d')

# Helper function to get daily transaction totals
def get_daily_totals(user_id, transaction_type):
    try:
        db_ref = get_database_ref()
        wallet_ref = db_ref.child(user_id)
        daily_totals_ref = wallet_ref.child('daily_totals').child(get_today_date())
        totals = daily_totals_ref.get()
        return totals.get(transaction_type, 0) if totals else 0
    except Exception as e:
        logger.error(f"Error fetching daily totals for user {user_id}: {e}")
        raise

# Helper function to update daily transaction totals
def update_daily_totals(user_id, transaction_type, amount):
    try:
        db_ref = get_database_ref()
        wallet_ref = db_ref.child(user_id)
        daily_totals_ref = wallet_ref.child('daily_totals').child(get_today_date())
        current_total = get_daily_totals(user_id, transaction_type)
        daily_totals_ref.update({transaction_type: current_total + amount})
    except Exception as e:
        logger.error(f"Error updating daily totals for user {user_id}: {e}")
        raise

# Add funds to the wallet
def add_funds_service(user_id, amount):
    if not user_id or amount is None or amount <= 0:
        logger.warning("Invalid input for add_funds_service.")
        return {
            "success": False,
            "message": "Invalid input. User ID and positive amount are required.",
            "data": None
        }, 400

    sanitized_user_id = sanitize_key(user_id)

    try:
        # Check daily deposit limit
        daily_deposit_total = get_daily_totals(sanitized_user_id, 'deposit')
        if daily_deposit_total + amount > MAX_DAILY_DEPOSIT:
            logger.info(f"Daily deposit limit exceeded for user {user_id}.")
            return {
                "success": False,
                "message": "Daily deposit limit exceeded.",
                "data": {
                    "daily_total": daily_deposit_total,
                    "attempted_deposit": amount,
                    "limit": MAX_DAILY_DEPOSIT
                }
            }, 400

        db_ref = get_database_ref()
        wallet_ref = db_ref.child(sanitized_user_id)

        # Fetch current balance
        wallet_data = wallet_ref.get()
        current_balance = wallet_data['balance'] if wallet_data else 0

        # Update balance
        new_balance = current_balance + amount
        wallet_ref.update({'balance': new_balance})

        # Log transaction
        transaction_ref = wallet_ref.child('transactions').push()
        transaction_ref.set({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

        # Update daily totals
        update_daily_totals(sanitized_user_id, 'deposit', amount)

        logger.info(f"Funds added successfully for user {user_id}. New balance: {new_balance}")
        return {
            "success": True,
            "message": "Funds added successfully.",
            "data": {"balance": new_balance}
        }

    except Exception as e:
        logger.error(f"Failed to add funds for user {user_id}: {e}")
        return {
            "success": False,
            "message": "Failed to add funds.",
            "data": {"details": str(e)}
        }, 500

# Deduct funds from the wallet
def deduct_funds_service(user_id, amount):
    if not user_id or amount is None or amount <= 0:
        logger.warning("Invalid input for deduct_funds_service.")
        return {
            "success": False,
            "message": "Invalid input. User ID and positive amount are required.",
            "data": None
        }, 400

    sanitized_user_id = sanitize_key(user_id)

    try:
        # Check daily withdrawal limit
        daily_withdrawal_total = get_daily_totals(sanitized_user_id, 'withdrawal')
        if daily_withdrawal_total + amount > MAX_DAILY_WITHDRAWAL:
            logger.info(f"Daily withdrawal limit exceeded for user {user_id}.")
            return {
                "success": False,
                "message": "Daily withdrawal limit exceeded.",
                "data": {
                    "daily_total": daily_withdrawal_total,
                    "attempted_withdrawal": amount,
                    "limit": MAX_DAILY_WITHDRAWAL
                }
            }, 400

        db_ref = get_database_ref()
        wallet_ref = db_ref.child(sanitized_user_id)

        # Fetch current balance
        wallet_data = wallet_ref.get()
        if not wallet_data:
            logger.warning(f"Wallet not found for user {user_id}.")
            return {
                "success": False,
                "message": "Wallet not found.",
                "data": None
            }, 404

        current_balance = wallet_data['balance']

        # Ensure sufficient balance
        if current_balance >= amount:
            new_balance = current_balance - amount
            wallet_ref.update({'balance': new_balance})

            # Log transaction
            transaction_ref = wallet_ref.child('transactions').push()
            transaction_ref.set({
                'type': 'withdrawal',
                'amount': amount,
                'timestamp': datetime.datetime.utcnow().isoformat()
            })

            # Update daily totals
            update_daily_totals(sanitized_user_id, 'withdrawal', amount)

            logger.info(f"Funds deducted successfully for user {user_id}. New balance: {new_balance}")
            return {
                "success": True,
                "message": "Funds deducted successfully.",
                "data": {"balance": new_balance}
            }
        else:
            logger.warning(f"Insufficient funds for user {user_id}. Current balance: {current_balance}")
            return {
                "success": False,
                "message": "Insufficient funds.",
                "data": {
                    "current_balance": current_balance,
                    "attempted_deduction": amount
                }
            }, 400

    except Exception as e:
        logger.error(f"Failed to deduct funds for user {user_id}: {e}")
        return {
            "success": False,
            "message": "Failed to deduct funds.",
            "data": {"details": str(e)}
        }, 500

# Get wallet balance
def get_balance_service(user_id):
    if not user_id:
        logger.warning("User ID is required for get_balance_service.")
        return {
            "success": False,
            "message": "User ID is required.",
            "data": None
        }, 400

    sanitized_user_id = sanitize_key(user_id)

    try:
        db_ref = get_database_ref()
        wallet_ref = db_ref.child(sanitized_user_id)

        # Fetch current balance
        wallet_data = wallet_ref.get()
        if wallet_data:
            logger.info(f"Balance retrieved for user {user_id}. Balance: {wallet_data['balance']}")
            return {
                "success": True,
                "message": "Wallet balance retrieved successfully.",
                "data": {"balance": wallet_data['balance']}
            }
        else:
            logger.warning(f"Wallet not found for user {user_id}.")
            return {
                "success": False,
                "message": "Wallet not found.",
                "data": None
            }, 404

    except Exception as e:
        logger.error(f"Failed to retrieve wallet balance for user {user_id}: {e}")
        return {
            "success": False,
            "message": "Failed to retrieve wallet balance.",
            "data": {"details": str(e)}
        }, 500

# Get transaction history
def get_transaction_history_service(user_id):
    if not user_id:
        logger.warning("User ID is required for get_transaction_history_service.")
        return {
            "success": False,
            "message": "User ID is required.",
            "data": None
        }, 400

    sanitized_user_id = sanitize_key(user_id)

    try:
        db_ref = get_database_ref()
        transactions_ref = db_ref.child(sanitized_user_id).child('transactions')

        # Fetch all transactions
        transactions = transactions_ref.get()
        if transactions:
            transaction_list = [
                {"id": key, "details": value} for key, value in transactions.items()
            ]
            transaction_list.sort(
                key=lambda x: x['details']['timestamp'], reverse=True
            )
            logger.info(f"Transaction history retrieved for user {user_id}.")
            return {
                "success": True,
                "message": "Transaction history retrieved successfully.",
                "data": transaction_list
            }
        else:
            logger.warning(f"No transactions found for user {user_id}.")
            return {
                "success": False,
                "message": "No transactions found.",
                "data": []
            }

    except Exception as e:
        logger.error(f"Failed to retrieve transaction history for user {user_id}: {e}")
        return {
            "success": False,
            "message": "Failed to retrieve transaction history.",
            "data": {"details": str(e)}
        }, 500
    
# Deduct entry fee for a contest
def deduct_entry_fee(user_id, contest_id, entry_fee):
    if not user_id or not contest_id or entry_fee <= 0:
        logger.warning("Invalid input for deduct_entry_fee.")
        return {'success': False, 'error': 'Invalid input'}, 400

    sanitized_user_id = sanitize_key(user_id)
    sanitized_contest_id = sanitize_key(contest_id)

    try:
        db_ref = get_database_ref()
        wallet_ref = db_ref.child(sanitized_user_id)

        wallet_data = wallet_ref.get()
        if not wallet_data or 'balance' not in wallet_data:
            logger.warning(f"Wallet not found for user {user_id}.")
            return {'success': False, 'error': 'Wallet not found'}, 404

        current_balance = wallet_data['balance']
        if current_balance < entry_fee:
            logger.warning(f"Insufficient balance for user {user_id}. Current balance: {current_balance}, Entry fee: {entry_fee}")
            return {'success': False, 'error': 'Insufficient balance'}, 400

        # Deduct entry fee
        new_balance = current_balance - entry_fee
        wallet_ref.update({'balance': new_balance})

        # Log transaction
        transaction_ref = wallet_ref.child('transactions').push()
        transaction_ref.set({
            'type': 'contest_entry',
            'contest_id': sanitized_contest_id,
            'amount': -entry_fee,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

        logger.info(f"Entry fee of {entry_fee} deducted for user {user_id} for contest {contest_id}. New balance: {new_balance}")
        return {'success': True, 'message': 'Entry fee deducted', 'balance': new_balance}

    except Exception as e:
        logger.error(f"Error deducting entry fee for user {user_id}: {e}")
        return {'success': False, 'error': 'Database error', 'details': str(e)}, 500

# Credit winnings to a user
def credit_winnings_service(user_id, contest_id, winnings):
    if not user_id or not contest_id or winnings <= 0:
        logger.warning("Invalid input for credit_winnings_service.")
        return {'error': 'Invalid input'}, 400

    sanitized_user_id = sanitize_key(user_id)
    sanitized_contest_id = sanitize_key(contest_id)

    try:
        db_ref = get_database_ref()
        wallet_ref = db_ref.child(sanitized_user_id)

        wallet_data = wallet_ref.get()
        current_balance = wallet_data['balance'] if wallet_data else 0

        # Credit winnings
        new_balance = current_balance + winnings
        wallet_ref.update({'balance': new_balance})

        # Log transaction
        transaction_ref = wallet_ref.child('transactions').push()
        transaction_ref.set({
            'type': 'contest_winnings',
            'contest_id': sanitized_contest_id,
            'amount': winnings,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

        logger.info(f"Winnings of {winnings} credited for user {user_id} for contest {contest_id}. New balance: {new_balance}")
        return {'message': 'Winnings credited', 'balance': new_balance}

    except Exception as e:
        logger.error(f"Error crediting winnings for user {user_id}: {e}")
        return {'error': 'Database error', 'details': str(e)}, 500
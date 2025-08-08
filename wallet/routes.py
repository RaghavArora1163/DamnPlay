from flask import Blueprint
from wallet.controller import (
    add_funds_controller,
    deduct_funds_controller,
    get_balance_controller,
    get_transaction_history_controller
)
from utils import standardize_response  # Import the standardize_response utility
from logging_utils import setup_logger

# Initialize logger for the wallet module
logger = setup_logger("wallet_routes")

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/add-funds', methods=['POST'])
def add_funds():
    """
    Route to add funds to a wallet.
    """
    try:
        logger.info("Processing add funds request.")
        result = add_funds_controller()
        logger.info("Funds added successfully.")
        return result  # standardize_response(data=result, message="Funds added successfully", success=True)
    except Exception as e:
        logger.error(f"Failed to add funds: {e}", exc_info=True)
        return standardize_response(data={"details": str(e)}, message="Failed to add funds", success=False)

@wallet_bp.route('/deduct-funds', methods=['POST'])
def deduct_funds():
    """
    Route to deduct funds from a wallet.
    """
    try:
        logger.info("Processing deduct funds request.")
        result = deduct_funds_controller()
        logger.info("Funds deducted successfully.")
        return result  # standardize_response(data=result, message="Funds deducted successfully", success=True)
    except Exception as e:
        logger.error(f"Failed to deduct funds: {e}", exc_info=True)
        return standardize_response(data={"details": str(e)}, message="Failed to deduct funds", success=False)

@wallet_bp.route('/balance', methods=['GET'])
def get_balance():
    """
    Route to get the wallet balance.
    """
    try:
        logger.info("Fetching wallet balance.")
        result = get_balance_controller()
        logger.info("Wallet balance fetched successfully.")
        return result  # standardize_response(data=result, message="Wallet balance fetched successfully", success=True)
    except Exception as e:
        logger.error(f"Failed to fetch wallet balance: {e}", exc_info=True)
        return standardize_response(data={"details": str(e)}, message="Failed to fetch wallet balance", success=False)

@wallet_bp.route('/transactions', methods=['GET'])
def get_transaction_history():
    """
    Route to get the transaction history of a wallet.
    """
    try:
        logger.info("Fetching transaction history.")
        result = get_transaction_history_controller()
        logger.info("Transaction history fetched successfully.")
        return result  # standardize_response(data=result, message="Transaction history fetched successfully", success=True)
    except Exception as e:
        logger.error(f"Failed to fetch transaction history: {e}", exc_info=True)
        return standardize_response(data={"details": str(e)}, message="Failed to fetch transaction history", success=False)

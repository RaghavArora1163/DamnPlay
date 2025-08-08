from flask import request
from wallet.services import (
    add_funds_service,
    deduct_funds_service,
    get_balance_service,
    get_transaction_history_service
)
from utils import standardize_response  # Import the standardize_response utility

def add_funds_controller():
    """
    Controller to handle adding funds to a wallet.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')

        if not user_id or amount is None or amount <= 0:
            return standardize_response(
                data={"details": "Invalid input. User ID and positive amount are required."},
                message="Failed to add funds",
                success=False
            )

        result = add_funds_service(user_id, amount)
        return result  #standardize_response(
        #     data=result,
        #     message="Funds added successfully",
        #     success=True
        #)
    except Exception as e:
        return standardize_response(
            data={"details": str(e)},
            message="Failed to add funds",
            success=False
        )

def deduct_funds_controller():
    """
    Controller to handle deducting funds from a wallet.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')

        if not user_id or amount is None or amount <= 0:
            return standardize_response(
                data={"details": "Invalid input. User ID and positive amount are required."},
                message="Failed to deduct funds",
                success=False
            )

        result = deduct_funds_service(user_id, amount)
        return  result#standardize_response(
            #data=result 
            # message="Funds deducted successfully",
            # success=True
        
    except Exception as e:
        return standardize_response(
            data={"details": str(e)},
            message="Failed to deduct funds",
            success=False
        )

def get_balance_controller():
    """
    Controller to handle fetching the wallet balance.
    """
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return standardize_response(
                data={"details": "User ID is required."},
                message="Failed to fetch wallet balance",
                success=False
            )

        result = get_balance_service(user_id)
        return result #standardize_response(
        #     data=result,
        #     message="Wallet balance fetched successfully",
        #     success=True
        # )
    except Exception as e:
        return standardize_response(
            data={"details": str(e)},
            message="Failed to fetch wallet balance",
            success=False
        )

def get_transaction_history_controller():
    """
    Controller to handle fetching the transaction history of a wallet.
    """
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return standardize_response(
                data={"details": "User ID is required."},
                message="Failed to fetch transaction history",
                success=False
            )

        result = get_transaction_history_service(user_id)
        return result#standardize_response(
        #     data=result,
        #     message="Transaction history fetched successfully",
        #     success=True
        # )
    except Exception as e:
        return standardize_response(
            data={"details": str(e)},
            message="Failed to fetch transaction history",
            success=False
        )

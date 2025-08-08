from flask import Blueprint, request, jsonify
from contest.models import get_contests_ref
from .controllers import (
    create_contest,
    join_contest,
    active_contests,
    cancel_contest,
    complete_contest_controller
)
from user.models import admin_required, token_required
from wallet.services import deduct_entry_fee
from utils import standardize_response
from logging_utils import setup_logger

# Initialize logger
logger = setup_logger("contest_routes")

# Define Blueprint for contest routes
contest_bp = Blueprint('contest', __name__)

# Route for creating a contest (Admin Only)
@contest_bp.route('/create', methods=['POST'])
@token_required
@admin_required
def create(current_user):
    """
    Route to create a new contest.
    Only accessible by admins.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Request body is missing.")
            return jsonify(standardize_response(False, message='Request body is required')), 400

        entry_fee = data.get('entry_fee')
        if entry_fee is None:
            logger.warning("Entry fee missing in request body.")
            return jsonify(standardize_response(False, message='Entry fee is required for contest creation')), 400

        logger.info("Creating a contest with entry fee: %s", entry_fee)
        return create_contest()

    except Exception as e:
        logger.error("Error occurred while creating contest: %s", str(e), exc_info=True)
        return jsonify(standardize_response(False, message='Failed to create contest', data={'details': str(e)})), 500


# Route for joining a contest
@contest_bp.route('/join', methods=['POST'])
@token_required
def join(current_user):
    """
    Route to join a contest.
    Deducts entry fee from the user's wallet.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Request body is missing.")
            return jsonify(standardize_response(False, message='Request body is required')), 400

        contest_id = data.get('contest_id')
        if not contest_id:
            logger.warning("Contest ID missing in request body.")
            return jsonify(standardize_response(False, message='Contest ID is required')), 400

        logger.info("User %s attempting to join contest with ID: %s", current_user.get('user_id'), contest_id)

        # Retrieve contest details
        contest_ref = get_contests_ref().child(contest_id).get()
        if not contest_ref:
            logger.warning("Contest not found for ID: %s", contest_id)
            return jsonify(standardize_response(False, message='Contest not found')), 404

        entry_fee = contest_ref.get('entry_fee')
        if entry_fee is None:
            logger.warning("Entry fee not set for contest ID: %s", contest_id)
            return jsonify(standardize_response(False, message='Contest entry fee not set')), 400

        logger.info("Entry fee for contest ID %s: %s", contest_id, entry_fee)

        # Deduct entry fee and proceed to join the contest
        return join_contest()

    except Exception as e:
        logger.error("Error occurred while joining contest: %s", str(e), exc_info=True)
        return jsonify(standardize_response(False, message='Failed to join contest', data={'details': str(e)})), 500


# Route for retrieving active contests
@contest_bp.route('/active', methods=['GET'])
def active():
    """
    Route to retrieve active contests.
    Accessible without authentication.
    """
    try:
        logger.info("Retrieving active contests.")
        return active_contests()

    except Exception as e:
        logger.error("Error occurred while retrieving active contests: %s", str(e), exc_info=True)
        return jsonify(standardize_response(False, message='Failed to retrieve active contests', data={'details': str(e)})), 500


# Route for canceling a contest (Admin Only)
@contest_bp.route('/cancel', methods=['POST'])
@token_required
@admin_required
def cancel(current_user):
    """
    Route to cancel a contest and refund participants.
    Only accessible by admins.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Request body is missing.")
            return jsonify(standardize_response(False, message='Request body is required')), 400

        contest_id = data.get('contest_id')
        if not contest_id:
            logger.warning("Contest ID missing in request body.")
            return jsonify(standardize_response(False, message='Contest ID is required')), 400

        logger.info("User %s attempting to cancel contest with ID: %s", current_user.get('user_id'), contest_id)

        # Call the cancel_contest logic
        cancel_response, status_code = cancel_contest()
        return cancel_response, status_code

    except Exception as e:
        logger.error("Error occurred while canceling contest: %s", str(e), exc_info=True)
        return jsonify(standardize_response(False, message='Failed to cancel contest', data={'details': str(e)})), 500


# Route for completing a contest (Admin Only)
@contest_bp.route('/complete', methods=['POST'])
@token_required
@admin_required
def complete(current_user):
    """
    Route to complete a contest and archive leaderboard data.
    Only accessible by admins.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Request body is missing.")
            return jsonify(standardize_response(False, message='Request body is required')), 400

        contest_id = data.get('contest_id')
        if not contest_id:
            logger.warning("Contest ID missing in request body.")
            return jsonify(standardize_response(False, message='Contest ID is required')), 400

        logger.info("User %s attempting to complete contest with ID: %s", current_user.get('user_id'), contest_id)

        # Call the complete_contest logic
        return complete_contest_controller(contest_id)

    except Exception as e:
        logger.error("Error occurred while completing contest: %s", str(e), exc_info=True)
        return jsonify(standardize_response(False, message='Failed to complete contest', data={'details': str(e)})), 500

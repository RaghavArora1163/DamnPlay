from flask import request, jsonify
from contest.services import ContestService
from wallet.services import deduct_entry_fee, credit_winnings_service
from leaderboard.services import complete_contest
from .models import get_valid_games
from datetime import datetime
from utils import standardize_response

# Helper function to validate datetime format
def validate_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

# Controller for creating a contest
def create_contest():
    """
    Controller to handle the creation of a new contest.
    """
    data = request.get_json()

    # Validate inputs
    game_id = data.get('game_id')
    prize_pool = data.get('prize_pool')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    entry_fee = data.get('entry_fee')

    if not game_id or not prize_pool or not start_time or not end_time or entry_fee is None:
        return standardize_response(
            success=False, 
            message="Missing required fields (game_id, prize_pool, start_time, end_time, entry_fee)"
        ), 400

    # Validate game_id
    valid_games = get_valid_games()
    valid_game_ids = [game["game_id"] for game in valid_games]

    if game_id not in valid_game_ids:
        return standardize_response(
            success=False, 
            message=f"Invalid game_id. Valid game IDs are: {', '.join(valid_game_ids)}"
        ), 400

    # Validate datetime format
    start_time_dt = validate_datetime(start_time)
    end_time_dt = validate_datetime(end_time)
    if not start_time_dt or not end_time_dt:
        return standardize_response(
            success=False, 
            message="Invalid datetime format. Use YYYY-MM-DD HH:MM:SS"
        ), 400

    # Check start and end time order
    if start_time_dt >= end_time_dt:
        return standardize_response(
            success=False, 
            message="Start time must be before end time"
        ), 400

    # Validate entry fee
    try:
        entry_fee = float(entry_fee)
        if entry_fee < 0:
            return standardize_response(
                success=False, 
                message="Entry fee must be a non-negative value"
            ), 400
    except ValueError:
        return standardize_response(
            success=False, 
            message="Entry fee must be a valid number"
        ), 400

    # Delegate to service for further validation and creation
    try:
        result = ContestService.create_contest(data)
        response_data, status_code = result
        return jsonify(response_data), status_code
    except Exception as e:
        return standardize_response(
            success=False, 
            message="Failed to create contest", 
            data={"error": str(e)}
        ), 500

# Controller for joining a contest
def join_contest():
    """
    Controller to handle joining a contest.
    Deducts the entry fee dynamically and updates participation.
    """
    data = request.get_json()

    user_id = data.get('user_id')
    contest_id = data.get('contest_id')

    if not user_id or not contest_id:
        return standardize_response(
            success=False, 
            message="Missing required fields (user_id, contest_id)"
        ), 400

    try:
        # Fetch contest details and validate
        contest_details = ContestService.get_contest_by_id(contest_id)
        print(contest_details)
        if not contest_details:
            return standardize_response(
                success=False, 
                message=f"Contest with ID {contest_id} not found"
            ), 404

        entry_fee = contest_details.get('entry_fee')
        if entry_fee is None:
            return standardize_response(
                success=False, 
                message="Entry fee is not defined for this contest"
            ), 400

        # Deduct entry fee from user's wallet
        deduction_response = deduct_entry_fee(user_id=user_id, contest_id=contest_id, entry_fee=entry_fee)
        print(deduction_response)
        if not deduction_response.get('success'):
            return standardize_response(
                success=False, 
                message="Failed to deduct entry fee", 
                data={"error": deduction_response.get('error')}
            ), 400

        # Proceed to join the contest
        result = ContestService.join_contest(data)
        print(result)
        response_data, status_code = result
        return jsonify(response_data), status_code

    except Exception as e:
        return standardize_response(
            success=False, 
            message="Failed to join contest", 
            data={"error": str(e)}
        ), 500

# Controller for retrieving active contests
def active_contests():
    """
    Controller to retrieve active contests.
    """
    try:
        result = ContestService.get_active_contests()
        return standardize_response(
            result
        ), 200
    except Exception as e:
        return standardize_response(
            success=False, 
            message="Failed to retrieve active contests", 
            data={"error": str(e)}
        ), 500

# Controller for canceling a contest
def cancel_contest():
    """
    Controller to handle the cancellation of a contest.
    Refunds participants and updates contest status.
    """
    data = request.get_json()
    contest_id = data.get('contest_id')

    if not contest_id:
        return standardize_response(
            success=False, 
            message="Missing required field: contest_id"
        ), 400

    try:
        result = ContestService.cancel_contest(contest_id)
        response_data, status_code = result
        return jsonify(response_data), status_code
    except Exception as e:
        return standardize_response(
            success=False, 
            message="Failed to cancel contest", 
            data={"error": str(e)}
        ), 500

# Controller for completing a contest
def complete_contest_controller():
    """
    Controller to handle the completion of a contest and archive its leaderboard data.
    """
    data = request.get_json()
    contest_id = data.get('contest_id')

    if not contest_id:
        return standardize_response(
            success=False, 
            message="Missing required field: contest_id"
        ), 400

    try:
        # Delegate to service to complete the contest
        result = complete_contest(contest_id)
        return standardize_response(
            success=True, 
            data=result, 
            message="Contest completed successfully"
        ), 200
    except Exception as e:
        return standardize_response(
            success=False, 
            message="Failed to complete contest", 
            data={"error": str(e)}
        ), 500

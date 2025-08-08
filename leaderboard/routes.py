from flask import Blueprint
from utils import standardize_response  # Import the standardize_response function
from logging_utils import setup_logger  # Import the logger setup function

# Define the leaderboard blueprint
leaderboard_blueprint = Blueprint('leaderboard', __name__)

# Initialize the logger
logger = setup_logger("leaderboard_routes")

@leaderboard_blueprint.route('/leaderboard/<contest_id>', methods=['GET'])
def fetch_leaderboard_route(contest_id):
    """
    Fetch the current leaderboard for an active contest.
    """
    from .controllers import get_leaderboard  # Import here to avoid circular import
    try:
        logger.info(f"Fetching leaderboard for contest_id: {contest_id}")
        result = get_leaderboard(contest_id)
        logger.info(f"Leaderboard fetched successfully for contest_id: {contest_id}")
        return  result #standardize_response(data=result, message="Leaderboard fetched successfully", success=True)
    except Exception as e:
        logger.error(f"Error fetching leaderboard for contest_id: {contest_id}, Error: {str(e)}")
        return standardize_response(data={"details": str(e)}, message="Failed to fetch leaderboard", success=False), 500

@leaderboard_blueprint.route('/update_leaderboard', methods=['POST'])
def update_leaderboard_route():
    """
    Update the leaderboard for an active contest.
    """
    from .controllers import modify_leaderboard  # Import here to avoid circular import
    try:
        logger.info("Updating leaderboard for an active contest")
        result = modify_leaderboard()
        logger.info("Leaderboard updated successfully")
        return  result#standardize_response(data=result, message="Leaderboard updated successfully", success=True)
    except Exception as e:
        logger.error(f"Error updating leaderboard, Error: {str(e)}")
        return standardize_response(data={"details": str(e)}, message="Failed to update leaderboard", success=False), 500

@leaderboard_blueprint.route('/leaderboard/history/<contest_id>', methods=['GET'])
def fetch_historical_leaderboard_route(contest_id):
    """
    Fetch the historical leaderboard for a completed contest.
    """
    from .controllers import get_historical_leaderboard  # Import here to avoid circular import
    try:
        logger.info(f"Fetching historical leaderboard for contest_id: {contest_id}")
        result = get_historical_leaderboard(contest_id)
        logger.info(f"Historical leaderboard fetched successfully for contest_id: {contest_id}")
        return standardize_response(data=result, message="Historical leaderboard fetched successfully", success=True)
    except Exception as e:
        logger.error(f"Error fetching historical leaderboard for contest_id: {contest_id}, Error: {str(e)}")
        return standardize_response(data={"details": str(e)}, message="Failed to fetch historical leaderboard", success=False), 500

@leaderboard_blueprint.route('/leaderboard/complete', methods=['POST'])
def complete_leaderboard_route():
    """
    Complete a contest and archive its leaderboard.
    """
    from .controllers import complete_contest_route  # Import here to avoid circular import
    try:
        logger.info("Completing a contest and archiving its leaderboard")
        result = complete_contest_route()
        logger.info("Contest completed and leaderboard archived successfully")
        return standardize_response(data=result, message="Contest completed successfully", success=True)
    except Exception as e:
        logger.error(f"Error completing contest and archiving leaderboard, Error: {str(e)}")
        return standardize_response(data={"details": str(e)}, message="Failed to complete contest", success=False), 500

from flask import jsonify, request
from leaderboard.services import (
    fetch_leaderboard,
    update_leaderboard_entry,
    fetch_historical_leaderboard,
    complete_contest
)
from utils import standardize_response

def get_leaderboard(contest_id):
    """
    Fetch the current leaderboard for an active contest.
    """
    try:
        leaderboard_data = fetch_leaderboard(contest_id)
        return {
            "leaderboard": leaderboard_data
        }
    except Exception as e:
        raise Exception(f"Error fetching leaderboard: {str(e)}")

def modify_leaderboard():
    """
    Update the leaderboard for a contest by adding/updating entries.
    This assumes the required data is provided in the request body.
    """
    from flask import request
    try:
        # Parse request JSON for required parameters
        data = request.get_json()
        contest_id = data.get('contest_id')
        user_id = data.get('user_id')
        username = data.get('username')
        score = data.get('score')

        # Validate input
        if not contest_id or not user_id or username is None or score is None:
            raise ValueError("Missing required parameters: 'contest_id', 'user_id', 'username', or 'score'")

        # Call the update_leaderboard_entry function with the required arguments
        success = update_leaderboard_entry(contest_id, user_id, username, score)
        if success:
            return standardize_response(
                data={"contest_id": contest_id, "user_id": user_id},
                message="Leaderboard updated successfully",
                success=True
            )
        else:
            return standardize_response(
                data={"contest_id": contest_id, "user_id": user_id},
                message="Failed to update leaderboard",
                success=False
            )

    except Exception as e:
        print(f"Error updating leaderboard: {e}")
        return standardize_response(
            data={"details": f"Error updating leaderboard: {str(e)}"},
            message="Failed to update leaderboard",
            success=False
        )

def get_historical_leaderboard(contest_id):
    """
    Fetch historical leaderboard for a completed contest.
    """
    try:
        historical_data = fetch_historical_leaderboard(contest_id)
        return {
            "historical_leaderboard": historical_data
        }
    except Exception as e:
        raise Exception(f"Error fetching historical leaderboard: {str(e)}")

def complete_contest_route():
    """
    Complete a contest and archive its leaderboard.
    """
    try:
        contest_id = request.json.get("contest_id")
        result = complete_contest(contest_id)
        return {
            "completion_status": result
        }
    except Exception as e:
        raise Exception(f"Error completing contest: {str(e)}")

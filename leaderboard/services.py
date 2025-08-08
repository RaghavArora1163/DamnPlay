from datetime import datetime
from firebase_admin import db
from leaderboard.models import LeaderboardEntry
from wallet.services import credit_winnings_service
from functools import lru_cache
from utils import standardize_response
from logging_utils import setup_logger

# Initialize logger
logger = setup_logger("leaderboard_services")

# Firebase database references
leaderboard_ref = db.reference('leaderboards')
contests_ref = db.reference('contests')
completed_contests_ref = db.reference('completed_contests')

# Helper function to validate datetime format
def validate_datetime(datetime_str):
    """
    Validate a datetime string against the format '%Y-%m-%d %H:%M:%S'.

    :param datetime_str: String to validate
    :return: datetime object if valid, None otherwise
    """
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logger.error(f"Invalid datetime format: {datetime_str}")
        return None

@lru_cache(maxsize=128)
def get_leaderboard_data(contest_id):
    """
    Fetch leaderboard data from the database and cache it.

    :param contest_id: The ID of the contest
    :return: Leaderboard data dictionary
    """
    logger.info(f"Fetching leaderboard data for contest_id: {contest_id}")
    return leaderboard_ref.child(contest_id).get()

@lru_cache(maxsize=128)
def get_contest_data(contest_id):
    """
    Fetch contest data from the database and cache it.

    :param contest_id: The ID of the contest
    :return: Contest data dictionary
    """
    logger.info(f"Fetching contest data for contest_id: {contest_id}")
    return contests_ref.child(contest_id).get()

def fetch_leaderboard(contest_id):
    """
    Fetch and rank leaderboard data for a given contest ID, handling ties and missing submissions.

    :param contest_id: The ID of the contest
    :return: Standardized response with leaderboard entries or error details
    """
    try:
        logger.info(f"Fetching leaderboard for contest_id: {contest_id}")
        leaderboard_data = get_leaderboard_data(contest_id)
        contest_data = get_contest_data(contest_id)

        if not leaderboard_data:
            logger.warning(f"No leaderboard data found for contest {contest_id}")
            return standardize_response(data=None, message=f"No leaderboard data found for contest {contest_id}", success=False)

        participants = contest_data.get('participants', []) if contest_data else []
        for participant in participants:
            if participant not in leaderboard_data:
                leaderboard_data[participant] = {
                    'username': 'Unknown',
                    'score': 0
                }

        sorted_leaderboard = sorted(
            leaderboard_data.items(),
            key=lambda x: x[1].get('score', 0),
            reverse=True
        )

        result = []
        rank = 1
        previous_score = None
        tied_ranks = 0

        for i, (user_id, user_data) in enumerate(sorted_leaderboard):
            current_score = user_data.get('score', 0)

            if previous_score is not None:
                if current_score < previous_score:
                    rank += tied_ranks + 1
                    tied_ranks = 0
                else:
                    tied_ranks += 1

            previous_score = current_score

            entry = LeaderboardEntry(
                user_id=user_id,
                contest_id=contest_id,
                timestamp=datetime.now(),
                username=user_data.get('username', 'Unknown'),
                score=current_score,
                rank=rank
            )
            result.append(entry.to_dict())

        logger.info(f"Successfully fetched leaderboard for contest_id: {contest_id}")
        return standardize_response(data=result, message="Leaderboard fetched successfully", success=True)

    except Exception as e:
        logger.exception(f"Failed to fetch leaderboard for contest_id: {contest_id}")
        return standardize_response(data={"details": str(e)}, message="Failed to fetch leaderboard", success=False)

def update_leaderboard_entry(contest_id, user_id, username, score):
    """
    Update or add a leaderboard entry for a specific contest and user.

    :param contest_id: The ID of the contest
    :param user_id: The ID of the user
    :param username: The username of the user
    :param score: The score of the user
    :return: Standardized response with success or error details
    """
    try:
        logger.info(f"Updating leaderboard entry for user_id: {user_id} in contest_id: {contest_id}")
        contest = get_contest_data(contest_id)
        if not contest:
            logger.warning(f"Contest {contest_id} does not exist.")
            return standardize_response(data=None, message=f"Contest {contest_id} does not exist.", success=False)

        leaderboard_ref.child(contest_id).child(user_id).set({
            'username': username,
            'score': score
        })

        get_leaderboard_data.cache_clear()
        logger.info(f"Successfully updated leaderboard entry for user_id: {user_id} in contest_id: {contest_id}")
        return standardize_response(data=None, message="Leaderboard entry updated successfully", success=True)

    except Exception as e:
        logger.exception(f"Failed to update leaderboard entry for user_id: {user_id} in contest_id: {contest_id}")
        return standardize_response(data={"details": str(e)}, message="Failed to update leaderboard entry", success=False)

def complete_contest(contest_id):
    """
    Mark a contest as completed, distribute winnings among rank 1 holders equally, 
    update contest status, and archive its leaderboard data.

    :param contest_id: The ID of the contest
    :return: Standardized response with success or error details
    """
    try:
        logger.info(f"Completing contest_id: {contest_id}")
        leaderboard_data = get_leaderboard_data(contest_id)
        contest_data = get_contest_data(contest_id)

        if not leaderboard_data:
            logger.warning(f"No leaderboard data found for contest {contest_id}")
            return standardize_response(data=None, message=f"No leaderboard data found for contest {contest_id}", success=False)

        if not contest_data:
            logger.warning(f"Contest data not found for contest {contest_id}")
            return standardize_response(data=None, message=f"Contest data not found for contest {contest_id}", success=False)

        prize_pool = contest_data.get("prize_pool", 0)
        if prize_pool <= 0:
            logger.error(f"Invalid prize pool for contest {contest_id}")
            return standardize_response(data=None, message=f"Invalid prize pool for contest {contest_id}", success=False)

        sorted_leaderboard = sorted(
            leaderboard_data.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )

        result = []
        rank = 1
        previous_score = None
        tied_ranks = 0
        rank_1_holders = []

        for user_id, user_data in sorted_leaderboard:
            current_score = user_data.get('score', 0)

            if previous_score is not None:
                if current_score < previous_score:
                    rank += tied_ranks + 1
                    tied_ranks = 0
                else:
                    tied_ranks += 1

            previous_score = current_score

            if rank == 1:
                rank_1_holders.append(user_id)

            entry = LeaderboardEntry(
                user_id=user_id,
                contest_id=contest_id,
                timestamp=datetime.now(),
                username=user_data.get("username", "Unknown"),
                score=current_score,
                rank=rank
            )
            entry_dict = entry.to_dict()
            entry_dict['timestamp'] = entry_dict['timestamp'].isoformat()
            result.append(entry_dict)

        if rank_1_holders:
            prize_per_user = prize_pool / len(rank_1_holders)
            for user_id in rank_1_holders:
                credit_winnings_service(user_id, contest_id, prize_per_user)

        completed_data = {
            "leaderboard": result,
            "completed_at": datetime.now().isoformat()
        }

        completed_contests_ref.child(contest_id).set(completed_data)
        contests_ref.child(contest_id).update({"status": "completed"})
        leaderboard_ref.child(contest_id).delete()

        logger.info(f"Successfully completed contest_id: {contest_id}")
        return standardize_response(data=None, message=f"Contest {contest_id} completed successfully", success=True)

    except Exception as e:
        logger.exception(f"Failed to complete contest_id: {contest_id}")
        return standardize_response(data={"details": str(e)}, message="Failed to complete contest", success=False)

def fetch_historical_leaderboard(contest_id):
    """
    Fetch the historical leaderboard data for a completed contest.

    :param contest_id: The ID of the completed contest
    :return: Standardized response with historical leaderboard data or error details
    """
    try:
        logger.info(f"Fetching historical leaderboard for contest_id: {contest_id}")
        data = completed_contests_ref.child(contest_id).get()
        if not data:
            logger.warning(f"No historical data found for contest {contest_id}")
            return standardize_response(data=None, message=f"No historical data found for contest {contest_id}", success=False)

        logger.info(f"Successfully fetched historical leaderboard for contest_id: {contest_id}")
        return standardize_response(data=data, message="Historical leaderboard fetched successfully", success=True)

    except Exception as e:
        logger.exception(f"Failed to fetch historical leaderboard for contest_id: {contest_id}")
        return standardize_response(data={"details": str(e)}, message="Failed to fetch historical leaderboard", success=False)

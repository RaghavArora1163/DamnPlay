from datetime import datetime
from contest.models import get_contests_ref, get_user_contest_mapping_ref, get_valid_games
from wallet.services import deduct_funds_service, add_funds_service
from utils import standardize_response
from logging_utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

class ContestService:
    @staticmethod
    def validate_datetime(datetime_str):
        """Validate and parse a datetime string."""
        try:
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            logger.error("Invalid datetime format: %s", datetime_str)
            return None

    @staticmethod
    def validate_required_fields(data, required_fields):
        """Check if required fields are present in the data."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.warning("Missing required fields: %s", ", ".join(missing_fields))
            return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400
        return None

    @staticmethod
    def validate_game_id(game_id):
        """Validate the provided game ID against valid game IDs."""
        valid_games = get_valid_games()
        valid_game_ids = [game["game_id"] for game in valid_games]

        if game_id not in valid_game_ids:
            logger.warning("Invalid game_id: %s. Valid game IDs are: %s", game_id, ", ".join(valid_game_ids))
            return {'error': f"Invalid game_id. Valid game IDs are: {', '.join(valid_game_ids)}"}, 400
        return None

    @staticmethod
    def check_contest_overlap(game_id, start_time, end_time):
        """
        Check if a new contest overlaps with existing contests for the same game ID.
        """
        contests_ref = get_contests_ref()
        existing_contests = contests_ref.order_by_child("game_id").equal_to(game_id).get()

        if existing_contests:
            new_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            new_end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

            for contest_id, contest in existing_contests.items():
                if isinstance(contest, dict):  # Ensure contest is a dictionary
                    existing_start = datetime.strptime(contest["start_time"], '%Y-%m-%d %H:%M:%S')
                    existing_end = datetime.strptime(contest["end_time"], '%Y-%m-%d %H:%M:%S')

                    # Check if the contests overlap
                    if new_start < existing_end and new_end > existing_start:
                        logger.warning(
                            "Contest overlap detected. New contest conflicts with existing contest ID: %s", contest_id
                        )
                        return {
                            "error": f"Contest overlaps with an existing contest (ID: {contest_id})"
                        }, 400

        return None

    @staticmethod
    def create_contest(data):
        """Create a new contest."""
        logger.info("Creating a new contest with data: %s", data)

        # Validate required fields
        required_fields = ['game_id', 'prize_pool', 'start_time', 'end_time', 'entry_fee']
        field_validation = ContestService.validate_required_fields(data, required_fields)
        if field_validation:
            return standardize_response(success=False, message=field_validation[0]['error'], data=None), field_validation[1]

        # Validate game ID
        game_id = data.get('game_id')
        game_validation = ContestService.validate_game_id(game_id)
        if game_validation:
            return standardize_response(success=False, message=game_validation[0]['error'], data=None), game_validation[1]

        # Validate datetime format
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        start_time_dt = ContestService.validate_datetime(start_time)
        end_time_dt = ContestService.validate_datetime(end_time)
        if not start_time_dt or not end_time_dt:
            return standardize_response(success=False, message='Invalid datetime format. Use YYYY-MM-DD HH:MM:SS', data=None), 400

        if start_time_dt >= end_time_dt:
            logger.error("Start time must be before end time: %s >= %s", start_time, end_time)
            return standardize_response(success=False, message='Start time must be before end time', data=None), 400

        # Check for contest overlap
        overlap_error = ContestService.check_contest_overlap(game_id, start_time, end_time)
        if overlap_error:
            return standardize_response(success=False, message=overlap_error[0]['error'], data=None), overlap_error[1]

        # Validate entry fee
        try:
            entry_fee = float(data.get('entry_fee'))
            if entry_fee < 0:
                logger.error("Entry fee must be a non-negative value: %s", entry_fee)
                return standardize_response(success=False, message='Entry fee must be a non-negative value', data=None), 400
        except ValueError:
            logger.error("Entry fee must be a valid number: %s", data.get('entry_fee'))
            return standardize_response(success=False, message='Entry fee must be a valid number', data=None), 400

        # Save contest to Firebase
        contest_id = get_contests_ref().push().key
        contest = {
            'id': contest_id,
            'game_id': game_id,
            'prize_pool': data['prize_pool'],
            'start_time': start_time,
            'end_time': end_time,
            'entry_fee': entry_fee,
            'status': 'active',
        }
        get_contests_ref().child(contest_id).set(contest)
        logger.info("Contest created successfully with ID: %s", contest_id)

        # Return standardized success response
        return standardize_response(
            success=True,
            message="Contest created successfully",
            data=contest
        ), 201

    @staticmethod
    def join_contest(data):
        """Allow a user to join a contest."""
        logger.info("Joining contest with data: %s", data)

        # Validate required fields
        required_fields = ['user_id', 'contest_id']
        field_validation = ContestService.validate_required_fields(data, required_fields)
        if field_validation:
            return standardize_response(success=False, message=field_validation[0]['error'], data=None), field_validation[1]

        user_id = data.get('user_id')
        contest_id = data.get('contest_id')

        # Check if contest exists
        contest = ContestService.get_contest_by_id(contest_id)
        if not contest:
            logger.error("Contest with ID '%s' not found.", contest_id)
            return standardize_response(success=False, message=f"Contest with ID '{contest_id}' not found.", data=None), 404

        # Fetch entry fee from the contest
        entry_fee = contest.get('entry_fee')
        if entry_fee is None:
            logger.error("Entry fee not found for contest ID '%s'.", contest_id)
            return standardize_response(success=False, message=f"Entry fee not found for contest ID '{contest_id}'.", data=None), 400

        # Check if the contest has started
        current_time = datetime.now()
        start_time_dt = ContestService.validate_datetime(contest['start_time'])
        if current_time >= start_time_dt:
            logger.warning("Cannot join a contest after it has started: Contest ID '%s'", contest_id)
            return standardize_response(success=False, message='Cannot join a contest after it has started.', data=None), 400

        # Check if user is already joined
        user_list = get_user_contest_mapping_ref().child(contest_id).get() or []
        if user_id in user_list:
            logger.info("User '%s' has already joined contest '%s'.", user_id, contest_id)
            return standardize_response(success=False, message=f"User '{user_id}' has already joined the contest.", data=None), 400

        # Add user to the contest
        user_list.append(user_id)
        get_user_contest_mapping_ref().child(contest_id).set(user_list)
        logger.info("User '%s' joined contest '%s' successfully.", user_id, contest_id)

        # Return standardized success response
        return standardize_response(
            success=True,
            message="User joined the contest successfully.",
            data={
                'user_id': user_id,
                'contest_id': contest_id
            }
        ), 200

    @staticmethod
    def get_active_contests():
        """
        Retrieve active contests.
        A contest is considered active if the current time falls within its start and end times.
        """
        try:
            current_time = datetime.now()
            contests = get_contests_ref().get() or {}

            active_contests_list = []
            for contest_id, contest in contests.items():
                if isinstance(contest, dict):
                    start_time_dt = ContestService.validate_datetime(contest['start_time'])
                    end_time_dt = ContestService.validate_datetime(contest['end_time'])

                    if start_time_dt and end_time_dt and start_time_dt <= current_time <= end_time_dt:
                        active_contests_list.append({**contest, "id": contest_id})

            logger.info("Active contests retrieved successfully.")
            return standardize_response(
                success=True,
                message="Active contests retrieved successfully.",
                data={"active_contests": active_contests_list}
            ), 200

        except Exception as e:
            logger.exception("Failed to retrieve active contests.")
            return standardize_response(
                success=False,
                message="Failed to retrieve active contests.",
                data={"details": str(e)}
            ), 500

    @staticmethod
    def cancel_contest(contest_id):
        """
        Cancel a contest and refund all participants.
        A contest can only be canceled if it exists and is not already canceled.
        """
        try:
            logger.info("Canceling contest with ID: %s", contest_id)

            # Fetch contest details
            contests_ref = get_contests_ref()
            contest = contests_ref.child(contest_id).get()

            if not contest:
                logger.error("Contest with ID '%s' not found.", contest_id)
                return standardize_response(
                    success=False,
                    message=f"Contest with ID '{contest_id}' not found.",
                    data={}
                ), 404

            # Check if contest is already canceled
            if contest.get('status') == 'canceled':
                logger.warning("Contest with ID '%s' is already canceled.", contest_id)
                return standardize_response(
                    success=False,
                    message="Contest is already canceled.",
                    data={}
                ), 400

            # Refund participants
            user_contest_mapping_ref = get_user_contest_mapping_ref()
            participants = user_contest_mapping_ref.child(contest_id).get() or []

            for user_id in participants:
                entry_fee = contest.get('entry_fee', 0)
                refund_response = add_funds_service(user_id, entry_fee)
                print(refund_response)

                # Check if refund was successful
                if not refund_response['success']:
                    logger.error(
                        "Failed to refund participant '%s' for contest '%s'.", user_id, contest_id
                    )
                    return standardize_response(
                        success=False,
                        message=f"Failed to refund participant {user_id}.",
                        data={"details": refund_response.get('error', 'Unknown error')}
                    ), 500

            # Mark contest as canceled
            contests_ref.child(contest_id).update({'status': 'canceled'})

            # Remove participants (optional cleanup)
            user_contest_mapping_ref.child(contest_id).delete()
            logger.info("Contest '%s' has been canceled successfully.", contest_id)

            return standardize_response(
                success=True,
                message=f"Contest '{contest_id}' has been canceled, and all participants have been refunded.",
                data={}
            ), 200

        except Exception as e:
            logger.exception("An error occurred while canceling the contest.")
            return standardize_response(
                success=False,
                message="An error occurred while canceling the contest.",
                data={"details": str(e)}
            ), 500

    @staticmethod
    def get_contest_by_id(contest_id):
        """Retrieve a contest by its ID."""
        contest = get_contests_ref().child(contest_id).get()
        if contest:
            logger.info("Contest retrieved successfully with ID: %s", contest_id)
        else:
            logger.warning("Contest with ID '%s' not found.", contest_id)
        return contest if contest else None

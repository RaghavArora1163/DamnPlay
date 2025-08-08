from .models import get_games_collection
from logging_utils import setup_logger

# Initialize the logger for this module
logger = setup_logger("game_services")

def calculate_popularity(game_id):
    """
    Calculate the popularity score for a specific game.

    Args:
        game_id (str): The ID of the game.
    Returns:
        dict: A dictionary containing the game ID and its calculated popularity score,
              or an error message if the game is not found.
    """
    try:
        # Log the calculation process
        logger.info("Calculating popularity for game_id: %s", game_id)

        # Fetch the game document
        games_ref = get_games_collection()
        game_doc = games_ref.document(game_id).get()

        if not game_doc.exists:
            logger.warning("Game not found for game_id: %s", game_id)
            return {"error": "Game not found"}

        # Retrieve game data and calculate popularity
        game_data = game_doc.to_dict()
        popularity_score = game_data.get("average_rating", 0) * 20

        logger.info("Popularity score calculated for game_id: %s, score: %s", game_id, popularity_score)
        return {"game_id": game_id, "popularity": popularity_score}

    except Exception as e:
        logger.error("Error occurred while calculating popularity for game_id: %s, error: %s", game_id, str(e), exc_info=True)
        return {"error": "An unexpected error occurred while calculating popularity."}


def validate_game_data(data):
    """
    Validate the game data for required fields.

    Args:
        data (dict): The input game data.
    Returns:
        dict: None if all fields are valid, or an error dictionary if a field is missing.
    """
    try:
        # Log the validation process
        logger.info("Validating game data: %s", data)

        required_fields = ["title", "category", "description", "release_year"]
        for field in required_fields:
            if field not in data:
                logger.warning("Validation failed, missing field: %s", field)
                return {"error": f"Missing field: {field}"}

        logger.info("Game data validation passed.")
        return None

    except Exception as e:
        logger.error("Error occurred during game data validation: %s", str(e), exc_info=True)
        return {"error": "An unexpected error occurred during validation."}

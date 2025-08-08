from flask import Blueprint, request, jsonify
from game.models import get_games_ref
from .controllers import get_all_games, add_game
from logging_utils import setup_logger

# Initialize the logger for this module
logger = setup_logger("game_routes")

game_blueprint = Blueprint('game', __name__)

def validate_pagination(page, limit):
    """
    Validate pagination parameters.
    Args:
        page (int): Page number for pagination.
        limit (int): Number of items per page.
    Raises:
        ValueError: If page or limit is invalid.
    """
    if page < 1:
        raise ValueError("Page must be a positive integer.")
    if limit < 1:
        raise ValueError("Limit must be a positive integer.")

def validate_required_fields(data, required_fields):
    """
    Validate required fields in the input data.
    Args:
        data (dict): Input data from request.
        required_fields (list): List of required field names.
    Returns:
        list: Missing fields.
    """
    return [field for field in required_fields if field not in data]

@game_blueprint.route('/games', methods=['GET'])
def list_games():
    """
    Retrieve and list games with filtering and pagination.
    """
    try:
        # Log the request
        logger.info("GET /games endpoint called with query parameters: %s", request.args)

        # Extract query parameters
        category = request.args.get('category')
        min_popularity = float(request.args.get('min_popularity', 0))
        max_popularity = float(request.args.get('max_popularity', 100))
        min_rating = float(request.args.get('min_rating', 0))
        max_rating = float(request.args.get('max_rating', 5))
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Validate pagination parameters
        validate_pagination(page, limit)

        # Fetch and filter games
        games = get_all_games(
            category=category,
            page=page,
            limit=limit,
            min_popularity=min_popularity,
            max_popularity=max_popularity,
            min_rating=min_rating,
            max_rating=max_rating
        )

        # Check if the games variable is valid
        if not isinstance(games, list):
            raise ValueError("Invalid data format returned from get_all_games.")

        logger.info("Games fetched successfully. Total: %d", len(games))

        return jsonify({
            "success": True,
            "total": len(games),
            "page": page,
            "limit": limit,
            "games": games
        }), 200

    except ValueError as ve:
        # Handle validation errors
        logger.warning("Validation error in list_games: %s", str(ve))
        return jsonify({"success": False, "error": str(ve)}), 400

    except Exception as e:
        # Handle unexpected errors
        logger.error("Unexpected error in list_games: %s", str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    

@game_blueprint.route('/games', methods=['POST'])
def create_game():
    """
    Add a new game with metadata to the database.
    """
    try:
        # Log the request
        logger.info("POST /games endpoint called with data: %s", request.get_json())

        # Parse request data
        data = request.get_json()
        if not data:
            logger.warning("Invalid input: JSON payload required.")
            return jsonify({
                "success": False,
                "error": "Invalid input. JSON payload required."
            }), 400

        # Validate required fields
        required_fields = ['title', 'category', 'description', 'release_year', 'popularity', 'average_rating']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            logger.warning("Missing required fields: %s", ', '.join(missing_fields))
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Add game to the database
        result = add_game(data)

        logger.info("Game created successfully: %s", result)

        return jsonify({
            "success": True,
            "data": result,
            "message": "Game created successfully."
        }), 201

    except ValueError as ve:
        # Handle validation errors
        logger.warning("Validation error in create_game: %s", str(ve))
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400

    except Exception as e:
        # Handle unexpected errors
        logger.error("Unexpected error in create_game: %s", str(e), exc_info=True)
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Please try again later.",
            "details": str(e)
        }), 500

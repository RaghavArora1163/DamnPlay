import firebase_admin
from firebase_admin import credentials, db
from user.models import get_firebase_app

# Check if the app is already initialized
# if not firebase_admin._apps:
#     cred = credentials.Certificate('C:/Users/RJ36/OneDrive/Desktop/RBAC Updated/user/firebase_credentials.json')
#     firebase_admin.initialize_app(cred, {
#         'databaseURL': 'https://project-b15f4-default-rtdb.asia-southeast1.firebasedatabase.app/'
#     })
get_firebase_app()

def get_games_ref():
    """
    Get a reference to the 'games' node in the database.

    Returns:
        Reference: Firebase reference to the 'games' node.
    """
    return db.reference('games')

def add_game(game_data):
    """
    Add a new game to the database.

    Args:
        game_data (dict): The game metadata to be added.

    Returns:
        str: The unique ID of the new game.
    """
    # Ensure required fields are present
    required_fields = ["title", "category", "description", "thumbnail", "release_year", "popularity"]
    missing_fields = [field for field in required_fields if field not in game_data]

    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")

    # Set default for optional metadata
    game_metadata = {
        "title": game_data["title"],
        "category": game_data["category"],
        "description": game_data["description"],
        "thumbnail": game_data["thumbnail"],
        "release_year": game_data["release_year"],
        "popularity": game_data["popularity"],
        "average_rating": game_data.get("average_rating", 0),  # Default to 0 if not provided
    }

    games_ref = get_games_ref()
    new_game_ref = games_ref.push()  # Create a new game entry
    new_game_ref.set(game_metadata)  # Save game metadata
    return new_game_ref.key  # Return the unique ID of the new game

def get_all_games(category=None, min_popularity=0, max_popularity=100, min_rating=0, max_rating=5, page=1, limit=10):
    """
    Retrieve all games from the database with optional filters and pagination.

    Args:
        category (str, optional): Filter by game category. Defaults to None.
        min_popularity (float, optional): Minimum popularity filter. Defaults to 0.
        max_popularity (float, optional): Maximum popularity filter. Defaults to 100.
        min_rating (float, optional): Minimum rating filter. Defaults to 0.
        max_rating (float, optional): Maximum rating filter. Defaults to 5.
        page (int, optional): Page number for pagination. Defaults to 1.
        limit (int, optional): Number of items per page. Defaults to 10.

    Returns:
        dict: A dictionary containing filtered and paginated games.
    """
    games_ref = get_games_ref()
    games = games_ref.get() or {}

    # Filter games based on provided criteria
    filtered_games = {
        game_id: game_data
        for game_id, game_data in games.items()
        if (not category or game_data.get('category') == category)
        and (min_popularity <= game_data.get('popularity', 0) <= max_popularity)
        and (min_rating <= game_data.get('average_rating', 0) <= max_rating)
    }

    # Convert to list and apply pagination
    filtered_games_list = [
        {**{"id": game_id}, **game_data}
        for game_id, game_data in filtered_games.items()
    ]
    start = (page - 1) * limit
    end = start + limit

    return filtered_games_list[start:end]

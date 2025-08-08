from .models import get_games_ref, add_game as add_game_to_db

def get_all_games(category=None, min_popularity=0, max_popularity=100, min_rating=0, max_rating=5, page=1, limit=10):
    """
    Retrieve all games with optional filters and pagination.

    Args:
        category (str, optional): Filter by game category.
        min_popularity (float, optional): Minimum popularity filter. Defaults to 0.
        max_popularity (float, optional): Maximum popularity filter. Defaults to 100.
        min_rating (float, optional): Minimum rating filter. Defaults to 0.
        max_rating (float, optional): Maximum rating filter. Defaults to 5.
        page (int, optional): Page number for pagination. Defaults to 1.
        limit (int, optional): Number of items per page. Defaults to 10.

    Returns:
        list: A list of filtered and paginated games.
    """
    games_ref = get_games_ref()

    # Apply database query with filtering and indexing
    query = games_ref.order_by_child('popularity')  # Use index on "popularity"

    # Filter by category
    if category:
        query = games_ref.order_by_child("category").equal_to(category)

    # Fetch games within the popularity range
    games = query.get() or {}

    # Apply additional filtering and pagination
    filtered_games = [
        {**{"id": game_id}, **game_data}
        for game_id, game_data in games.items()
        if (min_popularity <= game_data.get('popularity', 0) <= max_popularity)
        and (min_rating <= game_data.get('average_rating', 0) <= max_rating)
    ]

    # Paginate results
    start = max(0, (page - 1) * limit)
    end = start + limit
    return filtered_games[start:end]

def add_game(game_data):
    """
    Add a new game to the database.

    Args:
        game_data (dict): The game metadata to be added.

    Returns:
        dict: A dictionary containing the new game ID and a success message.
    """
    # Ensure required fields are present
    required_fields = ["title", "category", "description", "thumbnail", "release_year", "popularity"]
    missing_fields = [field for field in required_fields if field not in game_data]

    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")

    # Construct game metadata
    game_metadata = {
        "title": game_data["title"],
        "category": game_data["category"],
        "description": game_data["description"],
        "thumbnail": game_data["thumbnail"],
        "release_year": game_data["release_year"],
        "popularity": game_data["popularity"],
        "average_rating": game_data.get("average_rating", 0),  # Default to 0 if not provided
    }

    # Add game to the database
    return add_game_to_db(game_metadata)

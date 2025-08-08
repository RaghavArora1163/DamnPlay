from firebase_admin import db

# Firebase references
def get_contests_ref():
    """
    Returns the Firebase reference for contests.
    """
    return db.reference('contests')

def get_user_contest_mapping_ref():
    """
    Returns the Firebase reference for user-contest mapping.
    """
    return db.reference('user_contest_mapping')

def get_users_wallet_ref():
    """
    Returns the Firebase reference for users' wallets.
    """
    return db.reference('users_wallet')

def get_valid_games():
    """
    Fetch valid games from the Firebase database, including their IDs.
    """
    try:
        # Reference to the 'games' node in the database
        games_ref = db.reference('games')

        # Fetch all games data
        games_data = games_ref.get()

        # Log the fetched data for debugging
        print(f"Fetched games data: {games_data}")

        # Return an empty list if no games are found
        if not games_data:
            print("No games found in the database.")
            return []

        # Extract game IDs and relevant details
        valid_games = [
            {
                "game_id": game_id,  # Firebase key as game ID
                "title": game.get("title"),
                "category": game.get("category"),
                "average_rating": game.get("average_rating"),
                "popularity": game.get("popularity"),
                "release_year": game.get("release_year"),
                "thumbnail": game.get("thumbnail"),
                "description": game.get("description"),
            }
            for game_id, game in games_data.items() 
            if isinstance(game, dict) and "title" in game
        ]

        print(f"Valid games fetched: {valid_games}")
        return valid_games
    except Exception as e:
        # Log the error for better debugging
        print(f"Error fetching games from Firebase: {str(e)}")
        return []  # Return an empty list in case of error

def log_contest_creation(contest_id, data):
    """
    Log contest creation details for debugging.
    """
    print(f"Contest created: ID = {contest_id}, Data = {data}")

def log_overlap_check(game_id, start_time, end_time, result):
    """
    Log the results of an overlap check.
    """
    if result:
        print(f"Overlap detected for game ID '{game_id}' between {start_time} and {end_time}. Result: {result}")
    else:
        print(f"No overlap detected for game ID '{game_id}' between {start_time} and {end_time}.")

# Add entry_fee field to the contest data structure
def create_contest(data):
    """
    Creates a new contest in the Firebase database with an additional 'entry_fee' field.
    """
    contests_ref = get_contests_ref()

    # Ensure the entry_fee is part of the contest data
    contest_data = {
        "game_id": data.get("game_id"),
        "title": data.get("title"),
        "description": data.get("description"),
        "start_time": data.get("start_time"),
        "end_time": data.get("end_time"),
        "entry_fee": data.get("entry_fee"),  # New entry_fee field
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "prize": data.get("prize"),
    }

    # Push the contest data to Firebase
    new_contest_ref = contests_ref.push(contest_data)
    log_contest_creation(new_contest_ref.key, contest_data)
    return new_contest_ref.key

def deduct_entry_fee(user_id, contest_id, entry_fee):
    """
    Deduct the entry fee from the user's wallet and record the contest participation.
    """
    try:
        wallet_ref = get_users_wallet_ref()
        user_wallet = wallet_ref.child(user_id).get()

        if not user_wallet or 'balance' not in user_wallet:
            return {"success": False, "message": "User wallet not found or invalid."}

        current_balance = user_wallet['balance']

        if current_balance < entry_fee:
            return {"success": False, "message": "Insufficient balance."}

        # Deduct the entry fee
        new_balance = current_balance - entry_fee
        wallet_ref.child(user_id).update({"balance": new_balance})

        # Log the user-contest mapping
        user_contest_ref = get_user_contest_mapping_ref()
        user_contest_ref.child(user_id).child(contest_id).set({"entry_fee": entry_fee})

        return {"success": True, "message": "Entry fee deducted successfully."}

    except Exception as e:
        print(f"Error deducting entry fee: {str(e)}")
        return {"success": False, "message": "An error occurred while deducting entry fee."}

def log_contest_completion(contest_id, data):
    """Log a contest as completed, including its leaderboard data."""
    db.reference(f"completed_contests/{contest_id}").set(data)

import bcrypt
import jwt
import datetime
from flask import jsonify, request
from firebase_admin import db
import re
from datetime import datetime, timedelta
from user.models import get_firebase_app
from utils import standardize_response
from logging_utils import setup_logger

# Setup logger
logger = setup_logger("user_services")

# Simulated in-memory store for tracking attempts (use Redis/DB in production)
login_attempts = {}

get_firebase_app()

# Existing Functions
def register_user(data):
    logger.info("Attempting to register a new user.")
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')  # Default role is 'user'

    # Check for missing fields
    if not username or not email or not password:
        logger.warning("Registration failed: Missing required fields.")
        return standardize_response(False, message="All fields (username, email, password) are required"), 400

    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        logger.warning("Registration failed: Invalid email format.")
        return standardize_response(False, message="Invalid email format"), 400

    # Enforce password strength
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*]', password):
        logger.warning("Registration failed: Password does not meet complexity requirements.")
        return standardize_response(False, message="Password must meet complexity requirements"), 400

    # Check for duplicate username or email
    users = db.reference('users').get() or {}
    for user in users.values():
        if user.get('username') == username:
            logger.warning("Registration failed: Username already exists.")
            return standardize_response(False, message="Username already exists"), 400
        if user.get('email') == email:
            logger.warning("Registration failed: Email already exists.")
            return standardize_response(False, message="Email already exists"), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Prepare user data
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow().isoformat()
    }

    # Save user data to the database
    user_ref = db.reference('users').push(user_data)

    logger.info(f"User registered successfully with ID: {user_ref.key}")
    # Return successful registration response
    return standardize_response(
        True,
        data={"user_id": user_ref.key},
        message="Registration successful"
    ), 201

def login_user(data):
    logger.info("Attempting to log in user.")
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logger.warning("Login failed: Missing email or password.")
        return standardize_response(False, message="Email and password are required"), 400

    now = datetime.utcnow()

    # Initialize or update login attempts
    if email not in login_attempts:
        login_attempts[email] = {"count": 0, "last_attempt": None}

    attempts = login_attempts[email]
    if attempts["last_attempt"] and now - attempts["last_attempt"] < timedelta(minutes=1):
        if attempts["count"] >= 5:  # Allow max 5 attempts per minute
            logger.warning("Login failed: Too many login attempts.")
            return standardize_response(False, message="Too many login attempts. Please try again later."), 429

    # Reset attempts if the last attempt was over a minute ago
    if attempts["last_attempt"] is None or now - attempts["last_attempt"] >= timedelta(minutes=1):
        login_attempts[email]["count"] = 0

    login_attempts[email]["count"] += 1
    login_attempts[email]["last_attempt"] = now

    # Query the database for the user
    users = db.reference('users').order_by_child('email').equal_to(email).get()
    user = next(iter(users.values()), None)

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        logger.warning("Login failed: Invalid credentials.")
        return standardize_response(False, message="Invalid credentials"), 400

    # Reset login attempts on successful login
    login_attempts[email]["count"] = 0

    # Generate tokens
    user_id = next(iter(users.keys()))
    access_token = generate_access_token(user_id)
    refresh_token = generate_refresh_token(user_id)

    logger.info("Login successful.")
    return standardize_response(True, data={"access_token": access_token, "refresh_token": refresh_token}, message="Login successful"), 200

def list_all_users():
    logger.info("Fetching all users.")
    try:
        users = db.reference('users').get()
        if not users:
            logger.info("No users found in the database.")
            return standardize_response(True, data=[], message="No users found"), 200

        user_list = [{"id": uid, "email": info.get('email')} for uid, info in users.items()]
        logger.info("Users fetched successfully.")
        return standardize_response(True, data=user_list, message="Users fetched successfully"), 200

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return standardize_response(False, message=f"Error fetching users: {str(e)}"), 500

def logout_user(token):
    logger.info("Attempting to log out user.")
    try:
        # Example placeholder logic for token invalidation
        # Implement actual token blacklisting logic here
        if not token:
            logger.warning("Logout failed: Token is required.")
            return standardize_response(False, message="Token is required"), 400

        logger.info("User logged out successfully.")
        return standardize_response(True, message="User logged out successfully"), 200

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return standardize_response(False, message=f"Error during logout: {str(e)}"), 500

def generate_access_token(user_id):
    logger.info("Generating access token.")
    secret_key = "Raghav"  # Replace with a secure key from your environment variables
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def generate_refresh_token(user_id):
    logger.info("Generating refresh token.")
    secret_key = "Raghav"  # Replace with a secure key
    expiration_time = datetime.utcnow() + timedelta(days=7)
    payload = {"user_id": user_id, "exp": expiration_time}
    return jwt.encode(payload, secret_key, algorithm="HS256")

def validate_token(token):
    logger.info("Validating token.")
    try:
        decoded = jwt.decode(token, "Raghav", algorithms=["HS256"])
        if datetime.utcnow() > datetime.utcfromtimestamp(decoded["exp"]):
            raise Exception("Token has expired")
        return decoded
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed: Token has expired.")
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        logger.warning("Token validation failed: Invalid token.")
        raise Exception("Invalid token")

def check_user_role(user_roles, required_role):
    logger.info("Checking user role.")
    if required_role not in user_roles:
        logger.warning("Role mismatch detected.")
        raise PermissionError("Role mismatch")
    return True

def validate_refresh_token(refresh_token):
    logger.info("Validating refresh token.")
    try:
        decoded_token = jwt.decode(refresh_token, "Raghav", algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token validation failed: Token has expired.")
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        logger.warning("Refresh token validation failed: Invalid refresh token.")
        raise Exception("Invalid refresh token")

def refresh_access_token(refresh_token):
    logger.info("Refreshing access token.")
    try:
        # Validate the refresh token
        decoded_token = validate_refresh_token(refresh_token)
        user_id = decoded_token.get("user_id")
        if not user_id:
            logger.warning("Refresh token validation failed: User ID not found.")
            raise ValueError("User ID not found in the refresh token.")

        # Generate a new access token
        new_access_token = generate_access_token(user_id)
        logger.info("Access token refreshed successfully.")
        return jsonify({
            "access_token": new_access_token
        }), 200

    except ValueError as e:
        logger.error(f"Error refreshing access token: {str(e)}")
        return jsonify({"error": str(e)}), 400

def refresh_token_endpoint():
    logger.info("Access token refresh endpoint hit.")
    data = request.get_json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        logger.warning("Access token refresh failed: Refresh token is required.")
        return jsonify({"error": "Refresh token is required"}), 400

    return refresh_access_token(refresh_token)

def update_user_profile(current_user, data):
    logger.info("Updating user profile.")
    email = data.get('email')
    password = data.get('password')
    updates = {}

    if email:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            logger.warning("Profile update failed: Invalid email format.")
            return standardize_response(False, message="Invalid email format"), 400
        updates['email'] = email

    if password:
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*]', password):
            logger.warning("Profile update failed: Password does not meet complexity requirements.")
            return standardize_response(False, message="Password must meet complexity requirements"), 400
        updates['password'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Apply updates
    user_ref = db.reference(f'users/{current_user["id"]}')
    user_ref.update(updates)

    logger.info("User profile updated successfully.")
    return standardize_response(True, message="User profile updated successfully"), 200

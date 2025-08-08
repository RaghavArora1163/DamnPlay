
from flask import request, jsonify
import jwt
from functools import wraps
from logging_utils import setup_logger

# Initialize the logger for this module
logger = setup_logger(__name__)

JWT_SECRET = "Raghav"
JWT_ALGORITHM = "HS256"

def fix_jwt_padding(token):
    """Fixes base64 padding issue for JWT tokens."""
    missing_padding = len(token) % 4
    if missing_padding:
        token += '=' * (4 - missing_padding)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            logger.warning("Token is missing in the request headers.")  # Log the missing token
            return jsonify({"message": "Token is missing!"}), 401
        
        # Clean the token, remove 'Bearer ' if present
        if token.startswith("Bearer "):
            token = token[7:]

        # Fix the padding issue (if any)
        token = fix_jwt_padding(token)
        
        try:
            logger.debug(f"Extracted Token: {token}")  # Log the extracted token
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            request.user = data
        except Exception as e:
            logger.error(f"Token is invalid. Error: {str(e)}")  # Log the invalid token error
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated


# def check_admin():
#     """
#     Middleware to check if the user is an admin.
#     In a real-world scenario, replace this with proper authentication.
#     """
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # Mocked authentication: Validate an "Authorization" header
#             token = request.headers.get('Authorization')
#             print(token)
#             if not token or token != "Bearer admin-token":  # Replace with real token validation
#                 return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator

# def role_required(required_role):
    # def decorator(f):
    #     @wraps(f)
    #     def decorated(*args, **kwargs):
    #         if not hasattr(request, 'user') or 'role' not in request.user:
    #             return jsonify({"message": "Role information is missing!"}), 403
    #         if request.user['role'] != required_role:
    #             return jsonify({"message": "Access denied!"}), 403
    #         return f(*args, **kwargs)
    #     return decorated
    # return decorator

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask

# Initialize Flask app (if not already done here)
app = Flask(__name__)

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]  # Allow 5 login attempts per minute
)

# Optionally, customize error message for rate limit exceed
@app.errorhandler(429)
def ratelimit_exceeded(e):
    logger.warning("Rate limit exceeded for a client.")  # Log the rate limit event
    return {"error": "Too many login attempts. Please try again later."}, 429
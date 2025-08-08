from flask import jsonify, request
from user.services import register_user, login_user, list_all_users, update_user_profile,logout_user # Import the new service function
from user.models import token_required , admin_required
from utils import standardize_response

# Controller for user registration
def register_controller():
    try:
        data = request.json
        return register_user(data)
    except Exception as e:
        return standardize_response(False, message=str(e)), 500

def login_controller():
    try:
        data = request.json
        return login_user(data)
    except Exception as e:
        return standardize_response(False, message=str(e)), 500


from user.services import logout_user

def logout_controller():
    token = request.headers.get('Authorization')  # Extract token from headers
    if token:
        return logout_user(token)
    return jsonify({'error': 'Token missing'}), 400

@token_required
def update_user_profile_controller(current_user):
    try:
        data = request.json
        return update_user_profile(current_user, data)
    except Exception as e:
        return standardize_response(False, message=str(e)), 500

@token_required
@admin_required
def list_users_controller(current_user,f):
    """
    Controller for listing all users (admin-only access).
    """
    try:
        return list_all_users()
    except Exception as e:
        return standardize_response(False, message=f"Error listing users: {str(e)}"), 500

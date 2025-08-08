from middleware import token_required, limiter
from flask import Blueprint
from user.controllers import (
    register_controller,
    login_controller,
    logout_controller,
    list_users_controller,
    update_user_profile_controller,
)
from user.models import admin_required
from logging_utils import setup_logger  # Import centralized logging utility

# Initialize logger for this module
logger = setup_logger(__name__)

# Define the Blueprint
user_blueprint = Blueprint('user', __name__)

# Routes
# Public routes
user_blueprint.route('/register', methods=['POST'])(register_controller)
user_blueprint.route('/login', methods=['POST'])(limiter.limit("5 per minute")(login_controller))

# Protected routes
user_blueprint.route('/logout', methods=['POST'])(token_required(logout_controller))
user_blueprint.route('/profile/update', methods=['PUT'])(token_required(update_user_profile_controller))

from user.models import token_required

# Admin-only routes
user_blueprint.route('/admin/users', methods=['GET'])(token_required(admin_required(list_users_controller)))

# Log initialization of user routes
logger.info("User Blueprint routes initialized successfully.")

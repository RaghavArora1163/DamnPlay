from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from contest.routes import contest_bp
from game.routes import game_blueprint
from leaderboard.routes import leaderboard_blueprint
from user.routes import user_blueprint
from wallet.routes import wallet_bp
import os
from logging_utils import setup_logger

# Initialize the logger
logger = setup_logger(__name__)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS

# Application configuration
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Raghav'

# Register blueprints under a single entry point "damnplay"
app.register_blueprint(contest_bp, url_prefix='/damnplay/contest')
app.register_blueprint(game_blueprint, url_prefix='/damnplay/game')
app.register_blueprint(leaderboard_blueprint, url_prefix='/damnplay/leaderboard')
app.register_blueprint(user_blueprint, url_prefix='/damnplay/user')
app.register_blueprint(wallet_bp, url_prefix='/damnplay/wallet')

# Log application initialization
logger.info("Flask application initialized")

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    response = {
        "error": str(e),
        "message": "An unexpected error occurred. Please try again later."
    }
    return jsonify(response), 500

# Health check endpoint
@app.route('/damnplay/health', methods=['GET'])
def health_check():
    logger.info("Health check endpoint accessed")
    return jsonify({"status": "API Gateway is running"}), 200

# Swagger UI configuration
SWAGGER_URL = '/damnplay/api-docs'  # Swagger UI URL
SWAGGER_YAML_FILE = os.path.join(os.path.dirname(__file__), 'swagger.yaml')  # Path to Swagger YAML file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    '/damnplay/swagger.yaml',  # URL to serve the Swagger YAML file
    config={'app_name': "Damnplay API Documentation"}  # Swagger UI Config
)

# Serve Swagger UI
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve Swagger YAML file
@app.route('/damnplay/swagger.yaml', methods=['GET'])
def swagger_yaml():
    try:
        logger.info("Serving Swagger YAML file")
        return send_from_directory(
            os.path.dirname(SWAGGER_YAML_FILE),
            os.path.basename(SWAGGER_YAML_FILE)
        )
    except Exception as e:
        logger.error(f"Error serving Swagger YAML file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000)

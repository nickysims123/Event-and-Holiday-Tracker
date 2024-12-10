#Imports from meal_max 
from flask import Flask, jsonify, make_response, Response, request
from dotenv import load_dotenv 

#my imports 
import bcrypt #for hashing 
from models import users_model 
from utils.sql_utils import check_database_connection, check_table_exists

load_dotenv()

app = Flask(__name__)

####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection, users table, and events table  are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if users table exists...")
        check_table_exists("users")
        app.logger.info("users table exists.")
        app.logger.info("Checking if events table exists...")
        check_table_exists("events")
        app.logger.info("events table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

####################################################
#
# User Routes  
#
####################################################
@app.route('/api/create-account', methods=['POST'])
def create_account() -> Response:
    """
    Route to create user's account 

    Expected JSON Input:
        - username (str) : the user's username 
        - password (str) : the user's password 

    Returns:
        JSON response indicating success of creating account 

    Raises:
        400 error if either the username or password is missing 
        500 error if a user is unable to be added
    """

    app.logger.info('Creating new account')
    try:
        # Get the JSON data 
        data = request.get_json()

        # Get data 
        username = data.get('username')
        password = data.get('password')

        # Check for correct values 
        if not username or not password:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Call create_account
        app.logger.info('Adding user: %s, %s, %.2f, %s', username, password)
        users_model.create_account(username, password)
        
        app.logger.info("User added: %s", username)
        return make_response(jsonify({'status': 'success', 'user': username}), 201)
    
    except Exception as e:
        app.logger.error("Failed to add user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/login', methods=['POST'])
def login() -> Response:
    """
    Route to login a user

    Expected JSON Input:
        - username (str) : the user's username 
        - password (str) : the user's password 

    Returns:
        JSON response indicating success of logging in  

    Raises:
        400 error if either the username or password is missing 
        401 error if the login was unsuccessful
    """
    app.logger.info('Logging into account')
    try:
        # Get JSON data
        data = request.get_json()

        # Get data 
        username = data.get('username')
        password = data.get('password')

        # Check for correct values 
        if not username or not password:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)
        
        # Call login
        is_valid = users_model.login(username, password)

        # Check if the login is successful 
        if is_valid:
            return make_response(jsonify({'status': 'success', 'message': "Login successful"}), 200)
        else:
            return make_response(jsonify({"status": "error", "message": "Invalid username or password"}), 401)
        
    except Exception as e:
        app.logger.error("Failed to add login user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/update-password', methods=['POST'])
def update_password() -> Response:
    """
    Route to update user's password 

    Expected JSON Input:
        - username (str) : the user's username 
        - new_password (str) : the user's new password 

    Returns:
        JSON response indicating success of updating their password 

    Raises:
        400 error if either the username or password is missing 
        500 error if a user's password is unable to be updated
    """
    app.logger.info('updating password')
    
    try:
        # Get JSON data 
        data = request.get_json()

        # Get data
        username = data.get('username')
        new_password = data.get('new_password')

        # Check for correct values
        if not data or 'username' not in data or 'new_password' not in data:
            return jsonify({"error": "Username and new password are required"}), 400
        
        # Call update_password 
        users_model.update_password(username, new_password)
        return jsonify({'status': 'success', "message": f"Password for user '{username}' updated successfully."}), 200
    
    except Exception as e:
        app.logger.error("Error updating password: %s", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

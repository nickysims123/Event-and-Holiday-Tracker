from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from event_tracker.models import calendar_model
from event_tracker.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)


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
    Route to check if the database connection and events table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if events table exists...")
        check_table_exists("events")
        app.logger.info("events table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

##########################################################
#
# Events
#
##########################################################

@app.route('/api/create-event', methods=['POST'])
def add_event() -> Response:
    """
    Route to add a new event to the database.

    Expected JSON Input:
        - event_day (int): The day of the event.
        - event_month (int): The month of the event.
        - event_year (int): The year of the event.
        - event_name (str): The name of the event.
        - is_religious (bool): Whether the event is religious.

    Returns:
        JSON response indicating the success of the event addition.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the event to the database.
    """

    app.logger.info('Creating new event')
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract and validate required fields
        event_name = data.get('event_name')
        event_day = data.get('event_day')
        event_month = data.get('event_month')
        event_year = data.get('event_year')
        is_religious = data.get('is_religious')

        if event_day is None or event_month is None or event_year is None or not event_name or is_religious is None:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Check that the dates are valid
        try:
            day = int(event_day)
            if not isinstance(day, int) or day <= 0:
                raise ValueError("Event_day must have a positive value.")
        except ValueError as e:
            return make_response(jsonify({'error': 'Day must be a valid int less than 31.'}), 400)
        
        try:
            month = int(event_month)
            if not isinstance(month, int) or month <= 0:
                raise ValueError("Event_day must have a positive value.")
        except ValueError as e:
            return make_response(jsonify({'error': 'Day must be a valid int less than 31.'}), 400)

        # Call the celndar_model function to add the combatant to the database
        app.logger.info('Adding event: %s, %d, %d, %d, %s', event_name, event_day, event_month, event_year, str(is_religious))
        calendar_model.add_meal(event_name, event_day, event_month, event_year, is_religious)

        app.logger.info("Event added: %s", event_name)
        return make_response(jsonify({'status': 'success', 'event': event_name}), 201)
    except Exception as e:
        app.logger.error("Failed to add event: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/delete-event', methods=['DELETE'])
def delete_event(id: int) -> Response:
    """
    Route to delete an event by its ID. This performs a soft delete by marking it as deleted.

    Path Parameter:
        - id (int): The ID of the event to delete.

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info(f"Deleting event by ID: {id}")

        calendar_model.delete_event(id)
        return make_response(jsonify({'status': 'event deleted'}), 200)
    except Exception as e:
        app.logger.error(f"Error deleting meal: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    

@app.route('/api/get-meal-by-id/<int:meal_id>', methods=['GET'])
def get_event_by_id(id: int) -> Response:
    """
    Route to get an event by its ID.

    Path Parameter:
        - id (int): The ID of the event.

    Returns:
        JSON response with the meal details or error message.
    """
    try:
        app.logger.info(f"Retrieving event by ID: {id}")

        event = calendar_model.get_event_by_id(id)
        return make_response(jsonify({'status': 'success', 'event': event}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving event by ID: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
##########################################################
#
# Events Data
#
##########################################################
    
@app.route('/api/get-events', methods=['GET'])
def get_events() -> Response:
    """
    Route to get the a list of all events.

    Returns:
        JSON response with a sorted leaderboard of meals.
    Raises:
        500 error if there is an issue generating the leaderboard.
    """
    try:
        app.logger.info("Generating list of events")

        events_data = calendar_model.get_events()

        return make_response(jsonify({'status': 'success', 'events': events_data}), 200)
    except Exception as e:
        app.logger.error(f"Error generating events data: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
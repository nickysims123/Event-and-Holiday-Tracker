Welcome to our event tracker! This program lets you create events
stored in a relational database. These events can be created, updated, requested,
and deleted.

You can set up this code environment by running :
    - chmod +x setup_venv.sh
    - chmod +x run_docker.sh

Now, you can run all tests by the commands:
    - python -m pytest .
    - ./smoketest.sh

It's functionality includes checking distances between event dates, 
checking if the current date is a holiday given an external API call, 
The database also allows for soft deletion of events.

ISSUE LOG:
    - Unit Testing is variable for the functions provided on the main branch. There seems to be an issue with using Mocker as a parameter for my mock_cursor fixture. It has worked some times out of many. The issue lies with the SQL code in the test_calendar_model.py.
    - There is one test fixture that outright does not work: test_update_event. This fixture breaks because of the mock call to the fake DB: it cannot successfully check the data of the event after running the mock call.

ROUTES:

Route: /create-event

    Request Type: POST
    Purpose: creates a new event
    Request Body: 
        - event_name (str): The name of the event.
        - event_day (int): The day of the event.
        - event_month (int): The month of the event.
        - event_year (int): The year of the event.
        - is_religious (bool): Whether the event is religious.
    Reponse Format: JSON
        Success Response Example: 
            - code 201
            - {
                'status': 'success', 'event': event_name
            }
    Example Request: 
        - {
            "event_name" : "Christmas"
            "event_day" : 1
            "event_month" : 1
            "event_year" : 1
            "is_religious" true
        }
    Example Response: 
        - {
            'status': 'success',
            'event': 'Christmas',
            201
        }


Route: /delete-event

    Request Type: DELETE
    Purpose: deletes an event
    Request Body:
        None
    Response Format: JSON
    Success Response Example:
        - Code: 200
        - Content: {"status" : "event deleted"}
    Example Request:
        None
    Example Response:
        - {
            "status" : "event deleted",
            200
        }

Route: /get-event-by-id

    Request Type: GET
    Purpose: Gets a specific event
    Request Body: 
        - event_id (int) : The ID of the event
    Response Format: JSON
    Success Response Example: 
        - Code: 200
        - Content: {'status' : 'success', 'event' : event}
    Example Request:
        - {
            "id" : 1
        }
    Example Response: 
        - {
            'status' : 'success',
            'event': 'Christmas',
            200,
        }

Route: /get-events

    Request Type: GET
    Purpose: Gets all events
    Request Body:
        - None
    Response Format: JSON
    Success Response Example: 
        - Code: 200
        - Content: {'status': 'success', 'events': 'events_data'}
    Example Request:
        - None
    Example Response: 
    - {
        'status' : 'success',
        'events' : ['Christmas', 'Halloween'],
        200
    }

Route: /update_event

    Request Type: PUT
    Purpose: Change the date of a given event
    Request Body: 
        - {
            id (int): The ID of the event to be altered
            day (int): The new day of the event.
            month (int): The new month of the event.
            year (int): The new year of the event. 
        }
    Response Format: JSON
    Success Response Example:
        - Code: 200
        - Content: {
            'status': 'success',
            'new_day': event_day,
            'new_month': event_month,
            'new_year': event_year
            }
    Example Request:
        - {
            'id': 1
            'day': 2
            'month': 8
            'year': 2010
        }
    Example Response:
        - {
            'status': success,
            'new_day': 3,
            'new_month': 10,
            'new_year': 2012,
            200
        }
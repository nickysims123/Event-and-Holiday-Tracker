from contextlib import contextmanager
import re
import sqlite3

import pytest

from event_tracker.models.calendar_model import (
    Event,
    add_event,
    delete_event,
    get_event_by_id,
    get_events,
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("event_tracker.models.calendar_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_song(mock_cursor):
    """Test creating a new event in the table."""

    # Call the function to create a new song
    add_event(event_name="Event Name", event_day=1, event_month=1, event_year=2022, is_religious=True)

    expected_query = normalize_whitespace("""
        INSERT INTO events (event_name, event_day, event_month, event_year, is_religious)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Event Name", 1, 1, 2022, True)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_song_duplicate(mock_cursor):
    """Test creating a song with a duplicate name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: event.event_name")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Event with name 'Event Name' already exists"):
        add_event(event_name="Event Name", event_day=1, event_month=1, event_year=2022, is_religious=True)

def test_delete_event(mock_cursor):
    """Test soft deleting an event from the catalog by event ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_event(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM events WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE events SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_event_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent event."""

    # Simulate that no song exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Event with ID 999 not found"):
        delete_event(999)

def test_delete_event_already_deleted(mock_cursor):
    """Test error when trying to delete an event that's already marked as deleted."""

    # Simulate that the event exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete an event that's already been deleted
    with pytest.raises(ValueError, match="Event with ID 999 has already been deleted"):
        delete_event(999)

######################################################
#
#    Get Event
#
######################################################

def test_get_event_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ("Event Name", 1, 1, 2022, True)

    # Call the function and check the result
    result = get_event_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Event(id=1, event_name="Event Name", event_day=1, event_month=1, event_year=2022, is_religious=True)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, event_name, event_day, event_month, event_year, is_religoius, deleted FROM songs WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_event_by_id_bad_id(mock_cursor):
    # Simulate that no song exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Event with ID 999 not found"):
        get_event_by_id(999)

def test_get_events(mock_cursor):
    # Simulate that the songs exist in the database
    mock_cursor.fetchall.return_value = [
        (1, "Event 1", 1, 1, 2022, True),
        (2, "Event 2", 2, 2, 2022, False),
    ]

    # Call the function and check the result
    result = get_events()

    # Expected result based on the simulated fetchall return value

    expected_result = [
        Event(id=1, event_name="Event 1", event_day=1, event_month=1, event_year=2022, is_religious=True),
        Event(id=2, event_name="Event 2", event_day=2, event_month=2, event_year=2022, is_religious=False),
    ]

    # Ensure the result matches the expected output

    assert result == expected_result, f"Expected {expected_result}, got {result}"


from contextlib import contextmanager
import re
import sqlite3
import datetime

import pytest

from event_tracker.models.event_model import (
    Event,
    create_event,
    delete_event,
    check_if_holiday,
    check_time_until,
)

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def calendar_model():
    # Setup for calendar_model (e.g., create an instance of the model)
    model = calendar_model()
    yield model
    # Teardown if needed (e.g., closing database connections or cleanup)
    model.cleanup()

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
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("event_tracker.models.calendar_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Check Time until Date
#
######################################################


def test_valid_date_future(self):
    """Test with a valid future date."""

    today = datetime.date.today()
    future_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    self.assertEqual(check_time_until(future_date), -10)

def test_valid_date_past(self):
    """Test with a valid past date."""

    today = datetime.date.today()
    past_date = (today - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    self.assertEqual(check_time_until(past_date), 10)

def test_today_date(self):
    """Test with today's date."""

    today = datetime.date.today().strftime('%Y-%m-%d')
    self.assertEqual(check_time_until(today), 0)

def test_invalid_date_format(self):
    """Test with an invalid date format."""

    with pytest.raises(ValueError, match="Invalid date: 12/25/2024. date must be a string in the format day/month/year."):
        check_time_until('12/25/2024')

def test_non_string_date(self):
    """Test with a non-string input."""

    with pytest.raises(ValueError, match="Incorrect data format, should be YYYY-MM-DD."):
        check_time_until(20240101)


######################################################
#
#    Check Holiday Status
#
######################################################


def test_holiday_true(self, mock_get_holiday_status):
    """Test when today is a holiday."""

    mock_get_holiday_status.return_value = True
    self.assertTrue(check_if_holiday())


def test_holiday_false(self, mock_get_holiday_status):
    """Test when today is not a holiday."""
    
    mock_get_holiday_status.return_value = False
    self.assertFalse(check_if_holiday())
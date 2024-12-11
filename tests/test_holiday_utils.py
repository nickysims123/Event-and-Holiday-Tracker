import pytest
import requests

from event_tracker.utils.holiday_utils import get_holiday_status

HOLIDAY_STATUS = True

@pytest.fixture
def mock_nager_at(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_holiday_status(mock_nager_at):
    """Test retrieving a random number from nager.at."""
    result = get_holiday_status()

    # Assert that the result is the mocked random number
    assert result == HOLIDAY_STATUS, f"Expected holiday status {HOLIDAY_STATUS}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with('https://date.nager.at/Api/v3/IsTodayPublicHoliday/US', timeout=5)

def test_get_holiday_status_request_failure(mocker):
    """Simulate  a request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to date.nager.at failed: Connection error"):
        get_holiday_status()

def test_get_holiday_status_timeout(mocker):
    """Simulate  a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to date.nager.at timed out."):
        get_holiday_status()

def test_get_holiday_status_invalid_response(mock_nager_at):
    """Simulate  an invalid response (non-bool)."""
    mock_nager_at.ok = 'invalid'

    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_holiday_status()


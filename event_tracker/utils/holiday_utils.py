import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)
configure_logger(logger)



def get_holiday_status() -> bool:

    url = "https://date.nager.at/Api/v3/IsTodayPublicHoliday/US"

    try:
        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        status_code = response.status_code
        if status_code == "200":
            return True
        elif status_code == "204":
            return False
        else:
            return f"Error: Received unexpected status code {status_code}."

    except requests.exceptions.Timeout:
        logger.error("Request to date.nager.at timed out.")
        raise RuntimeError("Request to date.nager.at timed out.")
    except requests.exceptions.RequestException as e:
        logger.error("Request to date.nager.at failed: %s", e)
        raise RuntimeError("Request to date.nager.at failed: %s" % e)


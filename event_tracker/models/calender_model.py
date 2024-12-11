from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any
import datetime
from event_tracker.utils.holiday_utils import get_holiday_status


def check_time_until(date: str) -> int:
    """
    Returns the time in days between today and a given date.

    Args:
        date (str): the date to calculate the number of days until.

    Raises: 
        ValueError: if the date is not a string
        ValueError: if the date is not formated correctly
    """
    if not isinstance(date, (str)):
        raise ValueError(f"Invalid date: {date}. date must be a string in the format day/month/year.")
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD.")
    
    today = datetime.date.today()
    
    date = format_date(date)

    difference = datetime.strptime(today, "%Y/%m/%d") - datetime.strptime(date, "%Y/%m/%d") 

    return int(difference.days)

def check_if_holiday() -> bool:
    """
    Returns True if today is a holiday, and False if not.
    
    """
    return get_holiday_status()




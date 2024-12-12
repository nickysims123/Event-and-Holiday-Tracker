from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from event_tracker.utils.sql_utils import get_db_connection
from event_tracker.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Event:
    id: int
    event_name: str
    event_day: int
    event_month: int
    event_year: int
    is_religious: bool 

    def __post_init__(self):
        if self.event_day < 0 or self.event_month < 0 or self.event_year < 0:
            raise ValueError("Date must be a positive value.")

def add_event(event_day, event_month, event_year, event_name, is_religious) -> None :
    """
    Adds a new event to the database.

    Args:
        event_day (int): The day of the event.
        event_month (int): The month of the event.
        event_year (int): The year of the event.
        event_name (str): The name of the event.
        is_religious (bool): Whether the event is religious.

    Raises:
        ValueError: If the event name already exists or if the date is invalid.
        sqlite3.Error: If there is an issue with the database.
    """
    if not isinstance(event_day, (int)) or event_day <= 0:
        raise ValueError(f"Invalid day: {event_day}. Day must be a positive number.")
    if not isinstance(event_month, (int)) or event_month <= 0:
        raise ValueError(f"Invalid month: {event_month}. Month must be a positive number.")
    if not isinstance(event_year, (int)) or event_year <= 0:
        raise ValueError(f"Invalid year: {event_year}. Year must be a positive number.")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_name, event_day, event_month, event_year, is_religious)
                VALUES (?, ?, ?, ?, ?)
            """, (event_name, event_day, event_month, event_year, is_religious))
            conn.commit()

            logger.info("Event successfully added to the database: %s", event)

    except sqlite3.IntegrityError:
        logger.error("Duplicate event name: %s", event)
        raise ValueError(f"Event with name '{event}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def delete_event(id: int) -> None:
    """
    Marks an event as deleted in the database.

    Args:
        id (int): The ID of the event to delete.
    
    Raises:
        ValueError: If the event is not found or has already been deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM events WHERE id = ?", (id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Event with ID %s has already been deleted", id)
                    raise ValueError(f"Event with ID {id} has been deleted")
            except TypeError:
                logger.info("Event with ID %s not found", id)
                raise ValueError(f"Event with ID {id} not found")

            cursor.execute("UPDATE events SET deleted = TRUE WHERE id = ?", (id,))
            conn.commit()

            logger.info("Event with ID %s marked as deleted.", id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def get_events() -> dict[str, Any]:
    """
    Retrieves all events from the database.

    Returns:
        dict[str, Any]: A dictionary containing the events.
    """
    query = """
        SELECT id, event_name, event_day, event_month, event_year, is_religious
        FROM events WHERE deleted = false
    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            event = {
                'id': row[0],
                'event_name': row[1],
                'event_day': row[2],
                'event_month': row[3],
                'event_year': row[4],
                'is_religious': row[5]
            }
            leaderboard.append(event)

        logger.info("Events retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def get_event_by_id(id: int) -> Event:
    """
    Retrieves an event from the database by its ID.

    Args:
        id (int): The ID of the event to retrieve.

    Returns:
        Event: The event object.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, event_name, event_day, event_month, event_year, is_religious, deleted FROM events WHERE id = ?", (id,))
            row = cursor.fetchone()

            if row:
                if row[6]:
                    logger.info("Event with ID %s has been deleted", id)
                    raise ValueError(f"Event with ID {id} has been deleted")
                return Event(id=row[0], event_name=row[1], event_day=row[2], event_month=row[3], event_year=row[4], is_religious=row[5])
            else:
                logger.info("Event with ID %s not found", id)
                raise ValueError(f"Event with ID {id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
###########################################################
#
# NOTE: This following function is not used in the application.
# It is not tested nor called upon in our application.
# Mock documentation can be found in the README.md file. The idea
# was scrapped as we already have 'PUT' commands in the application.
# For this implementation, this function would need all 4 paramters
# to execute.    
#
###########################################################
    
def update_event_date(id: int, day: int, month: int, year: int) -> None:
    """
    Updates the date of an event in the database.
    
    Args:
        id (int): The ID of the event to update.
        day (int): The day of the event.
        month (int): The month of the event.
        year (int): The year of the event.

    Raises:
        ValueError: If the event is not found or has been deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM events WHERE id = ?", (id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Event with ID %s has been deleted", id)
                    raise ValueError(f"Event with ID {id} has been deleted")
            except TypeError:
                logger.info("Event with ID %s not found", id)
                raise ValueError(f"Event with ID {id} not found")

            cursor.execute("UPDATE events SET event_day = ?, event_month = ?, event_year = ? WHERE id = ?", (day, month, year, id))

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    

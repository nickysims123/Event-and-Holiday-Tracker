from dataclasses import dataclass
import logging
import sqlite3
import bcrypt

from utils.sql_utils import get_db_connection
from utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class User:
    id: int 
    username: str 
    password_hash: str 
    salt: str

def create_account(username: str, password: str) -> None:
    """
    create_account: creates an account for a user with a specified username and password 

    Args:
        username: str, containing the username 
        password: str, containing the password 

    Returns:
        None

    Raises: 
        ValueError: If username or password is left blank 
        ValueError: If an account with the given username already exists 
        sqlite3.Error: If any database error occurs  

    """
  
    if isinstance(username, (int, float)) or isinstance(password, (int, float)) or not username or not password:
        raise ValueError("Username and/or password are invalid")
    try:
        salt = bcrypt.gensalt()  # generates a salt in bytes
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt)
                VALUES (?, ?, ?)
            """, (username, password_hash, salt))
            conn.commit()

            logger.info("User created successfully: %s", User)

    except sqlite3.IntegrityError:
        logger.error("Duplicate username: %s", username)
        raise ValueError(f"Username '{username}' already exists")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    

def login(username: str, password: str) -> bool:
    """
    login: checks a user's credientials by comparing their password to the password associated with the username in db. 

    Args:
        username: a string, of the user's username
        password: a string, of the user's password

    Returns:
        bool: true if the password matches, false otherwise 
    
    Raises:
        ValueError: if password or username is not given 
        sqlite3.Error: If any database error occurs  
    """
    if isinstance(username, (int, float)) or isinstance(password, (int, float)) or not username or not password:
        raise ValueError("Username and/or password are invalid")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash, salt FROM users WHERE username = ?
            """, (username,))
        
            result = cursor.fetchone()
            if result:
                return bcrypt.checkpw(password.encode('utf-8'), result[0]) 
            else:
                logger.info("User not found: %s", username)
                return False
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_password(username: str, new_password: str) -> None:
    """
    update_password: takes in a username and a new password. Changes the old password associated with the user with a new one. 

    Args:
        username: a string, of the user's username
        new_password: a string, of the user's new password

    Returns: 
        None

    Raises: 
        ValueError: If the username or new password are not given
        sqlite3.Error: If any database error occurs  
    """
    if isinstance(username, (int, float)) or isinstance(new_password, (int, float)) or not username or not new_password:
        raise ValueError("Username and/or password are invalid")
    try: 
        new_salt = bcrypt.gensalt()
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), new_salt) 

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET password_hash = ?, salt = ?
                WHERE username = ?
            """, (new_password_hash, new_salt, username))
            conn.commit()

            logger.info("Password successfully changed for user: %s", User)
            
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e




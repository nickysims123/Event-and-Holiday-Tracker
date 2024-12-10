from contextlib import contextmanager
import re
import sqlite3

import pytest
import bcrypt 

from models.users_model import create_account, login, update_password

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
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("models.users_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    create_account
#
######################################################

def test_create_account(mock_cursor):
    """ Test creating an account """

    # Create account 
    create_account(username="user123", password="5678")

    # Expected query 
    expected_query = normalize_whitespace("""
        INSERT INTO users (username, password_hash, salt)
        VALUES (?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Get what the actual args were 
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Check username 
    assert actual_arguments[0] == "user123", "Username argument mismatch."

    # Check salt and pw not empty 
    assert actual_arguments[1], "Password hash should not be empty."
    assert actual_arguments[2], "Salt should not be empty."

def test_create_account_incorrect_values(mock_cursor):
    """ 
        Test creating account with incorrect values: 
        1. Empty username 
        2. Empty password
        3. Wrong username type
        4. Wrong password type 
    """
    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        create_account(username="", password="1234")

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        create_account(username="user12344", password ="") 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        create_account(username="user12344", password =88888) 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        create_account(username=341, password ="99909") 

def test_create_duplicate_account(mock_cursor):
    """ Test creating an account with the same username """
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: username")

    with pytest.raises(ValueError, match="Username 'user11' already exists"):
        create_account(username="user11", password="123444")

######################################################
#
#    login
#
######################################################

def test_login(mock_cursor):
    """ Test logging into an existing account """
    username = "user123"
    password = "5678"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt) 

    # Mock an existing password + salt 
    mock_cursor.fetchone.return_value = (password_hash, salt)

    #Get the actual result:
    result = login(username="user123", password="5678")
    expected_result = True 

    assert result == expected_result, f"Expected {expected_result}, but got {result}"

def test_login_incorrect_values(mock_cursor):
    """ 
        Test logging in with incorrect values:
        1. Empty username 
        2. Empty password
        3. Wrong username type
        4. Wrong password type 
    """
    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        login(username="", password="1234")

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        login(username="user12344", password ="") 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        login(username="user12344", password =88888) 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        login(username=341, password ="99909") 

def test_login_account_doesnt_exist(mock_cursor):
    """ Test logging into an account that doesn't exist """
    
    username = "user123"
    password = "5678"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt) 

    #Mock the decoding of the password and salts from the db
    mock_cursor.fetchone.return_value = None

    #Get the actual result:
    result = login(username="user90", password="5678")
    expected_result = False

    assert result == expected_result, f"Expected {expected_result}, but got {result}"

def test_login_wrong_pw(mock_cursor):
    """ Test logging into an account with the wrong password """

    username = "user123"
    password = "5678"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt) 

    #Mock the decoding of the password and salts from the db
    mock_cursor.fetchone.return_value = (password_hash, salt)

    #Get the actual result:
    result = login(username="user90", password="000")
    expected_result = False

    assert result == expected_result, f"Expected {expected_result}, but got {result}"

######################################################
#
#    update_password
#
######################################################
def test_update_password(mock_cursor):
    """ Test updating password """

    username = "user123"
    old_password = "5678"
    new_password = "newpassword123"

    salt = bcrypt.gensalt()
    old_password_hash = bcrypt.hashpw(old_password.encode('utf-8'), salt)

    mock_cursor.fetchone.return_value = (old_password_hash.decode('utf-8'), salt.decode('utf-8'))

    update_password(username="user123", new_password="newpassword123")

    expected_query = normalize_whitespace("""
                UPDATE users
                SET password_hash = ?, salt = ?
                WHERE username = ?
            """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_update_incorrect_values(mock_cursor):
    """ 
        Test updating password with the incorrect values:
        1. Empty username 
        2. Empty password
        3. Wrong username type
        4. Wrong password type 
    """
    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        update_password(username="", new_password="1234")

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        update_password(username="user12344", new_password ="") 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        update_password(username="user12344", new_password=88888) 

    with pytest.raises(ValueError, match="Username and/or password are invalid"):
        update_password(username=341, new_password ="99909") 


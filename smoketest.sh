#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

###############################################
#
# User 
#
###############################################


test_check_time_until() {
  local test_date=$1
  local expected_output=$2

  echo "Testing check_time_until with date: $test_date..."
  response=$(python3 -c "
        import datetime
        from your_module import check_distance
        print(check_distance('$test_date'))
        ")
  if [ "$response" = "$expected_output" ]; then
    echo "check_time_until('$test_date') passed. Output: $response"
  else
    echo "check_time_until('$test_date') failed. Expected: $expected_output, Got: $response"
    exit 1
  fi
}

# Function to test check_if_holiday
test_check_if_holiday() {
  echo "Testing check_if_holiday..."
  response=$(python3 -c "
        from your_module import check_if_holiday
        print(check_if_holiday())
        ")
  if [[ "$response" == "True" || "$response" == "False" ]]; then
    echo "check_if_holiday() passed. Output: $response"
  else
    echo "check_if_holiday() failed. Unexpected output: $response"
    exit 1
  fi
}

###############################################
#
# Main Execution
#
###############################################

check_health
check_db

echo "getting todays date"
TODAY=$(date +%Y-%m-%d)
PAST_DATE=$(date -d "-30 days" +%Y-%m-%d)
FUTURE_DATE=$(date -d "+30 days" +%Y-%m-%d)

echo "checking distance with three different times"
test_check_distance "$TODAY" "0"
test_check_distance "$PAST_DATE" "30"
test_check_distance "$FUTURE_DATE" "-30"

echo "checking if today is a holiday"
test_check_if_holiday

echo "All smoke tests passed successfully."

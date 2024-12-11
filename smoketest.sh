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

create_event() {
  event_name = $1
  event_day = $2
  event_month = $3
  event_year = $4
  is_religious = $5

  echo "Adding event ($event_name) to the playlist..."
  curl -s -X POST "$BASE_URL/create-event" -H "Content-Type: application/json" \
    -d "{\"event_name\":\"$event_name\", \"event_day\":\"$event_day\", \"event_month\":$event_month, \"event_year\":\"$event_tear\", \"is_religious\":$is_religious}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Event added successfully."
  else
    echo "Failed to add event."
    exit 1
  fi
}

delete_event_by_id() {
  event_id=$1

  echo "Deleting event by ID ($event_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-event/$event_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Event deleted successfully by ID ($event_id)."
  else
    echo "Failed to delete event by ID ($event_id)."
    exit 1
  fi
}

get_event_by_id() {
  event_id=$1

  echo "Getting event by ID ($event_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-event-by-id/$event_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "event retrieved successfully by ID ($event_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "event JSON (ID $event_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get event by ID ($event_id)."
    exit 1
  fi
}

get_all_events() {
  echo "Getting all events in the table..."
  response=$(curl -s -X GET "$BASE_URL/get-events")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All events retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Events JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get events."
    exit 1
  fi
}

check_health
check_db

create_event "Christmas" 25 12 2021 true
create_event "New Year" 1 1 2022 false

get_all_events
delete_event_by_id 1

get_all_events

create_event "Easter" 4 4 2022 true
get_event_by_id 2
get_event_by_id 3
delete_event_by_id 3
get_event_by_id 2
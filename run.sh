#!/bin/bash

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

# Set JAVA_HOME for the Docker containers
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$JAVA_HOME/bin:$PATH

# Ensure the databases are running
echo "Starting Docker Compose services..."
docker-compose up -d

# Function to check if the database is ready
function wait_for_db() {
  echo "Waiting for PostgreSQL to be ready..."
  while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do   
    sleep 1
    echo "Waiting for PostgreSQL..."
  done
  echo "PostgreSQL is up and running."
}

# Wait for PostgreSQL to be ready
wait_for_db

# Function to check if Alembic migrations have been applied
function check_migrations() {
  echo "Checking for existing migrations..."
  MIGRATIONS_COUNT=$(poetry run alembic history | wc -l)
  if [ "$MIGRATIONS_COUNT" -eq 0 ]; then
    echo "No migrations found. Creating initial migration..."
    poetry run alembic revision --autogenerate -m "Initial migration"
    echo "Applying initial migration..."
    poetry run alembic upgrade head
  else
    echo "Running Alembic migrations..."
    poetry run alembic upgrade head
  fi
}

# Apply database migrations
check_migrations

# Start the FastAPI application
echo "Starting FastAPI application..."
poetry run uvicorn fastapi_db2.main:app --reload --host 0.0.0.0 --port 8000

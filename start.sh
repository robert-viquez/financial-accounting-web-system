#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "Starting backend..."
cd "$BACKEND_DIR"

# Start the backend server in the background
source .venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$FRONTEND_DIR"

# Start the frontend server in the background
npm run dev &
FRONTEND_PID=$!


# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

wait

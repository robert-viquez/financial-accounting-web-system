#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "======================================"
echo " Starting Financial Accounting System"
echo "======================================"

# -------------------------------------
# 1. Start MySQL
# -------------------------------------
echo ""
echo "[1/3] Starting MySQL..."

if brew services list | grep -qE '^mysql[[:space:]].*started'; then
    echo "MySQL is already running."
else
    brew services start mysql
    echo "MySQL started."
fi

# Wait until MySQL accepts connections
echo "Waiting for MySQL..."

until mysqladmin ping -u root --silent 2>/dev/null; do
    sleep 1
done

echo "MySQL is ready."

# -------------------------------------
# 2. Start Django backend
# -------------------------------------
echo ""
echo "[2/3] Starting Django backend..."

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    echo "ERROR: backend/.venv was not found."
    exit 1
fi

source .venv/bin/activate

python manage.py runserver &
BACKEND_PID=$!

echo "Backend running at http://127.0.0.1:8000"

# -------------------------------------
# 3. Start Vue frontend
# -------------------------------------
echo ""
echo "[3/3] Starting Vue frontend..."

cd "$FRONTEND_DIR"

npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo " System started"
echo "======================================"
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop."
echo ""

# -------------------------------------
# Shutdown handling
# -------------------------------------
cleanup() {
    echo ""
    echo "Stopping application..."

    # Stop Django
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        wait "$BACKEND_PID" 2>/dev/null
    fi

    # Stop Vue
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        wait "$FRONTEND_PID" 2>/dev/null
    fi

    # Stop MySQL 
    if [ "$MYSQL_STARTED_BY_SCRIPT" = true ]; then
        echo "Stopping MySQL..."
        brew services stop mysql
    else
        echo "MySQL was already running, leaving it active."
    fi

    echo ""
    echo "System stopped safely."
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
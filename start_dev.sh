#!/bin/bash

# Development startup script for Propaganda Spotter
echo "🚀 Starting Propaganda Spotter Development Environment..."

# Function to cleanup on exit
cleanup() {
    echo "
🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap cleanup function on script exit
trap cleanup EXIT INT TERM

# Start backend
echo "🔧 Starting backend server on http://localhost:8000"
(cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
echo "🎨 Starting frontend server..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo "
✅ Environment started!"

# Wait for user to stop
wait
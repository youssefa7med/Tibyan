#!/bin/bash

# PPE Safety Monitoring System - Local Start Script for Linux/Mac
# This script starts both backend and frontend for local on-premises use

set -e

echo "=========================================="
echo "PPE Safety Monitoring System"
echo "Local On-Premises Startup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

echo "[1/4] Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib/python3.*/site-packages/fastapi" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. You can edit it if needed."
fi

deactivate
cd ..

echo "[2/4] Setting up frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

cd ..

echo "[3/4] Starting backend server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

echo "[4/4] Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "Startup complete!"
echo "=========================================="
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait






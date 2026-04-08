#!/bin/bash

# PPE Safety Monitoring System - Deployment Script
# This script deploys the system for production

set -e

echo "=========================================="
echo "PPE Safety Monitoring System - Deployment"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "Error: backend/.env not found"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Start backend
echo ""
echo "Starting backend..."
cd backend
source venv/bin/activate

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Backend is already running on port 8000"
    echo "Please stop it first or change the port"
    exit 1
fi

echo ""
echo "Starting FastAPI server..."
echo "Backend will be available at http://localhost:8000"
echo "Frontend build is in frontend/dist/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000






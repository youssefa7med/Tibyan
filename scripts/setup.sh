#!/bin/bash

# PPE Safety Monitoring System - Setup Script
# This script prepares the system for production deployment

set -e

echo "=========================================="
echo "PPE Safety Monitoring System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3.8+ required"; exit 1; }

# Check Node.js version
echo "Checking Node.js version..."
node --version || { echo "Node.js 18+ required"; exit 1; }

# Create virtual environment for backend
echo ""
echo "Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Create storage directory
echo ""
echo "Creating storage directories..."
mkdir -p backend/app/storage
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "Please edit backend/.env with your configuration"
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Run: ./scripts/deploy.sh"
echo ""






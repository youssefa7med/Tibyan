@echo off
REM PPE Safety Monitoring System - Local Start Script for Windows
REM This script starts both backend and frontend for local on-premises use

echo ==========================================
echo PPE Safety Monitoring System
echo Local On-Premises Startup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo [1/4] Setting up backend...
cd backend

REM Do not create virtual environment automatically
if not exist "venv" (
    echo ERROR: Python virtual environment not found at backend\venv
    echo Please create it manually first:
    echo   cd backend
    echo   python -m venv venv
    pause
    exit /b 1
)

echo Installing backend dependencies from requirements.txt...
venv\Scripts\python -m pip install -r requirements.txt

REM Do not create .env automatically
if not exist ".env" (
    echo WARNING: backend\.env not found. Using default environment values.
)

cd ..

echo [2/4] Setting up frontend...
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

cd ..

echo [3/4] Starting backend server...
start "PPE Backend" cmd /k "cd backend && venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

echo [4/4] Starting frontend server...
start "PPE Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo Startup complete!
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window...
echo (The backend and frontend will continue running)
pause >nul
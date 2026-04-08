# How to Run Frontend and Backend

## 🚀 Quick Start (Easiest Method)

### Windows - One-Click Start
```batch
start_local.bat
```
This automatically starts both backend and frontend in separate windows.

### Linux/Mac - One-Click Start
```bash
chmod +x start_local.sh
./start_local.sh
```

---

## 📋 Manual Method (Step by Step)

### Step 1: Start Backend

**Open Terminal/PowerShell 1:**

```bash
# Navigate to backend folder
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running on http://localhost:8000**

---

### Step 2: Start Frontend

**Open a NEW Terminal/PowerShell 2:**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend development server
npm run dev
```

**You should see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is running on http://localhost:5173**

---

## 🌐 Access the Application

1. **Open your browser**
2. **Go to:** http://localhost:5173
3. **You should see:** The Welcome/Documentation page

---

## ✅ Verify Everything is Working

### Check Backend
Open browser and go to: http://localhost:8000/api/health

You should see:
```json
{
  "ok": true,
  "name": "PPE Safety Monitoring System",
  "time": "2024-...",
  "version": "2.0.0",
  "running": false
}
```

### Check Frontend
- Open http://localhost:5173
- You should see the Welcome page with documentation

### Test the System
1. Click "Get Started" or go to Dashboard
2. Go to "Live Monitor" page
3. Click "Start" button
4. You should see real-time updates!

---

## 🛑 How to Stop

### Stop Backend
- In Terminal 1, press: `Ctrl + C`

### Stop Frontend
- In Terminal 2, press: `Ctrl + C`

---

## 🔧 Troubleshooting

### Backend won't start?

**Problem:** Port 8000 already in use
```bash
# Windows: Find what's using port 8000
netstat -ano | findstr :8000

# Linux/Mac: Find what's using port 8000
lsof -i :8000

# Solution: Kill the process or use different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Problem:** Python not found
```bash
# Check Python version
python --version
# Should be 3.8 or higher

# If not installed, download from python.org
```

**Problem:** Module not found
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start?

**Problem:** Port 5173 already in use
```bash
# Vite will automatically use next available port
# Or specify different port:
npm run dev -- --port 3000
```

**Problem:** Node modules not found
```bash
# Install dependencies
npm install
```

**Problem:** Can't connect to backend
- Make sure backend is running on port 8000
- Check backend terminal for errors
- Verify http://localhost:8000/api/health works

---

## 📝 First Time Setup Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Browser can access http://localhost:5173

---

## 🎯 Quick Reference

| Component | Command | Port | URL |
|-----------|---------|------|-----|
| Backend | `uvicorn app.main:app --host 0.0.0.0 --port 8000` | 8000 | http://localhost:8000 |
| Frontend | `npm run dev` | 5173 | http://localhost:5173 |
| Health Check | - | 8000 | http://localhost:8000/api/health |

---

## 💡 Tips

1. **Keep both terminals open** - Backend and Frontend need to run simultaneously
2. **Auto-reload enabled** - Both will automatically reload when you change code
3. **Check terminal output** - Errors will show in the terminal
4. **Demo mode** - Works out of the box, no configuration needed
5. **Data persists** - CSV logs are saved in `backend/app/storage/`

---

## 🚀 That's It!

You're ready to use the PPE Safety Monitoring System locally!






# Quick Start - Local On-Premises

## 🚀 Fastest Way to Run Locally

### Windows

**Option 1: Use the start script (Easiest)**
```batch
start_local.bat
```
This will automatically:
- Set up backend virtual environment
- Install dependencies
- Start backend on port 8000
- Start frontend on port 5173

**Option 2: Manual start**

**Terminal 1 - Backend:**
```batch
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```batch
cd frontend
npm install
npm run dev
```

### Linux/Mac

**Option 1: Use the start script**
```bash
chmod +x start_local.sh
./start_local.sh
```

**Option 2: Manual start**

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

## ✅ What You'll See

1. **Welcome Page** - Documentation with Problem Statement and Proposed Solution
2. **Dashboard** - Real-time monitoring dashboard
3. **Live Monitor** - Click "Start" to begin monitoring
4. **Alerts** - View safety alerts
5. **Logs** - View CSV logs
6. **Settings** - Configure the system

## 📝 Notes

- **Demo Mode**: Enabled by default - perfect for testing
- **No Internet Required**: Works completely offline
- **Data Storage**: CSV logs saved in `backend/app/storage/`
- **Auto-Reload**: Backend and frontend auto-reload on code changes

## 🔧 Configuration (Optional)

Edit `backend/.env` if you want to:
- Enable Telegram notifications
- Change demo mode settings
- Configure CORS for network access

Default settings work perfectly for local use!

## 🎉 You're Ready!

Just run the start script or manual commands above, and you're good to go!






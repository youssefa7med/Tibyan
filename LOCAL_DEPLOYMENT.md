# Local On-Premises Deployment Guide

This guide covers deploying the PPE Safety Monitoring System on your local machine or local network server (on-premises).

## 🏠 Local On-Premises Setup

### Option 1: Simple Local Development (Recommended for Testing)

#### Windows

1. **Backend Setup:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   
   # Create .env file
   copy .env.example .env
   # Edit .env with notepad or your editor
   
   # Run backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Setup (New Terminal):**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

3. **Access:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Health: http://localhost:8000/api/health

#### Linux/Mac

1. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   nano .env  # Edit with your settings
   
   # Run backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Setup (New Terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Option 2: Production Build for Local Network

#### Step 1: Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with production files.

#### Step 2: Run Backend as Service

**Windows (Using Task Scheduler or NSSM):**

1. Create a batch file `start_backend.bat`:
   ```batch
   @echo off
   cd /d D:\data science\note.books\Safety Helmet Vest\ppe-mockup\backend
   call venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Use NSSM (Non-Sucking Service Manager) to run as Windows service:
   ```powershell
   # Download NSSM from https://nssm.cc/download
   nssm install PPEMonitoringBackend "D:\path\to\start_backend.bat"
   nssm start PPEMonitoringBackend
   ```

**Linux (Using systemd):**

Create `/etc/systemd/system/ppe-backend.service`:
```ini
[Unit]
Description=PPE Safety Monitoring Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/ppe-mockup/backend
Environment="PATH=/path/to/ppe-mockup/backend/venv/bin"
ExecStart=/path/to/ppe-mockup/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ppe-backend
sudo systemctl start ppe-backend
```

#### Step 3: Serve Frontend

**Option A: Simple HTTP Server (Python)**
```bash
cd frontend/dist
python -m http.server 3000
# Access at http://localhost:3000
```

**Option B: Nginx (Recommended for Production)**

Install Nginx and configure:

**Windows:**
- Download Nginx for Windows
- Edit `conf/nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    root C:/path/to/ppe-mockup/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

**Linux:**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/ppe-monitoring
# Paste configuration above, update paths
sudo ln -s /etc/nginx/sites-available/ppe-monitoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Configuration for Local Network Access

### Backend Configuration

Edit `backend/.env`:
```env
APP_NAME=PPE Safety Monitoring System - Local
DEMO_MODE=true

# Allow access from local network
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://YOUR_IP:3000,http://YOUR_IP:5173

# Telegram (optional)
TELEGRAM_ENABLED=false
```

### Frontend Configuration

Create `frontend/.env.local` (optional):
```env
VITE_API_URL=http://YOUR_IP:8000
VITE_WS_URL=ws://YOUR_IP:8000
```

Or access via:
- Local: http://localhost:5173 (dev) or http://localhost:3000 (production)
- Network: http://YOUR_IP:5173 (dev) or http://YOUR_IP:3000 (production)

## 🌐 Accessing from Other Devices on Local Network

1. **Find your IP address:**
   - Windows: `ipconfig` (look for IPv4 Address)
   - Linux/Mac: `ifconfig` or `ip addr`

2. **Update CORS in backend/.env:**
   ```env
   CORS_ORIGINS=http://localhost:5173,http://YOUR_IP:5173,http://YOUR_IP:3000
   ```

3. **Access from other devices:**
   - http://YOUR_IP:5173 (development)
   - http://YOUR_IP:3000 (production build)

4. **Firewall (if needed):**
   - Windows: Allow ports 8000, 5173, 3000 in Windows Firewall
   - Linux: `sudo ufw allow 8000/tcp` and `sudo ufw allow 3000/tcp`

## 📁 Directory Structure for Local Deployment

```
D:\data science\note.books\Safety Helmet Vest\ppe-mockup\
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── storage/          # CSV logs stored here
│   ├── venv/                 # Python virtual environment
│   ├── .env                  # Local configuration
│   └── requirements.txt
├── frontend/
│   ├── dist/                 # Production build (after npm run build)
│   ├── src/
│   └── package.json
└── ppe_enhanced.py
```

## 🚀 Quick Start Commands

### Development Mode (Both running)

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Production Mode

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (Built):**
```bash
cd frontend/dist
python -m http.server 3000
```

## 🔍 Verification

1. **Check Backend:**
   ```bash
   curl http://localhost:8000/api/health
   # Should return: {"ok":true,"name":"PPE Safety Monitoring System",...}
   ```

2. **Check Frontend:**
   - Open browser to http://localhost:5173 (dev) or http://localhost:3000 (prod)
   - Should see Welcome/Documentation page

3. **Test WebSocket:**
   - Open browser console
   - Should see WebSocket connection status

## 📊 Data Storage

All CSV logs are stored in:
- `backend/app/storage/safety_log.csv`
- `backend/app/storage/safety_summary.csv`

These files persist between restarts.

## 🔒 Security for Local Network

1. **Firewall**: Only open necessary ports (8000, 3000, 5173)
2. **Access Control**: Consider adding authentication if on shared network
3. **HTTPS**: For production, consider setting up local SSL certificate

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux)
- Check Python version: `python --version` (should be 3.8+)
- Check virtual environment is activated

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in backend/.env
- Check firewall settings
- Try accessing backend directly: http://localhost:8000/api/health

### WebSocket disconnected
- Check backend is running
- Verify WebSocket endpoint: ws://localhost:8000/ws/events
- Check browser console for errors

## 📝 Notes

- **Demo Mode**: Enabled by default - perfect for local testing
- **No Internet Required**: Works completely offline (except optional Telegram/AI features)
- **Data Persistence**: CSV logs are saved locally
- **Easy Updates**: Just restart services after code changes

## ✅ Checklist for Local Deployment

- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend .env configured
- [ ] Backend running on port 8000
- [ ] Frontend accessible
- [ ] WebSocket connecting
- [ ] CSV logs generating

Your system is ready for local on-premises use! 🎉






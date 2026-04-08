# PPE Safety Monitoring System - Production Ready

AI-Enhanced Real-Time Personal Protective Equipment Detection & Compliance Monitoring System

## 🎯 Overview

This is a production-ready PPE (Personal Protective Equipment) safety monitoring system that uses advanced computer vision and machine learning to detect and monitor safety helmet and vest compliance in real-time.

## 📋 Problem Statement

Workplace safety is critical in construction, manufacturing, and industrial environments. Manual monitoring of PPE compliance is:
- Time-consuming and inconsistent
- Prone to human error
- Unable to provide real-time detection
- Lacks automated alerting and comprehensive reporting

## 💡 Proposed Solution

Our AI-Enhanced PPE Safety Monitoring System provides:
- **Real-Time Detection**: Continuous monitoring using computer vision
- **Intelligent Tracking**: Advanced person tracking with temporal consistency
- **Automated Alerts**: Instant notifications via Telegram
- **Comprehensive Reporting**: Detailed CSV logging and compliance reports

## ✨ Key Features

### Intelligence Features
- ✅ **Adaptive Confidence Thresholding** - Auto-adjusts based on scene conditions
- ✅ **Enhanced Temporal Consistency (EMA)** - Smoother status decisions
- ✅ **Occlusion Detection & Handling** - Handles overlapping persons intelligently
- ✅ **Scene-Aware Quality Analysis** - Adapts to lighting/blur conditions
- ✅ **PPE Memory System** - Remembers last seen PPE during occlusions
- ✅ **Enhanced Spatial Association** - Uses body proportions for smarter matching

### System Features
- ✅ Real-time WebSocket streaming
- ✅ Comprehensive CSV logging
- ✅ Production-ready error handling
- ✅ On-premises deployment support
- ✅ Modern, responsive UI

## 🏗️ Project Structure

```
ppe-mockup/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI backend with enhanced features
│   │   └── storage/         # CSV logs and data
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Welcome.jsx  # Documentation page
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Live.jsx
│   │   │   ├── Alerts.jsx
│   │   │   ├── Logs.jsx
│   │   │   └── Settings.jsx
│   │   ├── components/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── ppe_enhanced.py         # Core AI processing engine
├── models/                 # YOLO model files
│   ├── yolov8n.pt
│   └── best.pt
├── deployment/             # Production deployment files
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── scripts/                # Deployment scripts
│   ├── setup.sh
│   └── deploy.sh
└── README.md
```

## 🚀 Quick Start - Local On-Premises Deployment

### Prerequisites

- Python 3.8+
- Node.js 18+
- YOLO model files (yolov8n.pt, best.pt) - Optional for demo mode

### Quick Start (Development Mode)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env  # Windows: copy .env.example .env
# Edit .env with your settings (optional for demo mode)

# Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health

### Production Build (Optional)

For production build to serve on local network:

```bash
# Build frontend
cd frontend
npm run build

# Serve built files
cd dist
python -m http.server 3000
# Access at http://localhost:3000
```

**See [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) for detailed local deployment guide.**

## 🔧 Configuration

### Environment Variables (.env)

```env
# Application
APP_NAME=PPE Safety Monitoring System
DEMO_MODE=true

# Telegram (Optional)
TELEGRAM_ENABLED=false
TELEGRAM_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_COOLDOWN_SECONDS=30

# AI Assistant (Optional)
AI_ENABLED=false
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat
AI_API_KEY=your_api_key_here

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📦 Local On-Premises Deployment

### Quick Start (Easiest)

**Windows:**
```batch
start_local.bat
```

**Linux/Mac:**
```bash
chmod +x start_local.sh
./start_local.sh
```

### Manual Deployment

1. **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev  # Development
   # OR
   npm run build  # Production build
   ```

### Access from Local Network

1. Find your IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
2. Update `backend/.env`: Add your IP to `CORS_ORIGINS`
3. Access from other devices: `http://YOUR_IP:5173`

**See [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) for detailed guide.**
**See [QUICK_START_LOCAL.md](QUICK_START_LOCAL.md) for fastest setup.**

## 📊 API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Current statistics
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration
- `GET /api/alerts` - Get alerts
- `GET /api/logs` - Get logs
- `GET /api/reports/safety_log.csv` - Download safety log
- `GET /api/reports/safety_summary.csv` - Download summary
- `POST /api/monitor/start` - Start monitoring
- `POST /api/monitor/stop` - Stop monitoring
- `WS /ws/events` - WebSocket for real-time events

## 🧪 Testing

### Demo Mode

The system includes a demo mode that simulates realistic monitoring scenarios:
- Multiple workers with varying PPE compliance
- Real-time status changes
- Alert generation
- CSV logging

Start the backend and frontend, then click "Start" in the Live Monitor page.

## 📝 CSV Logging

The system generates two types of CSV files:

1. **safety_log.csv** - Frame-by-frame detailed logs
2. **safety_summary.csv** - Interval summaries with comprehensive metrics

Both files are stored in `backend/app/storage/` and can be downloaded via API.

## 🔒 Security Considerations

- Never commit `.env` files with sensitive data
- Use environment variables for all secrets
- Configure CORS appropriately for production
- Use HTTPS in production
- Secure WebSocket connections (WSS)

## 🛠️ Technology Stack

### Backend
- FastAPI - Modern Python web framework
- YOLOv8 - Object detection
- ByteTrack - Multi-object tracking
- OpenCV - Computer vision
- NumPy - Numerical computations

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- WebSocket API - Real-time updates

## 📄 License

This project is provided as-is for production use.

## 🤝 Support

For issues and questions, please refer to the documentation in the Welcome page of the application.

## 📈 Future Enhancements

- [ ] Real video stream integration
- [ ] Multi-camera support
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Integration with existing safety systems
- [ ] Custom model training interface


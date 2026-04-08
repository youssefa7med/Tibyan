# Production Deployment Guide - Local On-Premises

This guide covers deploying the PPE Safety Monitoring System on your local machine or local network server (on-premises deployment).

## 📋 Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Node.js 18+
- Nginx (for production frontend serving)
- Systemd (for service management)

## 🚀 Quick Deployment

### Option 1: Using Deployment Scripts

```bash
# 1. Setup
./scripts/setup.sh

# 2. Configure
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# 3. Deploy
./scripts/deploy.sh
```

### Option 2: Docker Deployment

```bash
cd deployment
docker-compose up -d
```

### Option 3: Manual Deployment

Follow the detailed steps below.

## 📦 Manual Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install python3 python3-pip python3-venv nodejs npm nginx -y
```

### 2. Clone/Copy Project

```bash
# Copy project to /opt/ppe-monitoring (or your preferred location)
sudo mkdir -p /opt/ppe-monitoring
sudo cp -r . /opt/ppe-monitoring/
cd /opt/ppe-monitoring
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Test backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# The built files are in dist/
```

### 5. Create Systemd Service

Create `/etc/systemd/system/ppe-backend.service`:

```ini
[Unit]
Description=PPE Safety Monitoring Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ppe-monitoring/backend
Environment="PATH=/opt/ppe-monitoring/backend/venv/bin"
ExecStart=/opt/ppe-monitoring/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
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
sudo systemctl status ppe-backend
```

### 6. Configure Nginx

Create `/etc/nginx/sites-available/ppe-monitoring`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change to your domain or IP

    # Frontend
    root /opt/ppe-monitoring/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket proxy
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

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/ppe-monitoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend port (if needed externally)
sudo ufw allow 8000/tcp
```

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```env
APP_NAME=PPE Safety Monitoring System - Production
DEMO_MODE=false  # Set to false for real video processing

# Telegram (if enabled)
TELEGRAM_ENABLED=true
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# CORS (update with your domain)
CORS_ORIGINS=https://your-domain.com,http://your-domain.com
```

### Model Files

Ensure model files are in the project root:
- `yolov8n.pt` - Person detection model
- `best.pt` - PPE detection model

## 📊 Monitoring

### View Logs

```bash
# Backend logs
sudo journalctl -u ppe-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Check Status

```bash
# Backend service
sudo systemctl status ppe-backend

# Nginx
sudo systemctl status nginx
```

## 🔄 Updates

### Update Backend

```bash
cd /opt/ppe-monitoring/backend
source venv/bin/activate
git pull  # or copy new files
pip install -r requirements.txt
sudo systemctl restart ppe-backend
```

### Update Frontend

```bash
cd /opt/ppe-monitoring/frontend
npm install
npm run build
sudo systemctl reload nginx
```

## 🛡️ Security Considerations

1. **Use HTTPS**: Set up SSL certificates (Let's Encrypt)
2. **Firewall**: Only expose necessary ports
3. **Environment Variables**: Never commit `.env` files
4. **User Permissions**: Run services with limited privileges
5. **Regular Updates**: Keep system and dependencies updated

## 📁 Directory Structure

```
/opt/ppe-monitoring/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── storage/          # CSV logs
│   ├── venv/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── dist/                 # Built frontend
│   └── src/
├── ppe_enhanced.py
├── models/
│   ├── yolov8n.pt
│   └── best.pt
└── scripts/
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u ppe-backend -n 50

# Check Python path
which python3
python3 --version

# Test manually
cd /opt/ppe-monitoring/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend not loading

```bash
# Check Nginx config
sudo nginx -t

# Check file permissions
sudo chown -R www-data:www-data /opt/ppe-monitoring/frontend/dist

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### WebSocket not connecting

- Ensure `/ws` location is configured in Nginx
- Check firewall allows WebSocket connections
- Verify backend is running on port 8000

## 📞 Support

For issues, check:
1. Application logs: `sudo journalctl -u ppe-backend`
2. Nginx logs: `/var/log/nginx/`
3. Backend storage: `backend/app/storage/`


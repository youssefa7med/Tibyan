# WebSocket Connection Troubleshooting

## 🔍 Quick Diagnosis

### Step 1: Check if Backend is Running

**Windows PowerShell:**
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000
```

**Or test the API:**
```powershell
# Test backend health
Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing
```

**Expected response:**
```json
{
  "ok": true,
  "name": "PPE Safety Monitoring System",
  "time": "...",
  "version": "2.0.0",
  "running": false
}
```

### Step 2: Check Backend Logs

Look at the terminal where you started the backend. You should see:
- `INFO:     Uvicorn running on http://0.0.0.0:8000`
- `INFO:     Application startup complete.`
- When WebSocket connects: `INFO: WebSocket client connected`

### Step 3: Test WebSocket Directly

Open `test_websocket.html` in your browser (double-click the file).

This will test the WebSocket connection directly.

## 🔧 Common Issues and Fixes

### Issue 1: Backend Not Running

**Symptoms:**
- WebSocket connection fails immediately
- Frontend shows "Disconnected"

**Fix:**
1. Make sure backend is running:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Verify it's running:
   - Check terminal for "Uvicorn running" message
   - Test http://localhost:8000/api/health in browser

### Issue 2: Backend Crashed

**Symptoms:**
- Backend was running but stopped
- Error messages in backend terminal

**Fix:**
1. Check backend terminal for error messages
2. Restart backend:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Issue 3: Port Already in Use

**Symptoms:**
- Backend won't start
- Error: "Address already in use"

**Fix:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Then update frontend `api.js` to use port 8001.

### Issue 4: CORS Issues

**Symptoms:**
- WebSocket connects but immediately disconnects
- Browser console shows CORS errors

**Fix:**
1. Check `backend/.env`:
   ```env
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. Restart backend after changing .env

### Issue 5: WebSocket Path Wrong

**Symptoms:**
- Connection fails with 404

**Fix:**
- Verify WebSocket URL is: `ws://localhost:8000/ws/events`
- Check `frontend/src/api.js` - `wsUrl()` function

## 🛠️ Step-by-Step Fix

### 1. Stop Everything
- Press `Ctrl+C` in backend terminal
- Press `Ctrl+C` in frontend terminal

### 2. Restart Backend
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Wait for: `INFO: Application startup complete.`

### 3. Test Backend
Open browser: http://localhost:8000/api/health

Should see JSON response.

### 4. Restart Frontend
```powershell
cd frontend
npm run dev
```

### 5. Check Browser Console
- Open browser DevTools (F12)
- Go to Console tab
- Look for WebSocket connection messages
- Should see: "Connecting to WebSocket: ws://localhost:8000/ws/events"
- Then: "WebSocket connected"

### 6. Check Network Tab
- Open DevTools → Network tab
- Filter by "WS" (WebSocket)
- Click on the WebSocket connection
- Check Status should be "101 Switching Protocols"

## ✅ Verification Checklist

- [ ] Backend terminal shows "Uvicorn running"
- [ ] http://localhost:8000/api/health returns JSON
- [ ] Frontend terminal shows "VITE ready"
- [ ] Browser console shows "WebSocket connected"
- [ ] Frontend shows "Connected" status (green dot)
- [ ] No errors in browser console
- [ ] No errors in backend terminal

## 🆘 Still Not Working?

1. **Check Backend Logs:**
   - Look at backend terminal
   - Copy any error messages

2. **Check Browser Console:**
   - Press F12
   - Go to Console tab
   - Copy any error messages

3. **Test WebSocket Manually:**
   - Open `test_websocket.html` in browser
   - See if it connects

4. **Restart Everything:**
   - Close all terminals
   - Restart backend
   - Restart frontend
   - Hard refresh browser (Ctrl+Shift+R)

## 📝 Debug Information to Collect

If still having issues, collect:
1. Backend terminal output (last 20 lines)
2. Browser console errors
3. Network tab WebSocket status
4. Output of: `netstat -ano | findstr :8000`






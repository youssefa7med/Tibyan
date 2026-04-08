# Video Streaming Setup Guide

## 📹 How to See Camera Stream

### Step 1: Install OpenCV

The video streaming requires OpenCV. Install it:

```bash
pip install opencv-python numpy
```

Or if you're using the requirements file:
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Video Source

1. Go to **Settings** page
2. In **Camera & Video Source** section:
   - Enter camera index: `0` (for first camera), `1` (for second camera), etc.
   - Or enter video file path: `C:\Videos\test.mp4`
   - Or enter RTSP stream: `rtsp://username:password@ip:port/stream`
3. Select **Mode: Real Mode (Live Video Processing)**
4. Click **Save & Apply**

### Step 3: Start Monitoring

1. Go to **Live Monitor** page
2. Click **Start** button
3. The camera stream will appear automatically!

## 🎥 What You'll See

- **Real Mode**: Actual video feed from your camera with bounding boxes overlaid
- **Demo Mode**: Canvas with simulated bounding boxes (no camera needed)

## 🔧 Troubleshooting

### Camera Not Showing

1. **Check OpenCV is installed:**
   ```bash
   python -c "import cv2; print(cv2.__version__)"
   ```

2. **Check camera index:**
   - Try `0`, `1`, `2` in Settings
   - Check if camera is being used by another app

3. **Check backend logs:**
   - Look for "Video capture started" message
   - Check for camera errors

4. **Test camera directly:**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   print("Camera works!" if ret else "Camera failed")
   cap.release()
   ```

### Video Stream Error

- Check browser console (F12) for errors
- Verify backend is running
- Check if camera is accessible
- Try different camera index

### Black Screen

- Make sure you clicked "Start"
- Check Settings → Mode is set to "Real Mode"
- Verify camera is connected and working
- Check backend terminal for errors

## ✅ Quick Test

1. Install: `pip install opencv-python numpy`
2. Settings → Video Source: `0` → Mode: `Real Mode` → Save
3. Live Monitor → Click **Start**
4. You should see your camera feed!

## 📝 Notes

- **Demo Mode**: Works without camera (simulated data)
- **Real Mode**: Requires camera and OpenCV
- **Video File**: Can use video file path instead of camera
- **RTSP**: Supports RTSP streams for IP cameras






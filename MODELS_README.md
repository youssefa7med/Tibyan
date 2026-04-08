# Missing Model Files - PPE Detection

## Problem
Your **PPE Safety Monitoring System** is running, but real camera detection won't work because the YOLO model files are missing:
- `yolov8n.pt` - Person detection model (required)
- `best.pt` - PPE detection model (custom trained)

When you try real mode without these files, the system automatically falls back to **demo mode** (simulated detections).

## Solution

### Option 1: Download Person Model (yolov8n.pt)
The person detection model can be auto-downloaded.

```bash
# Navigate to project root
cd d:\data science\note.books\Safety Helmet Vest\ppe-mockup

# Run setup script
python setup_models.py
```

This will download `yolov8n.pt` automatically (~83MB).

### Option 2: Download From Ultralytics
If the script doesn't work, download manually:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Option 3: Get PPE Detection Model (best.pt)
The `best.pt` file is a **custom-trained model** and cannot auto-download. You have options:

1. **Train Your Own:**
   - See `ppe_enhanced.py` for training code
   - Use your own PPE dataset or public datasets from Roboflow

2. **Download Pre-trained PPE Models:**
   - [Roboflow PPE Detection](https://roboflow.com/search?q=safety%20helmet)
   - [Ultralytics Models Hub](https://hub.ultralytics.com/)
   - Search for "YOLO PPE detection" or "helmet vest detection"

3. **Placeholder for Testing:**
   - If you just want to test, use person model for both:
   ```python
   # Copy yolov8n.pt to best.pt temporarily
   cp yolov8n.pt best.pt
   ```
   This will detect people but won't distinguish PPE items.

## After Placing Models

1. Place model files in project root:
   ```
   ppe-mockup/
   ├── yolov8n.pt      (person detection)
   ├── best.pt         (PPE detection)
   ├── backend/
   ├── frontend/
   └── ...
   ```

2. Open Settings → Camera & Video Source
3. Change Mode to "Real"
4. Click Start
5. Real detection should now work!

## Current Mode Status

Your system is currently in:
- **Demo Mode**: Uses simulated detections (always works, useful for testing UI)
- **Real Mode (with models)**: Uses actual camera + AI detection

Check the Alerts page for any errors about missing models.

## Troubleshooting

If you still get "No Detections":
- Check backend terminal for error messages
- Verify model files are in project root (not in backend/)
- Ensure camera is working (test in another app first)
- Check Settings page for camera source configuration
- Try lowering confidence threshold in Settings

## Need Help?

1. Check the **Alerts** page in the app - it shows detailed errors
2. Look at backend terminal output for model loading messages
3. Verify camera access: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

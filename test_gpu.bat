@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo Testing GPU setup...
"%~dp0venv\Scripts\python.exe" -c "import torch; from ultralytics import YOLO; print('CUDA Available:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'); m = YOLO('yolov8n.pt'); print('Model loaded on device:', m.device); print('PyTorch version:', torch.__version__)"
pause

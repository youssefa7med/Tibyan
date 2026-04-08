@echo off
REM Install PyTorch with CUDA 12.1 support
echo Installing PyTorch with CUDA 12.1 support...
"%~dp0venv\Scripts\python.exe" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --force-reinstall --no-deps
if %errorlevel% equ 0 (
    echo Installation successful!
) else (
    echo Installation failed with error code %errorlevel%
)
echo.
pause

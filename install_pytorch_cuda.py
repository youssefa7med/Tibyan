#!/usr/bin/env python
"""Install PyTorch with CUDA support - compatible with Python 3.13"""
import subprocess
import sys

print("Installing PyTorch with CUDA 12.4 support (Python 3.13 compatible)...")
print("This may take 3-5 minutes...")
print()

# Try CUDA 12.4 first (best for Python 3.13)
versions_to_try = [
    ("CUDA 12.4", "https://download.pytorch.org/whl/cu124"),
    ("CUDA 12.1", "https://download.pytorch.org/whl/cu121"),
]

for version_name, index_url in versions_to_try:
    print(f"Trying {version_name}...")
    
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir",
        "torch", "torchvision", "torchaudio",
        "--index-url", index_url
    ])
    
    if result.returncode == 0:
        print(f"\n✅ {version_name} installation successful!")
        break
    else:
        print(f"❌ {version_name} failed, trying next...")

print()
print("Installation complete. Checking...")
print()

# Check installation
try:
    import torch
    print(f"✅ PyTorch Version: {torch.__version__}")
    print(f"✅ CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        # Test a simple operation
        x = torch.rand(3, 3).cuda()
        print(f"✅ GPU Computation Test: OK")
    else:
        print("⚠️  CUDA not detected - GPU may not be available")
except Exception as e:
    print(f"❌ Error: {e}")

input("\nPress Enter to exit...")


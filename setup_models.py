#!/usr/bin/env python3
"""
Download required YOLO models for PPE detection.
Run this once before using real mode: python setup_models.py
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download YOLO models using ultralytics."""
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not installed")
        print("Install with: pip install ultralytics")
        return False
    
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("Downloading YOLO Models for PPE Detection")
    print("=" * 60)
    print()
    
    models = [
        ("yolov8n.pt", "Person Detection Model (80MB)"),
        ("best.pt", "PPE Detection Model (custom trained)")
    ]
    
    for model_name, description in models:
        model_path = project_root / model_name
        
        if model_path.exists():
            print(f"✓ {description}")
            print(f"  Already exists: {model_path}")
            continue
        
        print(f"↓ Downloading {description}")
        print(f"  {model_name}...")
        
        try:
            if model_name == "yolov8n.pt":
                # Download from ultralytics
                model = YOLO("yolov8n.pt")
                print(f"  ✓ Downloaded yolov8n.pt (person detection)")
            elif model_name == "best.pt":
                print(f"  ⚠ {model_name} is a custom-trained model")
                print(f"    This model was trained on custom PPE data")
                print(f"    You need to:")
                print(f"    1. Train it yourself: see ppe_enhanced.py for training code")
                print(f"    2. Or use a pre-trained PPE model from Roboflow/Ultralytics")
                print(f"    3. Download and place it in: {model_path}")
                print()
                return False
        except Exception as e:
            print(f"  ✗ Failed to download: {e}")
            return False
    
    print()
    print("=" * 60)
    print("✓ Models ready! You can now use Real Mode.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)

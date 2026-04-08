"""
Production-Ready PPE Safety Monitoring System Backend
Integrated with ppe_enhanced.py intelligence features
"""

import os
import csv
import time
import json
import asyncio
import logging
import io
import base64
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from collections import deque

if TYPE_CHECKING:
    import numpy as np

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Import enhanced PPE processing utilities
# Note: Full integration with ppe_enhanced.py video processing can be added later
# For now, we use the demo mode which simulates the enhanced features

def determine_status(has_helmet: bool, has_vest: bool, unsafe_counter: int, threshold: int = 3):
    """Determine safety status based on PPE and counter."""
    if has_helmet and has_vest:
        return "SAFE", 0
    c = unsafe_counter + 1
    if c >= threshold:
        return "UNSAFE", c
    return "CHECK", c

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import OpenCV for video streaming (after logger is set up)
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
    logger.info("OpenCV available - video streaming enabled")
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available - video streaming disabled. Install with: pip install opencv-python")

# Try to import YOLO models
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    logger.info("YOLO available - model-based detection enabled")
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("YOLO not available - Install with: pip install ultralytics")

# Try to import torch for CUDA detection
try:
    import torch
    TORCH_AVAILABLE = True
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        logger.info(f"CUDA available - GPU: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("CUDA not available, will use CPU")
except ImportError:
    TORCH_AVAILABLE = False
    CUDA_AVAILABLE = False
    logger.warning("PyTorch not available")

APP_NAME = os.getenv("APP_NAME", "Tibyan - Safety Monitoring System")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent  # Go up from backend/app to project root
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

LOG_CSV = STORAGE_DIR / "safety_log.csv"
SUMMARY_CSV = STORAGE_DIR / "safety_summary.csv"

logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Base dir: {BASE_DIR}")

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------- Configuration Models ---------------- 
class AppConfig(BaseModel):
    video_source: str = Field(default="0", description="Camera index, file path, or RTSP")
    confidence: float = Field(default=0.3, ge=0.0, le=1.0)
    unsafe_threshold: int = Field(default=3, ge=1, le=30)
    
    # Enhanced features
    adaptive_confidence_enabled: bool = True
    min_confidence: float = Field(default=0.2, ge=0.0, le=1.0)
    max_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    use_ema_temporal: bool = True
    ema_alpha: float = Field(default=0.3, ge=0.0, le=1.0)
    unsafe_threshold_ema: float = Field(default=0.7, ge=0.0, le=1.0)
    
    occlusion_detection_enabled: bool = True
    occlusion_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    
    scene_quality_enabled: bool = True
    quality_check_interval: int = Field(default=30, ge=1, le=300)
    
    ppe_memory_enabled: bool = True
    ppe_memory_frames: int = Field(default=15, ge=1, le=100)
    
    use_body_proportions: bool = True
    
    anti_flicker_enabled: bool = True
    status_history_size: int = Field(default=5, ge=1, le=30)
    status_change_threshold: int = Field(default=3, ge=1, le=30)
    
    use_bytetrack: bool = True
    tracker_type: str = Field(default="bytetrack.yaml")
    
    telegram_enabled: bool = False
    telegram_cooldown_seconds: int = Field(default=30, ge=1, le=300)
    
    mode: str = Field(default="real", description="demo or real")
    
    # Camera location/identification
    camera_location: str = Field(default="Camera 1", description="Location or name of camera")
    
    # Model paths
    person_model_path: str = Field(default="yolov8n.pt", description="Path to person detection model")
    ppe_model_path: str = Field(default="best.pt", description="Path to PPE detection model")

DEFAULT_CONFIG = AppConfig(
    video_source="0",
    confidence=0.3,
    unsafe_threshold=3,
    adaptive_confidence_enabled=True,
    min_confidence=0.2,
    max_confidence=0.5,
    use_ema_temporal=True,
    ema_alpha=0.3,
    unsafe_threshold_ema=0.7,
    occlusion_detection_enabled=True,
    occlusion_threshold=0.3,
    scene_quality_enabled=True,
    quality_check_interval=30,
    ppe_memory_enabled=True,
    ppe_memory_frames=15,
    use_body_proportions=True,
    anti_flicker_enabled=True,
    status_history_size=5,
    status_change_threshold=3,
    use_bytetrack=True,
    tracker_type="bytetrack.yaml",
    telegram_enabled=os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
    telegram_cooldown_seconds=int(os.getenv("TELEGRAM_COOLDOWN_SECONDS", "30")),
    mode="demo" if os.getenv("DEMO_MODE", "false").lower() == "true" else "real",
    person_model_path=os.getenv("PERSON_MODEL_PATH", "yolov8n.pt"),
    ppe_model_path=os.getenv("PPE_MODEL_PATH", "best.pt"),
)

config_state: AppConfig = DEFAULT_CONFIG.model_copy(deep=True)

# ---------------- CSV Initialization ---------------- 
def init_csvs():
    """Initialize CSV files with proper headers."""
    if not LOG_CSV.exists():
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp", "camera_location", "frame_id", "person_id",
                "x1", "y1", "x2", "y2",
                "helmet", "vest", "status", "unsafe_counter",
                "ema_score", "occluded", "quality_score"
            ])

    if not SUMMARY_CSV.exists():
        with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp", "interval_start", "interval_end", "duration_seconds",
                "total_frames", "frames_with_persons", "frames_with_violations",
                "frames_all_safe", "violation_rate_percent",
                "avg_fps", "min_fps", "max_fps",
                "avg_quality", "quality_rating", "avg_confidence",
                "unique_persons", "total_detections", "avg_persons_per_frame",
                "max_persons", "min_persons",
                "total_safe", "total_check", "total_unsafe",
                "avg_safe_per_frame", "avg_check_per_frame", "avg_unsafe_per_frame",
                "max_unsafe_simultaneous",
                "total_helmets_detected", "total_vests_detected",
                "avg_helmets_per_frame", "avg_vests_per_frame",
                "helmet_detection_rate", "vest_detection_rate",
                "safety_compliance_percent", "full_compliance_percent",
                "partial_compliance_percent", "non_compliance_percent",
                "unsafe_incidents", "unique_unsafe_persons", "unique_check_persons",
                "occlusions_detected", "frames_with_occlusion", "avg_ema_score",
                "compliance_trend", "status"
            ])

init_csvs()

# ---------------- Telegram Notifier ---------------- 
class TelegramNotifierAPI:
    """Telegram notification handler for API."""
    def __init__(self):
        self.update_from_config()
        self.last_sent = 0.0

    def update_from_config(self):
        """Update settings from environment and config state."""
        # Check config state first, then fall back to environment
        self.enabled = (
            config_state.telegram_enabled if hasattr(config_state, 'telegram_enabled') 
            else os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
        )
        self.token = os.getenv("TELEGRAM_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.cooldown = (
            config_state.telegram_cooldown_seconds if hasattr(config_state, 'telegram_cooldown_seconds')
            else int(os.getenv("TELEGRAM_COOLDOWN_SECONDS", "30"))
        )

    def send_text(self, text: str) -> bool:
        """Send text message to Telegram."""
        # Update from config in case it changed
        self.update_from_config()
        
        if not self.enabled:
            logger.debug("Telegram disabled")
            return False
        
        if not self.token or not self.chat_id:
            logger.warning("Telegram token or chat_id not configured")
            return False

        now = time.time()
        if now - self.last_sent < self.cooldown:
            logger.debug(f"Telegram cooldown active ({self.cooldown}s)")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            r = requests.post(url, data={"chat_id": self.chat_id, "text": text}, timeout=10)
            ok = (r.status_code == 200)
            if ok:
                self.last_sent = now
                logger.info("Telegram message sent successfully")
            else:
                logger.error(f"Telegram API error: {r.status_code} - {r.text}")
            return ok
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
    
    def send_alert(self, frame, unsafe_count: int, total_persons: int, location: str = "Construction Site") -> bool:
        """Send safety alert with frame image to Telegram (like ppe_enhanced.py)."""
        # Update from config in case it changed
        self.update_from_config()
        
        if not self.enabled:
            return False
        
        if not self.token or not self.chat_id:
            return False
        
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available - cannot send frame to Telegram")
            return False
        
        now = time.time()
        if now - self.last_sent < self.cooldown:
            return False
        
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            files = {'photo': buffer.tobytes()}
            
            # Create caption
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            caption_text = generate_safety_alert_message(unsafe_count, total_persons, timestamp, location)
            
            # Send photo with caption
            url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
            r = requests.post(
                url,
                data={"chat_id": self.chat_id, "caption": caption_text},
                files=files,
                timeout=15
            )
            
            ok = (r.status_code == 200)
            if ok:
                self.last_sent = now
                logger.info("Telegram alert with frame sent successfully")
            else:
                logger.error(f"Telegram API error: {r.status_code} - {r.text}")
            return ok
        except Exception as e:
            logger.error(f"Telegram alert send failed: {e}")
            return False

telegram_api = TelegramNotifierAPI()

# ---------------- AI Assistant (optional) ---------------- 
def ai_enabled() -> bool:
    return os.getenv("AI_ENABLED", "false").lower() == "true"

def generate_safety_alert_message(unsafe_count: int, total_persons: int, timestamp: str, location: str = "Unknown") -> str:
    """Generate standardized safety alert message in English."""
    return (
        f"⚠️ SAFETY ALERT - TIBYAN VIOLATION DETECTED\n"
        f"📍 Location: {location}\n"
        f"Unsafe Workers: {unsafe_count}\n"
        f"Total Persons: {total_persons}\n"
        f"Time: {timestamp}\n"
        f"Status: Missing helmet and/or safety vest\n"
        f"Action Required: Ensure all workers wear proper PPE"
    )

def generate_alert_caption_with_ai(context: Dict[str, Any]) -> Optional[str]:
    """Generate alert caption using AI (OpenAI-compatible API)."""
    if not ai_enabled():
        return None

    base_url = os.getenv("AI_BASE_URL", "").rstrip("/")
    api_key = os.getenv("AI_API_KEY", "")
    model = os.getenv("AI_MODEL", "deepseek-chat")

    if not base_url or not api_key:
        return None

    system = "You write short, clear safety alert messages for a PPE monitoring system."
    user = (
        f"Create a Telegram alert message in English about unsafe workers.\n"
        f"Context:\n{json.dumps(context, ensure_ascii=False)}\n"
        f"Rules:\n- Keep it under 6 lines\n- Include counts and time\n- Professional tone\n- English only\n"
    )

    url = f"{base_url}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=12)
        if r.status_code != 200:
            return None
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"AI caption generation failed: {e}")
        return None

# ---------------- Intelligence Components (from ppe_enhanced.py) ---------------- 

def calculate_iou(box1: np.ndarray, box2: np.ndarray) -> float:
    """Calculate Intersection over Union between two boxes."""
    if not CV2_AVAILABLE:
        return 0.0
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return 0.0
    
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter / (area1 + area2 - inter)

def get_box_center(box: np.ndarray) -> tuple:
    """Get center point (x, y) of bounding box."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)

class SceneQualityAnalyzer:
    """Analyzes frame quality and adjusts detection parameters."""
    def __init__(self):
        self.quality_history = deque(maxlen=10)
        self.last_quality_score = 1.0
    
    def analyze_frame(self, frame) -> tuple:
        """Analyze frame quality and return score + metrics."""
        if not CV2_AVAILABLE:
            return 1.0, {'quality_score': 1.0, 'label': 'Good'}
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127
        contrast = np.std(gray)
        contrast_score = min(contrast / 64, 1.0)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        sharpness_score = min(sharpness / 500, 1.0)
        quality_score = (brightness_score * 0.3 + contrast_score * 0.3 + sharpness_score * 0.4)
        self.quality_history.append(quality_score)
        self.last_quality_score = np.mean(self.quality_history)
        return self.last_quality_score, {'quality_score': self.last_quality_score, 'label': self.get_quality_label()}
    
    def get_quality_label(self) -> str:
        """Get quality label for display."""
        if self.last_quality_score >= 0.75:
            return "Excellent"
        elif self.last_quality_score >= 0.6:
            return "Good"
        elif self.last_quality_score >= 0.4:
            return "Fair"
        else:
            return "Poor"

class AdaptiveConfidenceManager:
    """Dynamically adjusts confidence based on scene conditions."""
    def __init__(self, base_conf=0.3, min_conf=0.2, max_conf=0.5):
        self.base_conf = base_conf
        self.min_conf = min_conf
        self.max_conf = max_conf
        self.detection_history = deque(maxlen=30)
        self.current_conf = base_conf
    
    def update(self, detections_count: int, quality_score: float) -> float:
        """Update confidence based on detection density and scene quality."""
        self.detection_history.append(detections_count)
        if len(self.detection_history) < 5:
            return self.current_conf
        
        avg_detections = np.mean(self.detection_history) if CV2_AVAILABLE else detections_count
        conf_adjustment = -0.05 if avg_detections < 2 else (+0.05 if avg_detections > 10 else 0)
        quality_adjustment = (quality_score - 0.7) * 0.1
        new_conf = self.base_conf + conf_adjustment + quality_adjustment
        new_conf = max(self.min_conf, min(self.max_conf, new_conf))
        self.current_conf = 0.8 * self.current_conf + 0.2 * new_conf
        return self.current_conf

class OcclusionDetector:
    """Detects when persons are occluded by others."""
    def __init__(self, threshold=0.3):
        self.threshold = threshold
    
    def detect_occlusion(self, person_box: np.ndarray, all_person_boxes: List[np.ndarray]) -> float:
        """Calculate occlusion ratio for a person."""
        px1, py1, px2, py2 = person_box
        person_area = (px2 - px1) * (py2 - py1)
        if person_area <= 0:
            return 0.0
        
        max_occlusion = 0.0
        for other_box in all_person_boxes:
            if np.array_equal(other_box, person_box):
                continue
            ox1, oy1, ox2, oy2 = other_box
            x1 = max(px1, ox1)
            y1 = max(py1, oy1)
            x2 = min(px2, ox2)
            y2 = min(py2, oy2)
            if x2 > x1 and y2 > y1:
                overlap_area = (x2 - x1) * (y2 - y1)
                occlusion_ratio = overlap_area / person_area
                max_occlusion = max(max_occlusion, occlusion_ratio)
        return max_occlusion
    
    def is_occluded(self, person_box: np.ndarray, all_person_boxes: List[np.ndarray]) -> bool:
        """Check if person is significantly occluded."""
        return self.detect_occlusion(person_box, all_person_boxes) > self.threshold

class PPEMemoryManager:
    """Remembers last seen PPE for each person."""
    def __init__(self, memory_frames=15):
        self.memory_frames = memory_frames
        self.ppe_memory = {}
    
    def update(self, person_id: int, has_helmet: bool, has_vest: bool):
        """Update PPE memory for a person."""
        self.ppe_memory[person_id] = {'helmet': has_helmet, 'vest': has_vest, 'frames_ago': 0}
    
    def get_remembered_ppe(self, person_id: int) -> tuple:
        """Get remembered PPE status if within memory window."""
        if person_id not in self.ppe_memory:
            return None, None
        memory = self.ppe_memory[person_id]
        if memory['frames_ago'] > self.memory_frames:
            return None, None
        return memory['helmet'], memory['vest']
    
    def increment_age(self):
        """Increment age of all memories."""
        for person_id in list(self.ppe_memory.keys()):
            self.ppe_memory[person_id]['frames_ago'] += 1
            if self.ppe_memory[person_id]['frames_ago'] > self.memory_frames * 2:
                del self.ppe_memory[person_id]

class TemporalConsistencyEMA:
    """Uses Exponential Moving Average for smoother status decisions."""
    def __init__(self, alpha=0.3, unsafe_threshold=0.7):
        self.alpha = alpha
        self.unsafe_threshold = unsafe_threshold
        self.safety_scores = {}
    
    def update_score(self, person_id: int, has_helmet: bool, has_vest: bool) -> str:
        """Update safety score with EMA and return status."""
        current_score = 1.0 if (has_helmet and has_vest) else 0.0
        if person_id not in self.safety_scores:
            self.safety_scores[person_id] = current_score
        else:
            self.safety_scores[person_id] = (
                self.alpha * current_score + (1 - self.alpha) * self.safety_scores[person_id]
            )
        score = self.safety_scores[person_id]
        if score >= 0.9:
            return "SAFE"
        elif score >= self.unsafe_threshold:
            return "CHECK"
        else:
            return "UNSAFE"
    
    def get_score(self, person_id: int) -> float:
        """Get current safety score for visualization."""
        return self.safety_scores.get(person_id, 1.0)
    
    def reset(self, person_id: int):
        """Reset score for a person."""
        if person_id in self.safety_scores:
            del self.safety_scores[person_id]

def associate_ppe_enhanced(person_box: np.ndarray, helmets: List[np.ndarray],
                          vests: List[np.ndarray], use_proportions: bool = True) -> tuple:
    """Enhanced PPE association using spatial zones + body proportions."""
    if not CV2_AVAILABLE:
        return False, False
    
    px1, py1, px2, py2 = person_box
    person_height = py2 - py1
    person_width = px2 - px1
    
    if person_height <= 0:
        return False, False
    
    person_area = person_height * person_width
    expected_helmet_height = person_height * 0.125
    expected_vest_width = person_width * 0.7
    
    helmet_zone_top = py1 - person_height * 0.05
    helmet_zone_bottom = py1 + person_height * 0.40
    helmet_zone_center = py1 + person_height * 0.12
    
    vest_zone_top = py1 + person_height * 0.30
    vest_zone_bottom = py1 + person_height * 0.80
    vest_zone_center = py1 + person_height * 0.50
    
    has_helmet = False
    has_vest = False
    best_helmet_score = 0
    best_vest_score = 0
    
    for h in helmets:
        hx, hy = get_box_center(h)
        h_height = h[3] - h[1]
        h_width = h[2] - h[0]
        helmet_area = h_height * h_width
        in_width = px1 - person_width * 0.1 <= hx <= px2 + person_width * 0.1
        in_zone = helmet_zone_top <= hy <= helmet_zone_bottom
        
        if in_width and in_zone:
            if use_proportions:
                size_diff = abs(h_height - expected_helmet_height) / expected_helmet_height
                size_score = max(0, 1.0 - size_diff)
                pos_diff = abs(hy - helmet_zone_center) / person_height
                pos_score = max(0, 1.0 - pos_diff * 2)
                area_ratio = helmet_area / person_area if person_area > 0 else 0
                area_score = 1.0 if 0.05 <= area_ratio <= 0.20 else 0.5
                score = size_score * 0.35 + pos_score * 0.40 + area_score * 0.25
            else:
                size_ratio = min(helmet_area / person_area, person_area / helmet_area) if person_area > 0 else 0
                distance_score = 1.0 / (1.0 + abs(hy - helmet_zone_center) / person_height)
                score = size_ratio * 0.6 + distance_score * 0.4
            
            if score > best_helmet_score:
                best_helmet_score = score
                has_helmet = True
    
    for v in vests:
        vx, vy = get_box_center(v)
        v_height = v[3] - v[1]
        v_width = v[2] - v[0]
        vest_area = v_height * v_width
        in_width = px1 - person_width * 0.1 <= vx <= px2 + person_width * 0.1
        in_zone = vest_zone_top <= vy <= vest_zone_bottom
        
        if in_width and in_zone:
            if use_proportions:
                width_diff = abs(v_width - expected_vest_width) / expected_vest_width
                width_score = max(0, 1.0 - width_diff)
                pos_diff = abs(vy - vest_zone_center) / person_height
                pos_score = max(0, 1.0 - pos_diff * 2)
                area_ratio = vest_area / person_area if person_area > 0 else 0
                area_score = 1.0 if 0.15 <= area_ratio <= 0.50 else 0.5
                score = width_score * 0.35 + pos_score * 0.40 + area_score * 0.25
            else:
                size_ratio = min(vest_area / person_area, person_area / vest_area) if person_area > 0 else 0
                distance_score = 1.0 / (1.0 + abs(vy - vest_zone_center) / person_height)
                score = size_ratio * 0.6 + distance_score * 0.4
            
            if score > best_vest_score:
                best_vest_score = score
                has_vest = True
    
    return has_helmet, has_vest

class IntelligentPersonTracker:
    """Enhanced person tracker with velocity prediction."""
    def __init__(self, iou_threshold: float = 0.4, use_prediction: bool = True):
        self.next_id = 0
        self.tracks: Dict[int, Dict] = {}
        self.iou_threshold = iou_threshold
        self.use_prediction = use_prediction
    
    def update(self, person_detections: List[np.ndarray]) -> Dict[int, Dict]:
        """Update tracks with intelligent matching."""
        updated = {}
        used_track_ids = set()
        
        for det in person_detections:
            best_iou = 0
            best_id = None
            
            for pid, pdata in self.tracks.items():
                if pid in used_track_ids:
                    continue
                iou = calculate_iou(det, pdata["box"])
                if iou > best_iou:
                    best_iou = iou
                    best_id = pid
            
            if best_iou > self.iou_threshold and best_id is not None:
                updated[best_id] = {
                    "box": det,
                    "unsafe_frame_counter": self.tracks[best_id].get("unsafe_frame_counter", 0),
                    "status": self.tracks[best_id].get("status", "SAFE")
                }
                used_track_ids.add(best_id)
            else:
                updated[self.next_id] = {
                    "box": det,
                    "unsafe_frame_counter": 0,
                    "status": "SAFE"
                }
                self.next_id += 1
        
        self.tracks = updated
        return self.tracks
    
    def update_unsafe_counter(self, person_id: int, new_counter: int):
        """Update unsafe_frame_counter."""
        if person_id in self.tracks:
            self.tracks[person_id]["unsafe_frame_counter"] = new_counter

# ---------------- Monitor Runtime State ---------------- 
class MonitorState:
    """Global state for monitoring system."""
    def __init__(self):
        self.running = False
        self.start_time = None
        self.frame_id = 0
        self.fps = 0.0
        self.last_fps_tick = time.time()
        self.frames_in_tick = 0

        self.people: Dict[int, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.max_alerts = 100

        # Enhanced metrics
        self.quality_score = 1.0
        self.current_confidence = 0.3
        self.occlusion_count = 0
        self.ema_scores: Dict[int, float] = {}
        
        # Video capture
        self.video_capture = None
        self.current_frame = None
        self.frame_lock = None  # Will be created in async context when needed
        
        # YOLO Models
        self.person_model = None
        self.ppe_model = None
        self.device = 0  # Device for model inference (cuda/mps/cpu)
        
        # Intelligence components
        self.scene_quality = None
        self.adaptive_conf = None
        self.occlusion_detector = None
        self.ppe_memory = None
        self.ema_manager = None
        self.tracker = None
        self.tracker_wrapper = None

STATE = MonitorState()

# ---------------- WebSocket Manager ---------------- 
class WSManager:
    """WebSocket connection manager."""
    def __init__(self):
        self.clients: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)
        logger.info(f"WebSocket client connected. Total: {len(self.clients)}")

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)
            logger.info(f"WebSocket client disconnected. Total: {len(self.clients)}")

    async def broadcast(self, event: Dict[str, Any]):
        dead = []
        for ws in self.clients:
            try:
                await ws.send_json(event)
            except Exception as e:
                logger.debug(f"WebSocket send failed: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

WS = WSManager()

# ---------------- Alert Management ---------------- 
def push_alert(kind: str, title: str, details: str, meta: Dict[str, Any] = None):
    """Add alert to state."""
    alert = {
        "id": f"{int(time.time()*1000)}-{hash(title) % 10000}",
        "time": now_str(),
        "kind": kind,  # info/warn/danger
        "title": title,
        "details": details,
        "meta": meta or {}
    }
    STATE.alerts.insert(0, alert)
    STATE.alerts = STATE.alerts[:STATE.max_alerts]

# ---------------- Demo Mode Simulator ---------------- 
def random_box(w=1280, h=720) -> List[int]:
    """Generate random bounding box for demo."""
    x1 = random.randint(50, w-200)
    y1 = random.randint(50, h-300)
    x2 = x1 + random.randint(120, 220)
    y2 = y1 + random.randint(250, 420)
    return [x1, y1, x2, y2]

async def demo_loop():
    """Demo mode: generates realistic simulation data."""
    if not STATE.people:
        STATE.people = {
            1: {"box": random_box(), "helmet": True, "vest": False, "unsafe_counter": 0, "status": "CHECK"},
            2: {"box": random_box(), "helmet": True, "vest": True, "unsafe_counter": 0, "status": "SAFE"},
        }

    while STATE.running:
        STATE.frame_id += 1
        
        # FPS calculation
        STATE.frames_in_tick += 1
        t = time.time()
        if (t - STATE.last_fps_tick) >= 1.0:
            STATE.fps = STATE.frames_in_tick / (t - STATE.last_fps_tick)
            STATE.frames_in_tick = 0
            STATE.last_fps_tick = t

        # Animate boxes
        for p in STATE.people.values():
            x1, y1, x2, y2 = p["box"]
            dx = random.randint(-6, 6)
            dy = random.randint(-4, 4)
            p["box"] = [max(0, x1+dx), max(0, y1+dy), max(50, x2+dx), max(80, y2+dy)]

        # Person 1: vest flicker simulation
        if random.random() < 0.25:
            STATE.people[1]["vest"] = not STATE.people[1]["vest"]

        # Person 2: stable safe
        if random.random() < 0.08:
            STATE.people[2]["helmet"] = True
            STATE.people[2]["vest"] = True

        # Person 3: appear/disappear
        if 3 not in STATE.people and random.random() < 0.10:
            STATE.people[3] = {"box": random_box(), "helmet": False, "vest": True, "unsafe_counter": 0, "status": "CHECK"}
            push_alert("info", "New worker detected", "Worker #3 entered the scene.", {"person_id": 3})
        elif 3 in STATE.people and random.random() < 0.06:
            del STATE.people[3]
            push_alert("info", "Worker left", "Worker #3 left the scene.", {"person_id": 3})

        # Status decision
        safe_count = check_count = unsafe_count = 0
        for pid, p in STATE.people.items():
            status, new_counter = determine_status(
                p["helmet"], p["vest"], p["unsafe_counter"], config_state.unsafe_threshold
            )
            p["unsafe_counter"] = new_counter
            p["status"] = status

            if status == "SAFE":
                safe_count += 1
            elif status == "CHECK":
                check_count += 1
            else:
                unsafe_count += 1

        # Log to CSV
        timestamp = now_str()
        log_entries = []
        with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for pid, p in STATE.people.items():
                x1, y1, x2, y2 = p["box"]
                log_row = [
                    timestamp, config_state.camera_location, STATE.frame_id, pid,
                    x1, y1, x2, y2,
                    p["helmet"], p["vest"], p["status"], p["unsafe_counter"],
                    "1.000", False, "1.000"  # Demo values
                ]
                w.writerow(log_row)
                # Store log entry for WebSocket broadcast
                log_entries.append({
                    "timestamp": timestamp,
                    "frame_id": str(STATE.frame_id),
                    "person_id": str(pid),
                    "x1": str(x1),
                    "y1": str(y1),
                    "x2": str(x2),
                    "y2": str(y2),
                    "helmet": str(p["helmet"]),
                    "vest": str(p["vest"]),
                    "status": p["status"],
                    "unsafe_counter": str(p["unsafe_counter"]),
                    "ema_score": "1.000",
                    "occluded": "False",
                    "quality_score": "1.000"
                })
        
        # Broadcast log entries via WebSocket
        if log_entries:
            log_event = {
                "type": "logs",
                "entries": log_entries,
                "total": len(log_entries)
            }
            await WS.broadcast(log_event)

        # Alerts
        if unsafe_count > 0:
            ctx = {
                "unsafe_count": unsafe_count,
                "total_persons": len(STATE.people),
                "time": now_str(),
                "location": "Demo Site",
                "unsafe_threshold": config_state.unsafe_threshold
            }
            ai_text = generate_alert_caption_with_ai(ctx)
            msg = ai_text or generate_safety_alert_message(
                unsafe_count, len(STATE.people), ctx['time'], config_state.camera_location
            )

            sent = False
            if config_state.telegram_enabled:
                sent = telegram_api.send_text(msg)

            push_alert(
                "danger",
                "UNSAFE workers detected",
                f"{unsafe_count} worker(s) without full PPE.",
                {"unsafe_count": unsafe_count, "telegram_sent": sent}
            )

        # Broadcast event
        event = {
            "type": "tick",
            "time": now_str(),
            "frame_id": STATE.frame_id,
            "fps": round(STATE.fps, 1),
            "camera_location": config_state.camera_location,
            "counts": {
                "total": len(STATE.people),
                "safe": safe_count,
                "check": check_count,
                "unsafe": unsafe_count
            },
            "people": [
                {"id": pid, **p} for pid, p in STATE.people.items()
            ],
            "alerts": STATE.alerts[:20],
            "config": config_state.model_dump(),
            "enhanced_metrics": {
                "quality_score": STATE.quality_score,
                "confidence": STATE.current_confidence,
                "occlusion_count": STATE.occlusion_count
            }
        }
        await WS.broadcast(event)

        await asyncio.sleep(0.33)  # ~3 FPS demo

# ---------------- FastAPI Application ---------------- 
app = FastAPI(
    title=APP_NAME,
    description="Production-ready PPE Safety Monitoring System with AI-enhanced detection",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API Endpoints ---------------- 
@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "name": APP_NAME,
        "time": now_str(),
        "version": "2.0.0",
        "running": STATE.running
    }

@app.get("/api/config")
def get_config():
    """Get current configuration."""
    return config_state.model_dump()

@app.post("/api/config")
def set_config(new_cfg: AppConfig):
    """Update configuration."""
    global config_state
    config_state = new_cfg
    
    # Update Telegram notifier with new settings
    telegram_api.update_from_config()
    
    logger.info(f"Configuration updated: {new_cfg.model_dump()}")
    return {"ok": True, "config": config_state.model_dump()}

@app.get("/api/stats")
def get_stats():
    """Get current statistics."""
    people = STATE.people or {}
    counts = {
        "total": len(people),
        "safe": sum(1 for p in people.values() if p.get("status") == "SAFE"),
        "check": sum(1 for p in people.values() if p.get("status") == "CHECK"),
        "unsafe": sum(1 for p in people.values() if p.get("status") == "UNSAFE"),
    }
    total_status = counts["safe"] + counts["check"] + counts["unsafe"]
    safety_pct = (counts["safe"] / total_status * 100.0) if total_status > 0 else 0.0
    
    return {
        "running": STATE.running,
        "frame_id": STATE.frame_id,
        "fps": round(STATE.fps, 1),
        "counts": counts,
        "safety_percentage": round(safety_pct, 1),
        "uptime_seconds": int(time.time() - (STATE.start_time or time.time())) if STATE.running else 0,
        "enhanced_metrics": {
            "quality_score": STATE.quality_score,
            "confidence": STATE.current_confidence,
            "occlusion_count": STATE.occlusion_count
        }
    }

@app.get("/api/alerts")
def get_alerts(limit: int = 50):
    """Get alerts."""
    limit = max(1, min(limit, 200))
    return {"items": STATE.alerts[:limit]}

@app.get("/api/logs")
def get_logs(limit: int = 50, offset: int = 0):
    """Get logs from CSV."""
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    if not LOG_CSV.exists():
        return {"items": [], "total": 0}

    try:
        with open(LOG_CSV, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total = len(rows)
        sliced = rows[offset: offset + limit]
        return {"items": sliced[::-1], "total": total}  # newest first
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"items": [], "total": 0}

@app.get("/api/reports/safety_log.csv")
def download_log():
    """Download safety log CSV."""
    if not LOG_CSV.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    return FileResponse(str(LOG_CSV), filename="safety_log.csv", media_type="text/csv")

@app.get("/api/reports/safety_summary.csv")
def download_summary():
    """Download safety summary CSV."""
    if not SUMMARY_CSV.exists():
        raise HTTPException(status_code=404, detail="Summary file not found")
    return FileResponse(str(SUMMARY_CSV), filename="safety_summary.csv", media_type="text/csv")

@app.post("/api/alerts/test-telegram")
def test_telegram():
    """Test Telegram notification."""
    # Update telegram API with current config
    telegram_api.update_from_config()
    
    ctx = {"time": now_str(), "location": "Test Location", "unsafe_count": 1, "total_persons": 2}
    msg = generate_alert_caption_with_ai(ctx) or (
        f"✅ Test Message - PPE Safety Monitoring System\n"
        f"Location: {ctx['location']}\n"
        f"Time: {ctx['time']}\n"
        f"This is a test message to verify Telegram configuration."
    )
    
    sent = telegram_api.send_text(msg)
    push_alert("info", "Test Telegram", f"Telegram test {'sent' if sent else 'failed'}.", {"telegram_sent": sent})
    
    return {
        "ok": True, 
        "telegram_sent": sent, 
        "message_preview": msg,
        "enabled": telegram_api.enabled,
        "has_token": bool(telegram_api.token),
        "has_chat_id": bool(telegram_api.chat_id)
    }

@app.post("/api/monitor/start")
async def start_monitor():
    """Start monitoring."""
    global config_state
    
    if STATE.running:
        return {"ok": True, "running": True, "message": "Already running"}

    STATE.running = True
    STATE.start_time = time.time()
    STATE.frame_id = 0
    
    # Check if real mode is requested but models are missing
    if config_state.mode == "real":
        person_model_path = getattr(config_state, 'person_model_path', "yolov8n.pt")
        ppe_model_path = getattr(config_state, 'ppe_model_path', "best.pt")
        
        # Check in project root
        person_model_full = PROJECT_ROOT / person_model_path
        ppe_model_full = PROJECT_ROOT / ppe_model_path
        
        person_exists = person_model_full.exists()
        ppe_exists = ppe_model_full.exists()
        
        logger.info(f"Checking for models:")
        logger.info(f"  Person model: {person_model_full} - {'EXISTS' if person_exists else 'NOT FOUND'}")
        logger.info(f"  PPE model: {ppe_model_full} - {'EXISTS' if ppe_exists else 'NOT FOUND'}")
        
        if not person_exists or not ppe_exists:
            missing = []
            if not person_exists:
                missing.append(f"yolov8n.pt (expected at {person_model_full})")
            if not ppe_exists:
                missing.append(f"best.pt (expected at {ppe_model_full})")
            
            logger.warning(f"Real mode selected but model files missing: {', '.join(missing)}")
            logger.warning("Falling back to demo mode")
            
            # Auto-switch to demo mode
            config_state.mode = "demo"
            push_alert("warn", "Models Not Found", 
                      f"Model files not found. Switched to demo mode. Place models in: {PROJECT_ROOT}", 
                      {"missing_models": missing})
    
    push_alert("info", "Monitoring started", f"System started in {config_state.mode} mode.", {"mode": config_state.mode})

    if config_state.mode == "demo":
        asyncio.create_task(demo_loop())
        logger.info("Started in DEMO mode")
    else:
        # Start real video capture
        if CV2_AVAILABLE:
            try:
                video_source = config_state.video_source
                # Try to convert to int if it's a number
                try:
                    video_source = int(video_source)
                except ValueError:
                    pass  # Keep as string (file path or RTSP)
                
                STATE.video_capture = cv2.VideoCapture(video_source)
                if not STATE.video_capture.isOpened():
                    error_msg = f"Cannot open video source: {video_source}. Check camera/video file exists."
                    logger.error(error_msg)
                    push_alert("danger", "Camera Error", error_msg, {})
                    STATE.running = False
                    return {"ok": False, "running": False, "error": error_msg}
                
                # Initialize frame lock (must be created in async context)
                if STATE.frame_lock is None:
                    STATE.frame_lock = asyncio.Lock()
                
                # Start video capture loop
                asyncio.create_task(video_capture_loop())
                logger.info(f"Started in REAL mode - Video capture from: {video_source}")
            except Exception as e:
                logger.error(f"Failed to start video capture: {e}")
                push_alert("danger", "Video Error", f"Failed to start video: {str(e)}", {})
                STATE.running = False
                return {"ok": False, "running": False, "error": str(e)}
        else:
            logger.error("OpenCV not available")
            push_alert("warn", "OpenCV Not Available", "Install opencv-python for real video processing.", {})
            STATE.running = False
            return {"ok": False, "running": False, "error": "OpenCV not available"}
    
    logger.info(f"Monitoring started in {config_state.mode} mode")
    return {"ok": True, "running": True, "mode": config_state.mode}

@app.post("/api/monitor/stop")
def stop_monitor():
    """Stop monitoring."""
    if not STATE.running:
        return {"ok": True, "running": False, "message": "Already stopped"}
    
    STATE.running = False
    
    # Release video capture
    if STATE.video_capture is not None:
        STATE.video_capture.release()
        STATE.video_capture = None
        STATE.current_frame = None
        STATE.frame_lock = None  # Reset frame lock
    
    push_alert("info", "Monitoring stopped", "System stopped.", {})
    logger.info("Monitoring stopped")
    return {"ok": True, "running": False}

@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    """WebSocket endpoint for real-time events."""
    try:
        await WS.connect(ws)
        logger.info("WebSocket client connected")
        
        # Send initial snapshot
        try:
            await ws.send_json({
                "type": "hello",
                "time": now_str(),
                "config": config_state.model_dump(),
                "state": {
                    "running": STATE.running,
                    "frame_id": STATE.frame_id,
                    "fps": STATE.fps
                }
            })
        except Exception as e:
            logger.error(f"Error sending initial WebSocket message: {e}")
        
        # Keep alive and handle messages
        while True:
            try:
                # Wait for message or timeout
                try:
                    data = await asyncio.wait_for(ws.receive_text(), timeout=15.0)
                    # Handle incoming messages if needed
                    try:
                        msg = json.loads(data)
                        if msg.get("type") == "pong":
                            logger.debug("Received pong from client")
                    except:
                        pass
                except asyncio.TimeoutError:
                    # Send ping on timeout
                    await ws.send_json({"type": "ping", "time": now_str()})
                    
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected normally")
                break
            except Exception as e:
                logger.error(f"WebSocket error in loop: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during connection")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
    finally:
        WS.disconnect(ws)
        logger.info("WebSocket connection closed")

# ---------------- GPU Device Detection ---------------- 
def get_device():
    """Detect and return the best available device (GPU/CUDA/MPS/CPU)."""
    if not YOLO_AVAILABLE:
        return "cpu"
    
    try:
        # Use the CUDA_AVAILABLE flag set at module load time
        if CUDA_AVAILABLE:
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
            return "cuda"
        elif TORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("Apple Silicon GPU (MPS) detected")
            return "mps"
        else:
            logger.info("No GPU detected, using CPU")
            return "cpu"
    except Exception as e:
        logger.warning(f"Error detecting device: {e}, defaulting to CPU")
        return "cpu"

def load_models():
    """Load YOLO models for real mode."""
    if not YOLO_AVAILABLE:
        logger.warning("YOLO not available - cannot load models")
        return False
    
    try:
        # Detect device (GPU/CUDA/MPS/CPU)
        device = get_device()
        
        # Get model paths from config or use defaults
        person_model_path = getattr(config_state, 'person_model_path', "yolov8n.pt")
        ppe_model_path = getattr(config_state, 'ppe_model_path', "best.pt")
        
        # Resolve to full paths in project root
        person_model_full = PROJECT_ROOT / person_model_path
        ppe_model_full = PROJECT_ROOT / ppe_model_path
        
        logger.info(f"Loading person model from: {person_model_full}")
        logger.info(f"Loading PPE model from: {ppe_model_full}")
        
        # Load models with explicit device
        STATE.person_model = YOLO(str(person_model_full), task='detect')
        STATE.ppe_model = YOLO(str(ppe_model_full), task='detect')
        
        # Move models to device
        STATE.person_model.to(device)
        STATE.ppe_model.to(device)
        
        # Store device for inference
        STATE.device = device
        
        logger.info(f"Models loaded successfully - will use {device} for inference")
        if device == "cuda":
            try:
                import torch
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"GPU: {gpu_name}")
                logger.info(f"GPU Memory: {gpu_memory:.2f} GB")
            except Exception as e:
                logger.debug(f"Could not get GPU info: {e}")
        elif device == "mps":
            logger.info("Using Apple Silicon GPU (Metal Performance Shaders)")
        else:
            logger.info("Using CPU for inference")
        return True
    except Exception as e:
        logger.error(f"Failed to load models: {e}", exc_info=True)
        return False

def initialize_intelligence_components():
    """Initialize intelligence components based on config."""
    if config_state.scene_quality_enabled:
        STATE.scene_quality = SceneQualityAnalyzer()
    
    if config_state.adaptive_confidence_enabled:
        STATE.adaptive_conf = AdaptiveConfidenceManager(
            config_state.confidence,
            config_state.min_confidence,
            config_state.max_confidence
        )
    
    if config_state.occlusion_detection_enabled:
        STATE.occlusion_detector = OcclusionDetector(config_state.occlusion_threshold)
    
    if config_state.ppe_memory_enabled:
        STATE.ppe_memory = PPEMemoryManager(config_state.ppe_memory_frames)
    
    if config_state.use_ema_temporal:
        STATE.ema_manager = TemporalConsistencyEMA(
            config_state.ema_alpha,
            config_state.unsafe_threshold_ema
        )
    
    # Initialize tracker
    if config_state.use_bytetrack and YOLO_AVAILABLE:
        try:
            import lap
            logger.info("Using ByteTrack tracker")
            # ByteTrack will be used via YOLO's track method
            STATE.tracker = None
        except ImportError:
            logger.warning("ByteTrack unavailable, using custom tracker")
            STATE.tracker = IntelligentPersonTracker(0.4, True)
    else:
        STATE.tracker = IntelligentPersonTracker(0.4, True)

# ---------------- Video Capture Loop ---------------- 
async def video_capture_loop():
    """Capture video frames in real-time and process with models."""
    if not CV2_AVAILABLE or not STATE.video_capture:
        logger.error("video_capture_loop: CV2 not available or no video capture object")
        return
    
    # Load models if in real mode
    if config_state.mode == "real" and YOLO_AVAILABLE:
        logger.info("Loading YOLO models for real mode processing...")
        if not load_models():
            logger.error("Failed to load models - falling back to demo mode")
            push_alert("danger", "Model Loading Failed", "YOLO models could not be loaded. Check model files exist (yolov8n.pt, best.pt).", {})
            STATE.running = False
            return
        
        # Initialize intelligence components
        initialize_intelligence_components()
        logger.info("Intelligence components initialized")
    elif config_state.mode == "real" and not YOLO_AVAILABLE:
        logger.warning("Real mode requested but YOLO not available - no detection will occur")
        push_alert("warn", "YOLO Not Available", "Install ultralytics: pip install ultralytics", {})
    
    quality_check_counter = 0
    frame_error_count = 0
    last_error_time = 0
    
    while STATE.running and STATE.video_capture is not None:
        try:
            ret, frame = STATE.video_capture.read()
            if not ret:
                frame_error_count += 1
                if frame_error_count > 30:  # Error over 30 frames
                    logger.error(f"Failed to read {frame_error_count} consecutive frames from video source")
                    if time.time() - last_error_time > 5:  # Only alert every 5 seconds
                        push_alert("danger", "Frame Read Error", f"Cannot read frames from camera. Check camera connection or video file.", {})
                        last_error_time = time.time()
                await asyncio.sleep(0.1)
                continue
            else:
                frame_error_count = 0  # Reset on success
            
            STATE.frame_id += 1
            
            # Process frame with models if in real mode
            if config_state.mode == "real" and YOLO_AVAILABLE and STATE.person_model and STATE.ppe_model:
                # Initialize people dict if not exists
                if not STATE.people:
                    STATE.people = {}
                # Scene quality analysis
                if STATE.scene_quality and STATE.frame_id % config_state.quality_check_interval == 0:
                    quality_score, metrics = STATE.scene_quality.analyze_frame(frame)
                    STATE.quality_score = quality_score
                else:
                    quality_score = STATE.quality_score
                
                # Adaptive confidence
                if STATE.adaptive_conf:
                    STATE.current_confidence = STATE.adaptive_conf.update(
                        len(STATE.people), quality_score
                    )
                
                # Run detection on GPU (optimized for speed)
                try:
                    # Get device for inference
                    device = getattr(STATE, 'device', 0)
                    
                    # Person detection (optimized for GPU)
                    if config_state.use_bytetrack:
                        person_results = STATE.person_model.track(
                            frame, classes=[0], conf=STATE.current_confidence,
                            tracker=config_state.tracker_type, verbose=False, persist=True,
                            device=device
                        )
                    else:
                        person_results = STATE.person_model(
                            frame, classes=[0], conf=STATE.current_confidence, 
                            verbose=False, device=device
                        )
                    
                    # PPE detection (optimized for GPU)
                    ppe_results = STATE.ppe_model(
                        frame, conf=STATE.current_confidence, verbose=False, device=device
                    )
                    
                    # Debug logging (every 30 frames)
                    if STATE.frame_id % 30 == 0:
                        person_count = len(person_results[0].boxes) if person_results[0].boxes is not None else 0
                        ppe_count = len(ppe_results[0].boxes) if ppe_results[0].boxes is not None else 0
                        logger.debug(f"Frame {STATE.frame_id}: Detected {person_count} persons, {ppe_count} PPE items")
                        
                except Exception as e:
                    logger.error(f"Detection failed on frame {STATE.frame_id}: {e}", exc_info=True)
                    # Push alert only once per 10 seconds to avoid spam
                    if time.time() - last_error_time > 10:
                        error_msg = str(e)[:100]  # Truncate long errors
                        push_alert("warn", "Detection Error", f"Model inference failed: {error_msg}. Continuing with no detections.", {})
                        last_error_time = time.time()
                    # Continue processing even if detection fails - create empty results
                    class EmptyResults:
                        boxes = None
                    person_results = [EmptyResults()]
                    ppe_results = [EmptyResults()]
                
                # Extract PPE detections
                helmets = []
                vests = []
                try:
                    if ppe_results[0].boxes is not None and len(ppe_results[0].boxes) > 0:
                        for box in ppe_results[0].boxes:
                            cls = int(box.cls[0])
                            bbox = box.xyxy[0].cpu().numpy()
                            if cls == 0:  # Helmet
                                helmets.append(bbox)
                            elif cls == 1:  # Vest
                                vests.append(bbox)
                except Exception as e:
                    logger.debug(f"Error extracting PPE: {e}")
                    helmets = []
                    vests = []
                
                # Track persons
                tracks = {}
                try:
                    if config_state.use_bytetrack and person_results[0].boxes is not None and len(person_results[0].boxes) > 0:
                        # Use ByteTrack IDs
                        if hasattr(person_results[0].boxes, 'id') and person_results[0].boxes.id is not None:
                            track_ids = person_results[0].boxes.id.cpu().numpy().astype(int)
                            boxes = person_results[0].boxes.xyxy.cpu().numpy()
                            for track_id, box in zip(track_ids, boxes):
                                tracks[int(track_id)] = {
                                    "box": box,
                                    "unsafe_frame_counter": STATE.people.get(int(track_id), {}).get("unsafe_counter", 0),
                                    "status": "SAFE"
                                }
                        else:
                            # Fallback to custom tracker if no IDs
                            persons = []
                            for box in person_results[0].boxes:
                                persons.append(box.xyxy[0].cpu().numpy())
                            tracks = STATE.tracker.update(persons) if STATE.tracker else {}
                    else:
                        # Use custom tracker
                        persons = []
                        if person_results[0].boxes is not None and len(person_results[0].boxes) > 0:
                            for box in person_results[0].boxes:
                                persons.append(box.xyxy[0].cpu().numpy())
                        tracks = STATE.tracker.update(persons) if STATE.tracker else {}
                except Exception as e:
                    logger.debug(f"Error tracking persons: {e}")
                    tracks = {}
                
                # Get all person boxes for occlusion detection
                all_person_boxes = [pdata["box"] for pdata in tracks.values()]
                
                # PPE Memory update
                if STATE.ppe_memory:
                    STATE.ppe_memory.increment_age()
                
                # Process each person
                STATE.people = {}
                safe_count = check_count = unsafe_count = 0
                occlusion_count = 0
                
                for pid, pdata in tracks.items():
                    person_box = pdata["box"]
                    
                    # Associate PPE
                    has_helmet, has_vest = associate_ppe_enhanced(
                        person_box, helmets, vests, config_state.use_body_proportions
                    )
                    
                    # Check occlusion
                    is_occluded = False
                    if STATE.occlusion_detector:
                        is_occluded = STATE.occlusion_detector.is_occluded(person_box, all_person_boxes)
                        if is_occluded:
                            occlusion_count += 1
                            # Use remembered PPE if occluded
                            if STATE.ppe_memory:
                                mem_helmet, mem_vest = STATE.ppe_memory.get_remembered_ppe(pid)
                                if mem_helmet is not None:
                                    has_helmet = mem_helmet
                                if mem_vest is not None:
                                    has_vest = mem_vest
                    
                    # Update PPE memory
                    if STATE.ppe_memory:
                        STATE.ppe_memory.update(pid, has_helmet, has_vest)
                    
                    # Determine status
                    if STATE.ema_manager:
                        status = STATE.ema_manager.update_score(pid, has_helmet, has_vest)
                        ema_score = STATE.ema_manager.get_score(pid)
                        unsafe_counter = 0
                    else:
                        unsafe_counter = pdata.get("unsafe_frame_counter", 0)
                        status, unsafe_counter = determine_status(
                            has_helmet, has_vest, unsafe_counter, config_state.unsafe_threshold
                        )
                        if STATE.tracker:
                            STATE.tracker.update_unsafe_counter(pid, unsafe_counter)
                        ema_score = 1.0 if status == "SAFE" else 0.0
                    
                    STATE.people[pid] = {
                        "box": person_box.tolist() if isinstance(person_box, np.ndarray) else person_box,
                        "helmet": has_helmet,
                        "vest": has_vest,
                        "status": status,
                        "unsafe_counter": unsafe_counter
                    }
                    
                    STATE.ema_scores[pid] = ema_score
                    
                    if status == "SAFE":
                        safe_count += 1
                    elif status == "CHECK":
                        check_count += 1
                    else:
                        unsafe_count += 1
                
                STATE.occlusion_count = occlusion_count
                
                # Log to CSV
                timestamp = now_str()
                log_entries = []
                with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for pid, pdata in STATE.people.items():
                        box = pdata["box"]
                        x1, y1, x2, y2 = box[:4] if len(box) >= 4 else [0, 0, 0, 0]
                        occluded = STATE.occlusion_detector.is_occluded(np.array(box), all_person_boxes) if STATE.occlusion_detector else False
                        ema_score = STATE.ema_scores.get(pid, 1.0)
                        log_row = [
                            timestamp, config_state.camera_location, STATE.frame_id, pid,
                            int(x1), int(y1), int(x2), int(y2),
                            pdata["helmet"], pdata["vest"], pdata["status"], pdata["unsafe_counter"],
                            f"{ema_score:.3f}",
                            occluded,
                            f"{quality_score:.3f}"
                        ]
                        w.writerow(log_row)
                        # Store log entry for WebSocket broadcast
                        log_entries.append({
                            "timestamp": timestamp,
                            "frame_id": str(STATE.frame_id),
                            "person_id": str(pid),
                            "x1": str(int(x1)),
                            "y1": str(int(y1)),
                            "x2": str(int(x2)),
                            "y2": str(int(y2)),
                            "helmet": str(pdata["helmet"]),
                            "vest": str(pdata["vest"]),
                            "status": pdata["status"],
                            "unsafe_counter": str(pdata["unsafe_counter"]),
                            "ema_score": f"{ema_score:.3f}",
                            "occluded": str(occluded),
                            "quality_score": f"{quality_score:.3f}"
                        })
                
                # Broadcast log entries via WebSocket
                if log_entries:
                    log_event = {
                        "type": "logs",
                        "entries": log_entries,
                        "total": len(log_entries)
                    }
                    await WS.broadcast(log_event)
                
                # Alerts with frame (like ppe_enhanced.py)
                if unsafe_count > 0:
                    # Draw boxes on frame for Telegram alert
                    alert_frame = frame.copy()
                    if CV2_AVAILABLE:
                        alert_frame = draw_boxes_on_frame(alert_frame, STATE.people)
                    
                    sent = False
                    if config_state.telegram_enabled:
                        # Send frame with unsafe detections
                        sent = telegram_api.send_alert(
                            alert_frame, 
                            unsafe_count, 
                            len(STATE.people),
                            config_state.camera_location
                        )
                    
                    push_alert(
                        "danger",
                        "UNSAFE workers detected",
                        f"{unsafe_count} worker(s) without full PPE.",
                        {"unsafe_count": unsafe_count, "telegram_sent": sent}
                    )
                
                # Broadcast event (always broadcast, even with no detections)
                event = {
                    "type": "tick",
                    "time": now_str(),
                    "frame_id": STATE.frame_id,
                    "fps": round(STATE.fps, 1),
                    "camera_location": config_state.camera_location,
                    "counts": {
                        "total": len(STATE.people),
                        "safe": safe_count,
                        "check": check_count,
                        "unsafe": unsafe_count
                    },
                    "people": [
                        {"id": pid, **p} for pid, p in STATE.people.items()
                    ],
                    "alerts": STATE.alerts[:20],
                    "config": config_state.model_dump(),
                    "enhanced_metrics": {
                        "quality_score": STATE.quality_score,
                        "confidence": STATE.current_confidence,
                        "occlusion_count": STATE.occlusion_count
                    }
                }
                await WS.broadcast(event)
            else:
                # If not in real mode or models not loaded, still broadcast empty state
                if STATE.frame_id % 10 == 0:  # Broadcast every 10 frames to reduce load
                    event = {
                        "type": "tick",
                        "time": now_str(),
                        "frame_id": STATE.frame_id,
                        "fps": round(STATE.fps, 1),
                        "camera_location": config_state.camera_location,
                        "counts": {
                            "total": len(STATE.people) if STATE.people else 0,
                            "safe": 0,
                            "check": 0,
                            "unsafe": 0
                        },
                        "people": [],
                        "alerts": STATE.alerts[:20],
                        "config": config_state.model_dump(),
                        "enhanced_metrics": {
                            "quality_score": STATE.quality_score,
                            "confidence": STATE.current_confidence,
                            "occlusion_count": 0
                        }
                    }
                    await WS.broadcast(event)
            
            # Store current frame
            if STATE.frame_lock:
                async with STATE.frame_lock:
                    STATE.current_frame = frame.copy()
            else:
                STATE.current_frame = frame.copy()
            
            # Update FPS
            STATE.frames_in_tick += 1
            t = time.time()
            if (t - STATE.last_fps_tick) >= 1.0:
                STATE.fps = STATE.frames_in_tick / (t - STATE.last_fps_tick)
                STATE.frames_in_tick = 0
                STATE.last_fps_tick = t
            
            # Optimized sleep for faster FPS (reduce delay for GPU inference)
            await asyncio.sleep(0.016)  # ~60 FPS potential (if GPU can handle it)
            
        except Exception as e:
            logger.error(f"Error in video capture loop: {e}")
            await asyncio.sleep(0.1)
    
    logger.info("Video capture loop stopped")

# ---------------- Video Stream Endpoint ---------------- 
@app.get("/api/video/stream")
async def video_stream():
    """Stream video frames as MJPEG."""
    if not CV2_AVAILABLE:
        raise HTTPException(status_code=503, detail="OpenCV not available")
    
    async def generate_frames():
        while STATE.running:
            try:
                # Get current frame
                frame = None
                if STATE.frame_lock:
                    async with STATE.frame_lock:
                        frame = STATE.current_frame
                else:
                    frame = STATE.current_frame
                
                if frame is None:
                    # Send black frame if no video
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "No video source", (50, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Draw bounding boxes on frame
                frame_with_boxes = draw_boxes_on_frame(frame.copy(), STATE.people)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                await asyncio.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error generating video frame: {e}")
                await asyncio.sleep(0.1)
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

def draw_boxes_on_frame(frame: "np.ndarray", people: Dict[int, Dict[str, Any]]) -> "np.ndarray":
    """Draw bounding boxes and labels on frame."""
    if not CV2_AVAILABLE:
        return frame
    
    for pid, pdata in people.items():
        box = pdata.get("box", [0, 0, 0, 0])
        status = pdata.get("status", "SAFE")
        helmet = pdata.get("helmet", False)
        vest = pdata.get("vest", False)
        
        if not box or len(box) < 4:
            continue
        
        x1, y1, x2, y2 = map(int, box)
        
        # Choose color based on status
        if status == "SAFE":
            color = (0, 255, 0)  # Green
        elif status == "CHECK":
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 0, 255)  # Red
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"ID {pid} {status}"
        if not helmet:
            label += " [No Helmet]"
        if not vest:
            label += " [No Vest]"
        
        # Label background
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            frame,
            (x1, y1 - text_height - 10),
            (x1 + text_width + 4, y1),
            color,
            -1
        )
        
        # Label text
        cv2.putText(
            frame,
            label,
            (x1 + 2, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
    
    return frame

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

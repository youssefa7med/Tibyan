"""
Enhanced PPE Safety Monitoring System - Production Version with Intelligence Upgrades
Follows all AI Rules strictly from AI Rules.txt

NEW INTELLIGENCE FEATURES:
- Adaptive Confidence Thresholding (auto-adjusts based on scene)
- Enhanced Temporal Consistency with EMA (smoother decisions)
- Occlusion Detection & Handling (smart handling of overlapping persons)
- Scene-Aware Quality Analysis (adapts to lighting/blur)
- Enhanced Spatial Association with Body Proportions
- Multi-frame PPE Memory (remembers last seen PPE)

Pipeline: Detection → Tracking → PPE Association → Temporal Decision → Visualization → CSV Logging → Telegram Alerts
"""

import cv2
import numpy as np
import csv
import time
import requests
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional, Union
import os
import logging
from collections import deque

# ================== LOGGING SETUP ==================
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================
class Config:
    # ========== MAIN SETTINGS - CHANGE THESE TWO VARIABLES ==========
    
    # 1. VIDEO SOURCE (Camera, Video File, or RTSP)
    VIDEO_SOURCE: Union[int, str] = 1
    
    # 2. BASE CONFIDENCE THRESHOLD (Will be adapted automatically)
    CONFIDENCE = 0.3  # Base confidence (system will adapt this)
    
    # ========== INTELLIGENCE SETTINGS ==========
    
    # Adaptive Confidence
    ADAPTIVE_CONFIDENCE_ENABLED = True
    MIN_CONFIDENCE = 0.2  # Minimum confidence threshold
    MAX_CONFIDENCE = 0.5  # Maximum confidence threshold
    
    # Enhanced Temporal Consistency
    USE_EMA_TEMPORAL = True  # Use Exponential Moving Average
    EMA_ALPHA = 0.3  # Smoothing factor (0.1=slow, 0.5=fast)
    UNSAFE_THRESHOLD_EMA = 0.7  # Threshold for EMA score
    
    # Occlusion Handling
    OCCLUSION_DETECTION_ENABLED = True
    OCCLUSION_THRESHOLD = 0.3  # 30% overlap threshold
    
    # Scene Quality Analysis
    SCENE_QUALITY_ENABLED = True
    QUALITY_CHECK_INTERVAL = 30  # Check quality every N frames
    
    # PPE Memory (remembers last seen PPE for occluded persons)
    PPE_MEMORY_ENABLED = True
    PPE_MEMORY_FRAMES = 15  # Remember PPE for N frames
    
    # Enhanced Body Proportions
    USE_BODY_PROPORTIONS = True
    
    # ========== ADVANCED SETTINGS ==========
    
    # Model Paths
    PERSON_MODEL_PATH = "yolov8n.pt"
    PPE_MODEL_PATH = "best.pt"
    
    # Tracking
    USE_BYTETRACK = True
    TRACKER_TYPE = "bytetrack.yaml"
    
    # Anti-Flickering (Legacy - works alongside EMA)
    ANTI_FLICKER_ENABLED = True
    STATUS_HISTORY_SIZE = 5
    STATUS_CHANGE_THRESHOLD = 3
    
    # Safety Decision (Legacy threshold for non-EMA mode)
    UNSAFE_THRESHOLD = 3
    
    # CSV Logging
    CSV_FILE = "safety_log.csv"
    SUMMARY_CSV_FILE = "safety_summary.csv"
    SUMMARY_INTERVAL_SECONDS = 30
    
    # Telegram Notifications
    TELEGRAM_ENABLED = True
    TELEGRAM_TOKEN = "8746993307:AAEGiOBdYCVv3ETi4PikDt6iuCntN6LdE6A"
    TELEGRAM_CHAT_ID = "6730574204"
    TELEGRAM_COOLDOWN_SECONDS = 30
    
    # Performance
    FRAME_RESIZE = None
    FRAME_SKIP = 0
    
    # Visualization
    SHOW_VIDEO = True
    WINDOW_NAME = "Enhanced PPE Safety Monitor - AI Powered"
    SHOW_FPS = True
    SHOW_STATS = True
    SHOW_ZONES = False
    SHOW_DEBUG_INFO = True
    SHOW_QUALITY_INFO = True


# ================== UTILITY FUNCTIONS ==================
def calculate_iou(box1: np.ndarray, box2: np.ndarray) -> float:
    """Calculate Intersection over Union between two boxes."""
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


def get_box_center(box: np.ndarray) -> Tuple[float, float]:
    """Get center point (x, y) of bounding box."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def get_box_area(box: np.ndarray) -> float:
    """Get area of bounding box."""
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)


def normalize_video_source(source: Union[int, str]) -> Union[int, str]:
    """Normalize and validate video source."""
    if isinstance(source, int):
        return source
    elif isinstance(source, str):
        source_lower = source.lower()
        if source_lower.startswith(('rtsp://', 'http://', 'https://')):
            return source
        elif os.path.isfile(source) or source.endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            return source
        else:
            return source
    else:
        raise ValueError(f"Invalid VIDEO_SOURCE type: {type(source)}")


# ================== SCENE QUALITY ANALYZER ==================
class SceneQualityAnalyzer:
    """
    Analyzes frame quality and adjusts detection parameters.
    NEW INTELLIGENCE: Adapts to lighting, blur, and scene conditions.
    """
    
    def __init__(self):
        self.quality_history = deque(maxlen=10)
        self.last_quality_score = 1.0
    
    def analyze_frame(self, frame: np.ndarray) -> Tuple[float, Dict]:
        """Analyze frame quality and return score + metrics."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Brightness analysis
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127
        
        # Contrast analysis
        contrast = np.std(gray)
        contrast_score = min(contrast / 64, 1.0)
        
        # Sharpness analysis (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        sharpness_score = min(sharpness / 500, 1.0)
        
        # Overall quality score
        quality_score = (brightness_score * 0.3 + 
                        contrast_score * 0.3 + 
                        sharpness_score * 0.4)
        
        self.quality_history.append(quality_score)
        self.last_quality_score = np.mean(self.quality_history)
        
        metrics = {
            'brightness': brightness,
            'contrast': contrast,
            'sharpness': sharpness,
            'quality_score': quality_score,
            'avg_quality': self.last_quality_score
        }
        
        return self.last_quality_score, metrics
    
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


# ================== ADAPTIVE CONFIDENCE MANAGER ==================
class AdaptiveConfidenceManager:
    """
    NEW INTELLIGENCE: Dynamically adjusts confidence based on scene conditions.
    Increases confidence in good conditions, decreases in poor conditions.
    """
    
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
        
        avg_detections = np.mean(self.detection_history)
        
        # Base adjustment from detection count
        if avg_detections < 2:
            conf_adjustment = -0.05  # Lower confidence if too few detections
        elif avg_detections > 10:
            conf_adjustment = +0.05  # Raise confidence if too many detections
        else:
            conf_adjustment = 0
        
        # Quality-based adjustment
        quality_adjustment = (quality_score - 0.7) * 0.1
        
        # Combine adjustments
        new_conf = self.base_conf + conf_adjustment + quality_adjustment
        new_conf = max(self.min_conf, min(self.max_conf, new_conf))
        
        # Smooth transition
        self.current_conf = 0.8 * self.current_conf + 0.2 * new_conf
        
        return self.current_conf


# ================== OCCLUSION DETECTOR ==================
class OcclusionDetector:
    """
    NEW INTELLIGENCE: Detects when persons are occluded by others.
    Prevents false UNSAFE status due to hidden PPE.
    """
    
    def __init__(self, threshold=0.3):
        self.threshold = threshold
    
    def detect_occlusion(self, person_box: np.ndarray, 
                        all_person_boxes: List[np.ndarray]) -> float:
        """Calculate occlusion ratio for a person."""
        px1, py1, px2, py2 = person_box
        person_area = (px2 - px1) * (py2 - py1)
        
        if person_area <= 0:
            return 0.0
        
        max_occlusion = 0.0
        
        for other_box in all_person_boxes:
            if np.array_equal(other_box, person_box):
                continue
            
            # Calculate overlap
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
    
    def is_occluded(self, person_box: np.ndarray, 
                   all_person_boxes: List[np.ndarray]) -> bool:
        """Check if person is significantly occluded."""
        return self.detect_occlusion(person_box, all_person_boxes) > self.threshold


# ================== PPE MEMORY MANAGER ==================
class PPEMemoryManager:
    """
    NEW INTELLIGENCE: Remembers last seen PPE for each person.
    Helps maintain PPE status during brief occlusions or detection failures.
    """
    
    def __init__(self, memory_frames=15):
        self.memory_frames = memory_frames
        self.ppe_memory = {}  # person_id -> {helmet: bool, vest: bool, frames_ago: int}
    
    def update(self, person_id: int, has_helmet: bool, has_vest: bool):
        """Update PPE memory for a person."""
        self.ppe_memory[person_id] = {
            'helmet': has_helmet,
            'vest': has_vest,
            'frames_ago': 0
        }
    
    def get_remembered_ppe(self, person_id: int) -> Tuple[Optional[bool], Optional[bool]]:
        """Get remembered PPE status if within memory window."""
        if person_id not in self.ppe_memory:
            return None, None
        
        memory = self.ppe_memory[person_id]
        if memory['frames_ago'] > self.memory_frames:
            return None, None
        
        return memory['helmet'], memory['vest']
    
    def increment_age(self):
        """Increment age of all memories (call once per frame)."""
        for person_id in list(self.ppe_memory.keys()):
            self.ppe_memory[person_id]['frames_ago'] += 1
            
            # Remove old memories
            if self.ppe_memory[person_id]['frames_ago'] > self.memory_frames * 2:
                del self.ppe_memory[person_id]


# ================== TEMPORAL CONSISTENCY WITH EMA ==================
class TemporalConsistencyEMA:
    """
    NEW INTELLIGENCE: Uses Exponential Moving Average for smoother status decisions.
    Better than simple frame counting - considers all history with decay.
    """
    
    def __init__(self, alpha=0.3, unsafe_threshold=0.7):
        self.alpha = alpha
        self.unsafe_threshold = unsafe_threshold
        self.safety_scores = {}  # person_id -> safety_score (0=unsafe, 1=safe)
    
    def update_score(self, person_id: int, has_helmet: bool, has_vest: bool) -> str:
        """Update safety score with EMA and return status."""
        # Current frame score (1.0 = safe, 0.0 = unsafe)
        current_score = 1.0 if (has_helmet and has_vest) else 0.0
        
        if person_id not in self.safety_scores:
            self.safety_scores[person_id] = current_score
        else:
            # EMA formula: new = alpha * current + (1-alpha) * old
            self.safety_scores[person_id] = (
                self.alpha * current_score + 
                (1 - self.alpha) * self.safety_scores[person_id]
            )
        
        score = self.safety_scores[person_id]
        
        # Status based on smoothed score
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


# ================== ENHANCED PPE ASSOCIATION WITH BODY PROPORTIONS ==================
def associate_ppe_enhanced(person_box: np.ndarray, helmets: List[np.ndarray],
                          vests: List[np.ndarray], use_proportions: bool = True,
                          show_zones: bool = False) -> Tuple[bool, bool, Optional[Dict]]:
    """
    ENHANCED: PPE association using spatial zones + body proportions.
    More intelligent matching based on expected human body ratios.
    """
    px1, py1, px2, py2 = person_box
    person_height = py2 - py1
    person_width = px2 - px1
    
    if person_height <= 0:
        return False, False, None
    
    person_area = person_height * person_width
    
    # Expected proportions based on anthropometry
    expected_helmet_height = person_height * 0.125  # ~12.5% of body height
    expected_vest_width = person_width * 0.7       # ~70% of shoulder width
    
    # Define zones
    helmet_zone_top = py1 - person_height * 0.05
    helmet_zone_bottom = py1 + person_height * 0.40
    helmet_zone_center = py1 + person_height * 0.12
    
    vest_zone_top = py1 + person_height * 0.30
    vest_zone_bottom = py1 + person_height * 0.80
    vest_zone_center = py1 + person_height * 0.50
    
    has_helmet = False
    has_vest = False
    best_helmet_match = None
    best_vest_match = None
    best_helmet_score = 0
    best_vest_score = 0
    
    # Enhanced helmet matching with proportions
    for h in helmets:
        hx, hy = get_box_center(h)
        h_height = h[3] - h[1]
        h_width = h[2] - h[0]
        helmet_area = h_height * h_width
        
        # Spatial constraint
        in_width = px1 - person_width * 0.1 <= hx <= px2 + person_width * 0.1
        in_zone = helmet_zone_top <= hy <= helmet_zone_bottom
        
        if in_width and in_zone:
            score = 0
            
            if use_proportions:
                # Size proportion score
                size_diff = abs(h_height - expected_helmet_height) / expected_helmet_height
                size_score = max(0, 1.0 - size_diff)
                
                # Position score (distance from expected center)
                pos_diff = abs(hy - helmet_zone_center) / person_height
                pos_score = max(0, 1.0 - pos_diff * 2)
                
                # Area ratio score
                area_ratio = helmet_area / person_area if person_area > 0 else 0
                area_score = 1.0 if 0.05 <= area_ratio <= 0.20 else 0.5
                
                score = size_score * 0.35 + pos_score * 0.40 + area_score * 0.25
            else:
                # Simple scoring (original method)
                size_ratio = min(helmet_area / person_area, person_area / helmet_area) if person_area > 0 else 0
                distance_score = 1.0 / (1.0 + abs(hy - helmet_zone_center) / person_height)
                score = size_ratio * 0.6 + distance_score * 0.4
            
            if score > best_helmet_score:
                best_helmet_score = score
                best_helmet_match = h
                has_helmet = True
    
    # Enhanced vest matching with proportions
    for v in vests:
        vx, vy = get_box_center(v)
        v_height = v[3] - v[1]
        v_width = v[2] - v[0]
        vest_area = v_height * v_width
        
        # Spatial constraint
        in_width = px1 - person_width * 0.1 <= vx <= px2 + person_width * 0.1
        in_zone = vest_zone_top <= vy <= vest_zone_bottom
        
        if in_width and in_zone:
            score = 0
            
            if use_proportions:
                # Width proportion score
                width_diff = abs(v_width - expected_vest_width) / expected_vest_width
                width_score = max(0, 1.0 - width_diff)
                
                # Position score
                pos_diff = abs(vy - vest_zone_center) / person_height
                pos_score = max(0, 1.0 - pos_diff * 2)
                
                # Area ratio score
                area_ratio = vest_area / person_area if person_area > 0 else 0
                area_score = 1.0 if 0.15 <= area_ratio <= 0.50 else 0.5
                
                score = width_score * 0.35 + pos_score * 0.40 + area_score * 0.25
            else:
                # Simple scoring
                size_ratio = min(vest_area / person_area, person_area / vest_area) if person_area > 0 else 0
                distance_score = 1.0 / (1.0 + abs(vy - vest_zone_center) / person_height)
                score = size_ratio * 0.6 + distance_score * 0.4
            
            if score > best_vest_score:
                best_vest_score = score
                best_vest_match = v
                has_vest = True
    
    # Return match info
    match_info = {
        "helmet_zone": (helmet_zone_top, helmet_zone_bottom),
        "vest_zone": (vest_zone_top, vest_zone_bottom),
        "best_helmet": best_helmet_match,
        "best_vest": best_vest_match,
        "helmet_score": best_helmet_score,
        "vest_score": best_vest_score
    } if show_zones else None
    
    return has_helmet, has_vest, match_info


# ================== LEGACY: ANTI-FLICKERING STATUS MANAGER ==================
class AntiFlickerStatusManager:
    """Legacy anti-flickering (works alongside EMA)."""
    
    def __init__(self, history_size: int = 5, change_threshold: int = 3):
        self.history_size = history_size
        self.change_threshold = change_threshold
        self.status_history: Dict[int, List[str]] = {}
    
    def get_stable_status(self, person_id: int, new_status: str) -> str:
        """Get stable status after checking history."""
        if person_id not in self.status_history:
            self.status_history[person_id] = []
        
        self.status_history[person_id].append(new_status)
        
        if len(self.status_history[person_id]) > self.history_size:
            self.status_history[person_id] = self.status_history[person_id][-self.history_size:]
        
        history = self.status_history[person_id]
        
        if new_status == "UNSAFE":
            recent_unsafe = sum(1 for s in history[-self.change_threshold:] if s == "UNSAFE")
            if recent_unsafe >= self.change_threshold:
                return "UNSAFE"
        
        if len(history) >= self.change_threshold:
            recent_statuses = history[-self.change_threshold:]
            if len(set(recent_statuses)) == 1:
                return recent_statuses[0]
            else:
                return max(set(recent_statuses), key=recent_statuses.count)
        
        if len(history) > 0:
            return max(set(history), key=history.count)
        
        return new_status
    
    def reset(self, person_id: int):
        """Reset history for a person."""
        if person_id in self.status_history:
            del self.status_history[person_id]


# ================== INTELLIGENT PERSON TRACKER ==================
class IntelligentPersonTracker:
    """Enhanced person tracker with velocity prediction."""
    
    def __init__(self, iou_threshold: float = 0.4, use_prediction: bool = True):
        self.next_id = 0
        self.tracks: Dict[int, Dict] = {}
        self.iou_threshold = iou_threshold
        self.use_prediction = use_prediction
    
    def _predict_position(self, old_box: np.ndarray, velocity: Optional[np.ndarray]) -> np.ndarray:
        """Predict next position based on velocity."""
        if not self.use_prediction or velocity is None:
            return old_box
        
        predicted = old_box.copy()
        predicted[:2] += velocity[:2]
        predicted[2:] += velocity[2:]
        return predicted
    
    def _calculate_velocity(self, old_box: np.ndarray, new_box: np.ndarray) -> np.ndarray:
        """Calculate velocity vector."""
        return new_box - old_box
    
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
                
                if self.use_prediction and "velocity" in pdata and pdata["velocity"] is not None:
                    predicted_box = self._predict_position(pdata["box"], pdata["velocity"])
                    iou = calculate_iou(det, predicted_box)
                else:
                    iou = calculate_iou(det, pdata["box"])
                
                if iou > best_iou:
                    best_iou = iou
                    best_id = pid
            
            if best_iou > self.iou_threshold and best_id is not None:
                old_box = self.tracks[best_id]["box"]
                velocity = self._calculate_velocity(old_box, det) if self.use_prediction else None
                
                updated[best_id] = {
                    "box": det,
                    "unsafe_frame_counter": self.tracks[best_id]["unsafe_frame_counter"],
                    "velocity": velocity,
                    "history": self.tracks[best_id].get("history", []) + [det.copy()]
                }
                if len(updated[best_id]["history"]) > 5:
                    updated[best_id]["history"] = updated[best_id]["history"][-5:]
                
                used_track_ids.add(best_id)
            else:
                updated[self.next_id] = {
                    "box": det,
                    "unsafe_frame_counter": 0,
                    "velocity": None,
                    "history": [det.copy()]
                }
                self.next_id += 1
        
        self.tracks = updated
        return self.tracks
    
    def update_unsafe_counter(self, person_id: int, new_counter: int):
        """Update unsafe_frame_counter."""
        if person_id in self.tracks:
            self.tracks[person_id]["unsafe_frame_counter"] = new_counter


# ================== BYTETRACK WRAPPER ==================
class ByteTrackWrapper:
    """Wrapper for YOLO ByteTrack tracker."""
    
    def __init__(self, model, tracker_type: str = "bytetrack.yaml"):
        self.model = model
        self.tracker_type = tracker_type
        self.track_data: Dict[int, Dict] = {}
        self.id_mapping: Dict[int, int] = {}
        self.next_person_id = 0
    
    def update(self, results) -> Dict[int, Dict]:
        """Update tracks from YOLO tracking results."""
        updated = {}
        
        if results.boxes is not None and len(results.boxes) > 0:
            if hasattr(results.boxes, 'id') and results.boxes.id is not None:
                track_ids = results.boxes.id.cpu().numpy().astype(int)
                boxes = results.boxes.xyxy.cpu().numpy()
                
                for track_id, box in zip(track_ids, boxes):
                    if track_id not in self.id_mapping:
                        self.id_mapping[track_id] = self.next_person_id
                        self.track_data[self.next_person_id] = {
                            "unsafe_frame_counter": 0
                        }
                        self.next_person_id += 1
                    
                    person_id = self.id_mapping[track_id]
                    
                    if person_id not in self.track_data:
                        self.track_data[person_id] = {
                            "unsafe_frame_counter": 0
                        }
                    
                    updated[person_id] = {
                        "box": box,
                        "unsafe_frame_counter": self.track_data[person_id]["unsafe_frame_counter"]
                    }
        
        self.track_data = {pid: {"unsafe_frame_counter": pdata["unsafe_frame_counter"]} 
                          for pid, pdata in updated.items()}
        
        return updated
    
    def update_unsafe_counter(self, person_id: int, new_counter: int):
        """Update unsafe_frame_counter."""
        if person_id in self.track_data:
            self.track_data[person_id]["unsafe_frame_counter"] = new_counter


# ================== SAFETY DECISION (LEGACY) ==================
def determine_status(has_helmet: bool, has_vest: bool, 
                    unsafe_frame_counter: int, threshold: int = 3) -> Tuple[str, int]:
    """Legacy status determination (for non-EMA mode)."""
    if has_helmet and has_vest:
        return "SAFE", 0
    else:
        new_counter = unsafe_frame_counter + 1
        if new_counter >= threshold:
            return "UNSAFE", new_counter
        else:
            return "CHECK", new_counter


# ================== TELEGRAM NOTIFICATIONS ==================
class TelegramNotifier:
    """Handles Telegram alert notifications with cooldown."""
    
    def __init__(self, token: str, chat_id: str, cooldown_seconds: int = 30):
        self.token = token
        self.chat_id = chat_id
        self.cooldown_seconds = cooldown_seconds
        self.last_sent_time = 0
    
    def send_alert(self, frame: np.ndarray, unsafe_count: int, 
                   person_count: int, location: str = "Construction Site") -> bool:
        """Send safety alert to Telegram."""
        current_time = time.time()
        
        if current_time - self.last_sent_time < self.cooldown_seconds:
            return False
        
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        files = {'photo': buffer.tobytes()}
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caption_text = (
            f"⚠️ *SAFETY ALERT!* ⚠️\n"
            f"🚨 Unsafe Workers: {unsafe_count}\n"
            f"👷 Total Persons: {person_count}\n"
            f"📍 Location: {location}\n"
            f"⏱️ Time: {now}\n"
            f"⚠️ Missing PPE detected!"
        )
        
        try:
            response = requests.post(
                url,
                data={"chat_id": self.chat_id, "caption": caption_text, "parse_mode": "Markdown"},
                files=files,
                timeout=10
            )
            if response.status_code == 200:
                self.last_sent_time = current_time
                logger.info("Telegram alert sent!")
                return True
            else:
                logger.warning(f"Telegram error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Telegram failed: {e}")
            return False


# ================== CSV LOGGER ==================
class CSVLogger:
    """Handles CSV logging with enhanced intelligence features."""
    
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with headers."""
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "frame_id", "person_id",
                "x1", "y1", "x2", "y2",
                "helmet", "vest", "status", "unsafe_counter",
                "ema_score", "occluded", "quality_score"
            ])
    
    def log_frame(self, frame_id: int, tracks: Dict, helmets: List[np.ndarray],
                  vests: List[np.ndarray], config: Config,
                  ema_manager: Optional[TemporalConsistencyEMA] = None,
                  occlusion_detector: Optional[OcclusionDetector] = None,
                  all_person_boxes: List[np.ndarray] = None,
                  quality_score: float = 1.0,
                  tracker=None, tracker_wrapper=None):
        """Log all persons in current frame with intelligence features."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            
            for pid, pdata in tracks.items():
                person_box = pdata["box"]
                unsafe_counter = pdata.get("unsafe_frame_counter", 0)
                
                has_helmet, has_vest, _ = associate_ppe_enhanced(
                    person_box, helmets, vests, config.USE_BODY_PROPORTIONS
                )
                
                # Check occlusion
                is_occluded = False
                if occlusion_detector and all_person_boxes:
                    is_occluded = occlusion_detector.is_occluded(person_box, all_person_boxes)
                
                # Determine status (EMA or legacy)
                if ema_manager and config.USE_EMA_TEMPORAL:
                    status = ema_manager.update_score(pid, has_helmet, has_vest)
                    ema_score = ema_manager.get_score(pid)
                else:
                    status, new_counter = determine_status(
                        has_helmet, has_vest, unsafe_counter, config.UNSAFE_THRESHOLD
                    )
                    pdata["unsafe_frame_counter"] = new_counter
                    ema_score = 1.0 if status == "SAFE" else 0.0
                    
                    if tracker:
                        tracker.update_unsafe_counter(pid, new_counter)
                    elif tracker_wrapper:
                        tracker_wrapper.update_unsafe_counter(pid, new_counter)
                
                pdata["status"] = status
                
                x1, y1, x2, y2 = map(int, person_box)
                writer.writerow([
                    timestamp, frame_id, pid,
                    int(x1), int(y1), int(x2), int(y2),
                    has_helmet, has_vest, status, unsafe_counter,
                    f"{ema_score:.3f}", is_occluded, f"{quality_score:.3f}"
                ])


# ================== INTELLIGENT SUMMARY CSV LOGGER ==================
class SummaryCSVLogger:
    """
    ENHANCED: Intelligent summary logging with comprehensive metrics.
    Tracks unique persons, incidents, compliance rates, and trends.
    """
    
    def __init__(self, summary_csv_file: str, interval_seconds: int = 30):
        self.summary_csv_file = summary_csv_file
        self.interval_seconds = interval_seconds
        self.last_summary_time = time.time()
        self.start_time = time.time()
        
        # Enhanced statistics tracking
        self.summary_stats = {
            # Frame statistics
            "total_frames": 0,
            "frames_with_persons": 0,
            "frames_with_violations": 0,
            
            # Person tracking
            "unique_person_ids": set(),
            "total_person_detections": 0,
            "max_persons_in_frame": 0,
            "min_persons_in_frame": float('inf'),
            
            # Safety status tracking
            "safe_count_sum": 0,
            "check_count_sum": 0,
            "unsafe_count_sum": 0,
            "max_unsafe_in_frame": 0,
            "frames_all_safe": 0,
            
            # PPE detection tracking
            "helmet_detections_sum": 0,
            "vest_detections_sum": 0,
            "avg_helmets_per_frame": deque(maxlen=100),
            "avg_vests_per_frame": deque(maxlen=100),
            
            # Performance metrics
            "fps_values": deque(maxlen=100),
            "quality_values": deque(maxlen=100),
            "confidence_values": deque(maxlen=100),
            
            # Incident tracking
            "total_unsafe_incidents": 0,
            "unsafe_person_ids": set(),
            "check_person_ids": set(),
            
            # Occlusion & intelligence metrics
            "total_occlusions_detected": 0,
            "frames_with_occlusion": 0,
            "avg_ema_scores": deque(maxlen=100),
            
            # Compliance tracking over time
            "compliance_history": deque(maxlen=10),  # Last 10 intervals
        }
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize summary CSV with comprehensive headers."""
        with open(self.summary_csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                # Time information
                "timestamp", "interval_start", "interval_end", "duration_seconds",
                
                # Frame statistics
                "total_frames", "frames_with_persons", "frames_with_violations",
                "frames_all_safe", "violation_rate_percent",
                
                # Performance metrics
                "avg_fps", "min_fps", "max_fps",
                "avg_quality", "quality_rating",
                "avg_confidence",
                
                # Person statistics
                "unique_persons", "total_detections", "avg_persons_per_frame",
                "max_persons", "min_persons",
                
                # Safety status counts
                "total_safe", "total_check", "total_unsafe",
                "avg_safe_per_frame", "avg_check_per_frame", "avg_unsafe_per_frame",
                "max_unsafe_simultaneous",
                
                # PPE detection statistics
                "total_helmets_detected", "total_vests_detected",
                "avg_helmets_per_frame", "avg_vests_per_frame",
                "helmet_detection_rate", "vest_detection_rate",
                
                # Compliance metrics
                "safety_compliance_percent", "full_compliance_percent",
                "partial_compliance_percent", "non_compliance_percent",
                
                # Incident tracking
                "unsafe_incidents", "unique_unsafe_persons", "unique_check_persons",
                
                # Intelligence metrics
                "occlusions_detected", "frames_with_occlusion", "avg_ema_score",
                
                # Trend analysis
                "compliance_trend", "status"
            ])
    
    def update(self, frame_id: int, tracks: Dict, helmets: List[np.ndarray],
              vests: List[np.ndarray], safe_count: int, check_count: int,
              unsafe_count: int, fps: float, quality_score: float = 1.0,
              current_conf: float = 0.3, occlusion_count: int = 0,
              ema_scores: Dict[int, float] = None):
        """Update summary statistics with enhanced tracking."""
        stats = self.summary_stats
        
        # Frame statistics
        stats["total_frames"] += 1
        
        if len(tracks) > 0:
            stats["frames_with_persons"] += 1
        
        if unsafe_count > 0 or check_count > 0:
            stats["frames_with_violations"] += 1
        
        if unsafe_count == 0 and check_count == 0 and len(tracks) > 0:
            stats["frames_all_safe"] += 1
        
        # Person tracking
        for pid in tracks.keys():
            stats["unique_person_ids"].add(pid)
        
        stats["total_person_detections"] += len(tracks)
        
        if len(tracks) > 0:
            stats["max_persons_in_frame"] = max(stats["max_persons_in_frame"], len(tracks))
            stats["min_persons_in_frame"] = min(stats["min_persons_in_frame"], len(tracks))
        
        # Safety status tracking
        stats["safe_count_sum"] += safe_count
        stats["check_count_sum"] += check_count
        stats["unsafe_count_sum"] += unsafe_count
        stats["max_unsafe_in_frame"] = max(stats["max_unsafe_in_frame"], unsafe_count)
        
        # Track unsafe and check person IDs
        for pid, pdata in tracks.items():
            status = pdata.get("status", "SAFE")
            if status == "UNSAFE":
                stats["unsafe_person_ids"].add(pid)
            elif status == "CHECK":
                stats["check_person_ids"].add(pid)
        
        # Count unsafe incidents (new unsafe person)
        if unsafe_count > 0:
            stats["total_unsafe_incidents"] += unsafe_count
        
        # PPE detection tracking
        stats["helmet_detections_sum"] += len(helmets)
        stats["vest_detections_sum"] += len(vests)
        stats["avg_helmets_per_frame"].append(len(helmets))
        stats["avg_vests_per_frame"].append(len(vests))
        
        # Performance metrics
        if fps > 0:
            stats["fps_values"].append(fps)
        stats["quality_values"].append(quality_score)
        stats["confidence_values"].append(current_conf)
        
        # Occlusion tracking
        if occlusion_count > 0:
            stats["total_occlusions_detected"] += occlusion_count
            stats["frames_with_occlusion"] += 1
        
        # EMA scores tracking
        if ema_scores:
            avg_ema = np.mean(list(ema_scores.values())) if ema_scores else 1.0
            stats["avg_ema_scores"].append(avg_ema)
    
    def should_save_summary(self) -> bool:
        """Check if it's time to save."""
        return time.time() - self.last_summary_time >= self.interval_seconds
    
    def save_summary(self, config: Config) -> bool:
        """Save comprehensive summary statistics."""
        if not self.should_save_summary():
            return False
        
        current_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        interval_start = datetime.fromtimestamp(self.last_summary_time).strftime("%Y-%m-%d %H:%M:%S")
        interval_end = timestamp
        elapsed_seconds = current_time - self.last_summary_time
        
        stats = self.summary_stats
        
        # Calculate comprehensive metrics
        total_frames = stats["total_frames"]
        if total_frames == 0:
            return False
        
        # Frame metrics
        violation_rate = (stats["frames_with_violations"] / total_frames * 100) if total_frames > 0 else 0
        
        # Performance metrics
        avg_fps = np.mean(stats["fps_values"]) if len(stats["fps_values"]) > 0 else 0
        min_fps = np.min(stats["fps_values"]) if len(stats["fps_values"]) > 0 else 0
        max_fps = np.max(stats["fps_values"]) if len(stats["fps_values"]) > 0 else 0
        
        avg_quality = np.mean(stats["quality_values"]) if len(stats["quality_values"]) > 0 else 0
        quality_rating = "Excellent" if avg_quality >= 0.75 else "Good" if avg_quality >= 0.6 else "Fair" if avg_quality >= 0.4 else "Poor"
        
        avg_confidence = np.mean(stats["confidence_values"]) if len(stats["confidence_values"]) > 0 else 0
        
        # Person metrics
        unique_persons = len(stats["unique_person_ids"])
        total_detections = stats["total_person_detections"]
        avg_persons = total_detections / total_frames if total_frames > 0 else 0
        max_persons = stats["max_persons_in_frame"]
        min_persons = stats["min_persons_in_frame"] if stats["min_persons_in_frame"] != float('inf') else 0
        
        # Safety status metrics
        total_safe = stats["safe_count_sum"]
        total_check = stats["check_count_sum"]
        total_unsafe = stats["unsafe_count_sum"]
        
        avg_safe = total_safe / total_frames if total_frames > 0 else 0
        avg_check = total_check / total_frames if total_frames > 0 else 0
        avg_unsafe = total_unsafe / total_frames if total_frames > 0 else 0
        
        max_unsafe_simultaneous = stats["max_unsafe_in_frame"]
        
        # PPE metrics
        total_helmets = stats["helmet_detections_sum"]
        total_vests = stats["vest_detections_sum"]
        avg_helmets = np.mean(stats["avg_helmets_per_frame"]) if len(stats["avg_helmets_per_frame"]) > 0 else 0
        avg_vests = np.mean(stats["avg_vests_per_frame"]) if len(stats["avg_vests_per_frame"]) > 0 else 0
        
        # Detection rates (PPE detected per person)
        helmet_detection_rate = (total_helmets / total_detections * 100) if total_detections > 0 else 0
        vest_detection_rate = (total_vests / total_detections * 100) if total_detections > 0 else 0
        
        # Compliance metrics
        total_status_counts = total_safe + total_check + total_unsafe
        safety_compliance = (total_safe / total_status_counts * 100) if total_status_counts > 0 else 0
        full_compliance = (total_safe / total_status_counts * 100) if total_status_counts > 0 else 0
        partial_compliance = (total_check / total_status_counts * 100) if total_status_counts > 0 else 0
        non_compliance = (total_unsafe / total_status_counts * 100) if total_status_counts > 0 else 0
        
        # Store compliance for trend analysis
        stats["compliance_history"].append(safety_compliance)
        
        # Trend analysis
        if len(stats["compliance_history"]) >= 2:
            recent_trend = stats["compliance_history"][-1] - stats["compliance_history"][-2]
            if recent_trend > 5:
                compliance_trend = "Improving"
            elif recent_trend < -5:
                compliance_trend = "Declining"
            else:
                compliance_trend = "Stable"
        else:
            compliance_trend = "N/A"
        
        # Overall status
        if safety_compliance >= 95:
            status = "Excellent"
        elif safety_compliance >= 85:
            status = "Good"
        elif safety_compliance >= 70:
            status = "Acceptable"
        elif safety_compliance >= 50:
            status = "Needs Improvement"
        else:
            status = "Critical"
        
        # Incident tracking
        unsafe_incidents = stats["total_unsafe_incidents"]
        unique_unsafe = len(stats["unsafe_person_ids"])
        unique_check = len(stats["check_person_ids"])
        
        # Intelligence metrics
        total_occlusions = stats["total_occlusions_detected"]
        frames_with_occlusion = stats["frames_with_occlusion"]
        avg_ema = np.mean(stats["avg_ema_scores"]) if len(stats["avg_ema_scores"]) > 0 else 1.0
        
        # Write to CSV
        with open(self.summary_csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                # Time information
                timestamp, interval_start, interval_end, f"{elapsed_seconds:.1f}",
                
                # Frame statistics
                total_frames, stats["frames_with_persons"], stats["frames_with_violations"],
                stats["frames_all_safe"], f"{violation_rate:.2f}",
                
                # Performance metrics
                f"{avg_fps:.2f}", f"{min_fps:.2f}", f"{max_fps:.2f}",
                f"{avg_quality:.3f}", quality_rating,
                f"{avg_confidence:.3f}",
                
                # Person statistics
                unique_persons, total_detections, f"{avg_persons:.2f}",
                max_persons, min_persons,
                
                # Safety status counts
                total_safe, total_check, total_unsafe,
                f"{avg_safe:.2f}", f"{avg_check:.2f}", f"{avg_unsafe:.2f}",
                max_unsafe_simultaneous,
                
                # PPE detection statistics
                total_helmets, total_vests,
                f"{avg_helmets:.2f}", f"{avg_vests:.2f}",
                f"{helmet_detection_rate:.2f}", f"{vest_detection_rate:.2f}",
                
                # Compliance metrics
                f"{safety_compliance:.2f}", f"{full_compliance:.2f}",
                f"{partial_compliance:.2f}", f"{non_compliance:.2f}",
                
                # Incident tracking
                unsafe_incidents, unique_unsafe, unique_check,
                
                # Intelligence metrics
                total_occlusions, frames_with_occlusion, f"{avg_ema:.3f}",
                
                # Trend analysis
                compliance_trend, status
            ])
        
        # Enhanced logging
        logger.info(
            f"Summary [{interval_start} → {interval_end}]:\n"
            f"  Frames: {total_frames} | FPS: {avg_fps:.1f} ({min_fps:.1f}-{max_fps:.1f}) | Quality: {quality_rating}\n"
            f"  Persons: {unique_persons} unique, {avg_persons:.1f} avg/frame, {max_persons} max\n"
            f"  Safety: {safety_compliance:.1f}% | Safe: {total_safe} | Check: {total_check} | Unsafe: {total_unsafe}\n"
            f"  Incidents: {unsafe_incidents} unsafe events | {unique_unsafe} persons with violations\n"
            f"  Trend: {compliance_trend} | Status: {status}"
        )
        
        # Reset statistics for next interval
        self.last_summary_time = current_time
        self.summary_stats = {
            "total_frames": 0,
            "frames_with_persons": 0,
            "frames_with_violations": 0,
            "unique_person_ids": set(),
            "total_person_detections": 0,
            "max_persons_in_frame": 0,
            "min_persons_in_frame": float('inf'),
            "safe_count_sum": 0,
            "check_count_sum": 0,
            "unsafe_count_sum": 0,
            "max_unsafe_in_frame": 0,
            "frames_all_safe": 0,
            "helmet_detections_sum": 0,
            "vest_detections_sum": 0,
            "avg_helmets_per_frame": deque(maxlen=100),
            "avg_vests_per_frame": deque(maxlen=100),
            "fps_values": deque(maxlen=100),
            "quality_values": deque(maxlen=100),
            "confidence_values": deque(maxlen=100),
            "total_unsafe_incidents": 0,
            "unsafe_person_ids": set(),
            "check_person_ids": set(),
            "total_occlusions_detected": 0,
            "frames_with_occlusion": 0,
            "avg_ema_scores": deque(maxlen=100),
            "compliance_history": self.summary_stats["compliance_history"],  # Keep history
        }
        
        return True


# ================== ENHANCED VISUALIZATION ==================
def draw_enhanced_visualization(frame: np.ndarray, tracks: Dict, helmets: List[np.ndarray],
                               vests: List[np.ndarray], config: Config, fps: float = 0,
                               ema_manager: Optional[TemporalConsistencyEMA] = None,
                               quality_metrics: Optional[Dict] = None) -> np.ndarray:
    """Enhanced visualization with all intelligence features."""
    frame_copy = frame.copy()
    h, w = frame_copy.shape[:2]
    
    # Calculate statistics
    safe_count = 0
    check_count = 0
    unsafe_count = 0
    person_statuses = {}
    
    for pid, pdata in tracks.items():
        person_box = pdata["box"]
        
        has_helmet, has_vest, match_info = associate_ppe_enhanced(
            person_box, helmets, vests, config.USE_BODY_PROPORTIONS, config.SHOW_ZONES
        )
        
        if ema_manager and config.USE_EMA_TEMPORAL:
            status = ema_manager.update_score(pid, has_helmet, has_vest)
            ema_score = ema_manager.get_score(pid)
        else:
            unsafe_counter = pdata.get("unsafe_frame_counter", 0)
            status, _ = determine_status(has_helmet, has_vest, unsafe_counter, config.UNSAFE_THRESHOLD)
            ema_score = 1.0
        
        person_statuses[pid] = (status, has_helmet, has_vest, match_info, ema_score)
        
        if status == "SAFE":
            safe_count += 1
        elif status == "CHECK":
            check_count += 1
        else:
            unsafe_count += 1
    
    # Draw person boxes
    for pid, pdata in tracks.items():
        person_box = pdata["box"]
        status, has_helmet, has_vest, match_info, ema_score = person_statuses[pid]
        
        if status == "SAFE":
            color = (0, 255, 0)
            thickness = 2
        elif status == "CHECK":
            color = (0, 165, 255)
            thickness = 2
        else:
            color = (0, 0, 255)
            thickness = 3
        
        x1, y1, x2, y2 = map(int, person_box)
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, thickness)
        
        # Label with EMA score
        label = f"ID:{pid} {status}"
        if config.SHOW_DEBUG_INFO and config.USE_EMA_TEMPORAL:
            label += f" [{ema_score:.2f}]"
        if not has_helmet:
            label += " [No Helmet]"
        if not has_vest:
            label += " [No Vest]"
        
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame_copy, (x1, y1 - text_height - 10), (x1 + text_width + 4, y1), color, -1)
        cv2.putText(frame_copy, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw zones if enabled
        if config.SHOW_ZONES and match_info:
            px1, py1, px2, py2 = person_box
            helmet_zone_top, helmet_zone_bottom = match_info["helmet_zone"]
            vest_zone_top, vest_zone_bottom = match_info["vest_zone"]
            
            overlay = frame_copy.copy()
            cv2.rectangle(overlay, (int(px1), int(helmet_zone_top)), (int(px2), int(helmet_zone_bottom)), (255, 255, 0), -1)
            frame_copy = cv2.addWeighted(frame_copy, 0.7, overlay, 0.3, 0)
            
            overlay = frame_copy.copy()
            cv2.rectangle(overlay, (int(px1), int(vest_zone_top)), (int(px2), int(vest_zone_bottom)), (0, 255, 255), -1)
            frame_copy = cv2.addWeighted(frame_copy, 0.7, overlay, 0.3, 0)
    
    # Draw PPE boxes
    for h in helmets:
        x1, y1, x2, y2 = map(int, h)
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (255, 0, 0), 1)
    
    for v in vests:
        x1, y1, x2, y2 = map(int, v)
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 255), 1)
    
    # Info Panel
    panel_width = 450
    panel_height = 280 if config.SHOW_QUALITY_INFO else 220
    panel_x = 10
    panel_y = 10
    
    overlay = frame_copy.copy()
    cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), (0, 0, 0), -1)
    frame_copy = cv2.addWeighted(overlay, 0.75, frame_copy, 0.25, 0)
    
    cv2.putText(frame_copy, "Enhanced PPE Safety Monitor", (panel_x + 10, panel_y + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    y_offset = 60
    
    if config.SHOW_FPS:
        cv2.putText(frame_copy, f"FPS: {fps:.1f}", (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y_offset += 30
    
    if config.SHOW_STATS:
        cv2.putText(frame_copy, f"Persons: {len(tracks)}", (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 30
        
        cv2.putText(frame_copy, f"Safe: {safe_count}", (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 30
        
        cv2.putText(frame_copy, f"Check: {check_count}", (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        y_offset += 30
        
        cv2.putText(frame_copy, f"Unsafe: {unsafe_count}", (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += 30
        
        cv2.putText(frame_copy, f"PPE: H:{len(helmets)} V:{len(vests)}",
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y_offset += 25
    
    if config.SHOW_QUALITY_INFO and quality_metrics:
        quality_score = quality_metrics.get('quality_score', 1.0)
        quality_label = quality_metrics.get('label', 'Unknown')
        
        q_color = (0, 255, 0) if quality_score >= 0.75 else (0, 165, 255) if quality_score >= 0.5 else (0, 0, 255)
        cv2.putText(frame_copy, f"Quality: {quality_label} ({quality_score:.2f})",
                   (panel_x + 10, panel_y + y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, q_color, 2)
    
    return frame_copy


# ================== MAIN PROCESSING ==================
def process_video(config: Config):
    """Main video processing with all intelligence features."""
    print("=" * 70)
    print("Enhanced PPE Safety Monitoring System - AI Powered")
    print("=" * 70)
    
    video_source = normalize_video_source(config.VIDEO_SOURCE)
    source_type = "Camera" if isinstance(video_source, int) else ("RTSP" if str(video_source).startswith(('rtsp://', 'http://')) else "Video File")
    logger.info(f"Source: {source_type} - {video_source}")
    
    # Load models
    try:
        logger.info(f"Loading models...")
        person_model = YOLO(config.PERSON_MODEL_PATH)
        ppe_model = YOLO(config.PPE_MODEL_PATH)
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        return
    
    # Initialize intelligence components
    scene_quality = SceneQualityAnalyzer() if config.SCENE_QUALITY_ENABLED else None
    adaptive_conf = AdaptiveConfidenceManager(
        config.CONFIDENCE, config.MIN_CONFIDENCE, config.MAX_CONFIDENCE
    ) if config.ADAPTIVE_CONFIDENCE_ENABLED else None
    occlusion_detector = OcclusionDetector(config.OCCLUSION_THRESHOLD) if config.OCCLUSION_DETECTION_ENABLED else None
    ppe_memory = PPEMemoryManager(config.PPE_MEMORY_FRAMES) if config.PPE_MEMORY_ENABLED else None
    ema_manager = TemporalConsistencyEMA(config.EMA_ALPHA, config.UNSAFE_THRESHOLD_EMA) if config.USE_EMA_TEMPORAL else None
    
    logger.info("Intelligence Features:")
    if scene_quality:
        logger.info("  ✓ Scene Quality Analysis")
    if adaptive_conf:
        logger.info("  ✓ Adaptive Confidence")
    if occlusion_detector:
        logger.info("  ✓ Occlusion Detection")
    if ppe_memory:
        logger.info("  ✓ PPE Memory")
    if ema_manager:
        logger.info("  ✓ EMA Temporal Consistency")
    if config.USE_BODY_PROPORTIONS:
        logger.info("  ✓ Body Proportions")
    
    # Initialize tracker
    tracker = None
    tracker_wrapper = None
    use_bytetrack = False
    
    if config.USE_BYTETRACK and config.TRACKER_TYPE:
        try:
            import lap
            logger.info(f"Using ByteTrack: {config.TRACKER_TYPE}")
            tracker_wrapper = ByteTrackWrapper(person_model, config.TRACKER_TYPE)
            use_bytetrack = True
        except ImportError:
            logger.warning("ByteTrack unavailable, using custom tracker")
            tracker = IntelligentPersonTracker(0.4, True)
    else:
        logger.info("Using custom tracker")
        tracker = IntelligentPersonTracker(0.4, True)
    
    anti_flicker = AntiFlickerStatusManager(
        config.STATUS_HISTORY_SIZE, config.STATUS_CHANGE_THRESHOLD
    ) if config.ANTI_FLICKER_ENABLED else None
    
    logger_instance = CSVLogger(config.CSV_FILE)
    summary_logger = SummaryCSVLogger(config.SUMMARY_CSV_FILE, config.SUMMARY_INTERVAL_SECONDS)
    
    telegram = TelegramNotifier(
        config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, config.TELEGRAM_COOLDOWN_SECONDS
    ) if config.TELEGRAM_ENABLED else None
    
    # Open video
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        logger.error(f"Cannot open: {video_source}")
        return
    
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video: {width}x{height} @ {fps_video:.2f} FPS")
    if total_frames > 0:
        logger.info(f"Frames: {total_frames}")
    logger.info("Processing started...\n")
    
    frame_id = 0
    frame_skip_counter = 0
    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0
    current_conf = config.CONFIDENCE
    quality_metrics = {'quality_score': 1.0, 'label': 'Good'}
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("End of video")
                break
            
            if config.FRAME_SKIP > 0:
                frame_skip_counter += 1
                if frame_skip_counter <= config.FRAME_SKIP:
                    continue
                frame_skip_counter = 0
            
            if config.FRAME_RESIZE:
                frame = cv2.resize(frame, config.FRAME_RESIZE)
            
            frame_id += 1
            fps_frame_count += 1
            
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                current_fps = fps_frame_count / elapsed
                fps_frame_count = 0
                fps_start_time = time.time()
            
            # Scene quality analysis
            if scene_quality and frame_id % config.QUALITY_CHECK_INTERVAL == 0:
                quality_score, metrics = scene_quality.analyze_frame(frame)
                quality_metrics = metrics
                quality_metrics['label'] = scene_quality.get_quality_label()
            else:
                quality_score = quality_metrics.get('quality_score', 1.0)
            
            # Adaptive confidence
            if adaptive_conf:
                current_conf = adaptive_conf.update(len(tracks) if frame_id > 1 else 0, quality_score)
            
            # Detection
            try:
                if use_bytetrack:
                    person_results = person_model.track(
                        frame, classes=[0], conf=current_conf,
                        tracker=config.TRACKER_TYPE, verbose=False, persist=True
                    )
                else:
                    person_results = person_model(frame, classes=[0], conf=current_conf, verbose=False)
                
                ppe_results = ppe_model(frame, conf=current_conf, verbose=False)
            except Exception as e:
                logger.error(f"Detection failed: {e}")
                continue
            
            # Extract PPE
            helmets = []
            vests = []
            if ppe_results[0].boxes is not None:
                for box in ppe_results[0].boxes:
                    cls = int(box.cls[0])
                    bbox = box.xyxy[0].cpu().numpy()
                    if cls == 0:
                        helmets.append(bbox)
                    elif cls == 1:
                        vests.append(bbox)
            
            # Tracking
            try:
                if use_bytetrack and tracker_wrapper:
                    tracks = tracker_wrapper.update(person_results[0])
                else:
                    persons = []
                    if person_results[0].boxes is not None:
                        for box in person_results[0].boxes:
                            persons.append(box.xyxy[0].cpu().numpy())
                    tracks = tracker.update(persons)
            except Exception as e:
                logger.error(f"Tracking failed: {e}")
                continue
            
            # Get all person boxes for occlusion detection
            all_person_boxes = [pdata["box"] for pdata in tracks.values()]
            
            # PPE Memory update
            if ppe_memory:
                ppe_memory.increment_age()
            
            # CSV Logging
            logger_instance.log_frame(
                frame_id, tracks, helmets, vests, config,
                ema_manager, occlusion_detector, all_person_boxes,
                quality_score, tracker, tracker_wrapper
            )
            
            # Calculate statistics
            safe_count = check_count = unsafe_count = 0
            for pid, pdata in tracks.items():
                person_box = pdata["box"]
                has_helmet, has_vest, _ = associate_ppe_enhanced(
                    person_box, helmets, vests, config.USE_BODY_PROPORTIONS
                )
                
                # Apply PPE memory if occluded
                if occlusion_detector and occlusion_detector.is_occluded(person_box, all_person_boxes):
                    if ppe_memory:
                        mem_helmet, mem_vest = ppe_memory.get_remembered_ppe(pid)
                        if mem_helmet is not None:
                            has_helmet = mem_helmet
                        if mem_vest is not None:
                            has_vest = mem_vest
                
                # Update PPE memory
                if ppe_memory:
                    ppe_memory.update(pid, has_helmet, has_vest)
                
                # Determine status
                if ema_manager:
                    status = ema_manager.update_score(pid, has_helmet, has_vest)
                else:
                    unsafe_counter = pdata.get("unsafe_frame_counter", 0)
                    status, _ = determine_status(has_helmet, has_vest, unsafe_counter, config.UNSAFE_THRESHOLD)
                
                if status == "SAFE":
                    safe_count += 1
                elif status == "CHECK":
                    check_count += 1
                else:
                    unsafe_count += 1
            
            # Summary logging
            summary_logger.update(
                frame_id, tracks, helmets, vests,
                safe_count, check_count, unsafe_count, current_fps, quality_score
            )
            summary_logger.save_summary(config)
            
            # Visualization
            if config.SHOW_VIDEO:
                frame_vis = draw_enhanced_visualization(
                    frame, tracks, helmets, vests, config,
                    current_fps, ema_manager, quality_metrics
                )
                cv2.imshow(config.WINDOW_NAME, frame_vis)
            
            # Telegram alerts
            if telegram and unsafe_count > 0:
                telegram.send_alert(frame, unsafe_count, len(tracks))
            
            # Progress
            if total_frames > 0:
                progress = (frame_id / total_frames) * 100
                print(f"\rProgress: {progress:.1f}% | Frame: {frame_id} | "
                      f"FPS: {current_fps:.1f} | Conf: {current_conf:.3f} | "
                      f"Quality: {quality_metrics['label']} | "
                      f"Persons: {len(tracks)} | Safe: {safe_count} | Unsafe: {unsafe_count}",
                      end="", flush=True)
            else:
                print(f"\rFrame: {frame_id} | FPS: {current_fps:.1f} | "
                      f"Conf: {current_conf:.3f} | Quality: {quality_metrics['label']} | "
                      f"Persons: {len(tracks)} | Safe: {safe_count} | Unsafe: {unsafe_count}",
                      end="", flush=True)
            
            # Exit on 'q'
            if config.SHOW_VIDEO and cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("\n'q' pressed - Stopping...")
                break
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
    finally:
        summary_logger.save_summary(config)
        cap.release()
        if config.SHOW_VIDEO:
            cv2.destroyAllWindows()
        logger.info(f"\nFinished. Logged {frame_id} frames")
        logger.info(f"CSV: {config.CSV_FILE}")
        logger.info(f"Summary: {config.SUMMARY_CSV_FILE}")


# ================== MAIN ENTRY POINT ==================
if __name__ == "__main__":
    config = Config()
    
    # ========== MAIN SETTINGS - CHANGE THESE ==========
    
    # Video source (camera/file/RTSP)
    config.VIDEO_SOURCE = 0  # 0 for webcam, "video.mp4" for file
    
    # Base confidence (will be adapted automatically)
    config.CONFIDENCE = 0.6  # System will adapt this
    
    # ========== INTELLIGENCE FEATURES (Optional) ==========
    
    # Adaptive Confidence
    config.ADAPTIVE_CONFIDENCE_ENABLED = True
    config.MIN_CONFIDENCE = 0.2
    config.MAX_CONFIDENCE = 0.5
    
    # Enhanced Temporal Consistency (EMA)
    config.USE_EMA_TEMPORAL = True  # Recommended!
    config.EMA_ALPHA = 0.3  # 0.1=slow/stable, 0.5=fast/responsive
    config.UNSAFE_THRESHOLD_EMA = 0.7
    
    # Occlusion Handling
    config.OCCLUSION_DETECTION_ENABLED = True
    config.OCCLUSION_THRESHOLD = 0.3
    
    # Scene Quality
    config.SCENE_QUALITY_ENABLED = True
    config.QUALITY_CHECK_INTERVAL = 30
    
    # PPE Memory
    config.PPE_MEMORY_ENABLED = True
    config.PPE_MEMORY_FRAMES = 15
    
    # Body Proportions
    config.USE_BODY_PROPORTIONS = True
    
    # ========== VISUALIZATION ==========
    config.SHOW_VIDEO = True
    config.SHOW_FPS = True
    config.SHOW_STATS = True
    config.SHOW_DEBUG_INFO = True
    config.SHOW_QUALITY_INFO = True
    # config.SHOW_ZONES = True  # Uncomment to see PPE zones
    
    # ========== OPTIONAL PERFORMANCE ==========
    # config.FRAME_RESIZE = (1280, 720)  # Resize for speed
    # config.FRAME_SKIP = 1  # Process every 2nd frame
    
    print("\n" + "="*70)
    print("ENHANCED PPE SAFETY MONITORING SYSTEM")
    print("="*70)
    print("\nNew Intelligence Features:")
    print("  ✓ Adaptive Confidence - Auto-adjusts detection sensitivity")
    print("  ✓ EMA Temporal Consistency - Smoother status decisions")
    print("  ✓ Occlusion Detection - Handles overlapping persons")
    print("  ✓ Scene Quality Analysis - Adapts to lighting/blur")
    print("  ✓ PPE Memory - Remembers last seen PPE")
    print("  ✓ Body Proportions - Smarter PPE association")
    print("\n" + "="*70 + "\n")
    
    process_video(config)
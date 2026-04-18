import math
import time
import numpy as np

def calculate_distance(p1, p2):
    """
    Calculate Euclidean distance between two points p1 and p2.
    Points are expected as (x, y) tuples.
    """
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def get_center(p1, p2):
    """
    Get the midpoint between p1 and p2.
    """
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

class SmoothFilter:
    """
    Exponential Moving Average (EMA) filter to reduce jitter from the raw coordinates.
    """
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.value = None

    def update(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        return self.value

class FPSCounter:
    """
    Utility class to track frames per second.
    """
    def __init__(self):
        self.pTime = 0

    def update(self):
        cTime = time.time()
        fps = 0
        if cTime - self.pTime > 0:
            fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        return int(fps)

def draw_neon_text(img, text, pos, font_scale=1, thickness=2, color=(255, 255, 255), glow_color=(255, 0, 255)):
    import cv2
    # Neon glow effect by drawing thicker text first
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_DUPLEX, font_scale, glow_color, thickness + 4, cv2.LINE_AA)
    # Inner light
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness, cv2.LINE_AA)

def draw_futuristic_bar(img, x, y, width, height, value, fill_color=(255, 0, 255), label=""):
    import cv2
    # Glassy background
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y), (x + width, y + height), (20, 10, 30), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    # Border
    cv2.rectangle(img, (x, y), (x + width, y + height), fill_color, 1)
    
    # Corners
    line_len = min(20, int(width * 0.4))
    t = 2
    accent = (255, 255, 255)
    cv2.line(img, (x, y), (x + line_len, y), accent, t)
    cv2.line(img, (x, y), (x, y + line_len), accent, t)
    cv2.line(img, (x + width, y), (x + width - line_len, y), accent, t)
    cv2.line(img, (x + width, y), (x + width, y + line_len), accent, t)
    cv2.line(img, (x, y + height), (x + line_len, y + height), accent, t)
    cv2.line(img, (x, y + height), (x, y + height - line_len), accent, t)
    cv2.line(img, (x + width, y + height), (x + width - line_len, y + height), accent, t)
    cv2.line(img, (x + width, y + height), (x + width, y + height - line_len), accent, t)
    
    # Label
    if label:
        draw_neon_text(img, label, (x - 10, y - 15), 0.4, 1, (255, 255, 255), fill_color)
    
    # Fill value
    value = max(0, min(100, value))
    fill_h = int((height - 10) * (value / 100))
    if fill_h > 0:
        bar_box = [(x + 5, y + height - 5 - fill_h), (x + width - 5, y + height - 5)]
        cv2.rectangle(img, bar_box[0], bar_box[1], fill_color, -1)
        # Segments
        for step in range(y + height - 5, y + height - 5 - fill_h, -10):
            cv2.line(img, (x + 5, step), (x + width - 5, step), (10, 0, 20), 2)

def draw_hud_background(img):
    import cv2
    h, w = img.shape[:2]
    overlay = img.copy()
    # Darken
    cv2.rectangle(overlay, (0, 0), (w, h), (15, 0, 25), -1)
    
    # Grid
    for i in range(0, w, 60):
        cv2.line(overlay, (i, 0), (i, h), (60, 20, 80), 1)
    for i in range(0, h, 60):
        cv2.line(overlay, (0, i), (w, i), (60, 20, 80), 1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    
    # Center target
    cx, cy = int(w/2), int(h/2)
    # Orb effect
    cv2.ellipse(img, (cx, cy), (150, 150), 0, 0, 360, (250, 50, 150), 1, cv2.LINE_AA)
    cv2.ellipse(img, (cx, cy), (120, 120), 45, 0, 360, (255, 200, 50), 1, cv2.LINE_AA)
    
    # Corner brackets (large)
    bl = 40
    th = 2
    accent = (200, 100, 255)
    margin = 30
    cv2.line(img, (margin, margin), (margin + bl, margin), accent, th)
    cv2.line(img, (margin, margin), (margin, margin + bl), accent, th)
    cv2.line(img, (w - margin, margin), (w - margin - bl, margin), accent, th)
    cv2.line(img, (w - margin, margin), (w - margin, margin + bl), accent, th)
    cv2.line(img, (margin, h - margin), (margin + bl, h - margin), accent, th)
    cv2.line(img, (margin, h - margin), (margin, h - margin - bl), accent, th)
    cv2.line(img, (w - margin, h - margin), (w - margin - bl, h - margin), accent, th)
    cv2.line(img, (w - margin, h - margin), (w - margin, h - margin - bl), accent, th)
    
    # Tech texts
    draw_neon_text(img, "THE FUTURE OF", (w - 180, 50), 0.4, 1, (255, 255, 255), (255, 0, 255))
    draw_neon_text(img, "VISUAL TECHNOLOGY", (w - 180, 70), 0.4, 1, (255, 255, 255), (255, 0, 255))

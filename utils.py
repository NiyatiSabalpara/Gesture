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

import time
from utils import calculate_distance

class GestureRecognizer:
    def __init__(self):
        # Activation state
        self.is_active = False
        self.open_palm_start_time = 0
        self.activation_hold_time = 2.0 # seconds
        self.cooldown = 1.0
        self.last_toggle_time = 0

        # Swipe tracking
        self.prev_x = None
        self.swipe_threshold = 100 # pixel threshold for swipe

    def check_activation(self, fingers):
        """
        Check if the 4 main fingers are up and held for 2 seconds to toggle activation state.
        """
        if sum(fingers[1:]) == 4:
            if self.open_palm_start_time == 0:
                self.open_palm_start_time = time.time()
            elif time.time() - self.open_palm_start_time >= self.activation_hold_time:
                # Toggle state if not recently toggled
                if time.time() - self.last_toggle_time > self.cooldown:
                    self.is_active = not self.is_active
                    self.last_toggle_time = time.time()
                    self.open_palm_start_time = 0 # reset
                return True # indicating a toggle just happened
        else:
            self.open_palm_start_time = 0
            
        return False

    def detect_pinch(self, lm_list):
        """
        Calculates distance between thumb tip (4) and index tip (8).
        Returns the distance and the center point for drawing.
        """
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        distance = calculate_distance((x1, y1), (x2, y2))
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        return distance, (cx, cy)

    def detect_fist(self, fingers):
        """
        Checks if 4 main fingers are closed.
        """
        return sum(fingers[1:]) == 0

    def detect_peace(self, fingers):
        """
        Checks if index and middle are up, others down.
        """
        # fingers list: [thumb, index, middle, ring, pinky]
        return fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0

    def detect_swipe(self, lm_list):
        """
        Tracks wrist x position to detect left/right swipe.
        Returns 'left', 'right', or None
        """
        wrist_x = lm_list[0][1]
        
        if self.prev_x is None:
            self.prev_x = wrist_x
            return None

        diff = wrist_x - self.prev_x
        
        if diff > self.swipe_threshold:
            self.prev_x = wrist_x # Reset after successful swipe
            return 'right'
        elif diff < -self.swipe_threshold:
            self.prev_x = wrist_x # Reset after successful swipe
            return 'left'
            
        # Optional: gracefully decay prev_x or update it to follow to not trigger late
        # But for robust swiping, we can just update it constantly if moving slow
        score_diff = abs(diff)
        if score_diff < 10: 
            self.prev_x = wrist_x

        return None

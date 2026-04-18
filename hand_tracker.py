import cv2
import mediapipe as mp
import time

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None

        # Use new Tasks API which is fully compatible with Python 3.13
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.detection_con,
            min_hand_presence_confidence=self.track_con,
            min_tracking_confidence=self.track_con
        )
        self.landmarker = HandLandmarker.create_from_options(options)

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Timestamp must be monotonic integer in milliseconds
        timestamp_ms = int(time.time() * 1000)
        
        self.results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        
        if draw and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                self.draw_landmarks(img, hand_landmarks)
        return img

    def draw_landmarks(self, img, hand_landmarks):
        """Draws the landmarks and connections manually without mp.solutions"""
        h, w, _ = img.shape
        connections = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
                       (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16),
                       (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
        
        points = []
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            points.append((cx, cy))
            cv2.circle(img, (cx, cy), 3, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 6, (255, 0, 255), 1)
            
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(points) and end_idx < len(points):
                cv2.line(img, points[start_idx], points[end_idx], (255, 255, 0), 2)

    def get_positions(self, img, hand_no=0, draw=True):
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                h, w, c = img.shape
                for id, lm in enumerate(my_hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 255, 255), cv2.FILLED)
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), 1)
        return lm_list
        
    def fingers_up(self, lm_list):
        fingers = []
        if not lm_list:
            return fingers

        # Thumb (Comparing tip x to previous x for basic open/closed state)
        if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1) 
        else:
            fingers.append(0)

        # 4 Fingers (Comparing tip y to lower joint y)
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

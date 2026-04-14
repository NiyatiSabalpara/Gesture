import cv2
import numpy as np
from hand_tracker import HandTracker
from gesture_logic import GestureRecognizer
from system_control import SystemController
from utils import SmoothFilter, FPSCounter

def main():
    # Desired webcam dimensions
    wCam, hCam = 640, 480

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    tracker = HandTracker(detection_con=0.8, track_con=0.8)
    recognizer = GestureRecognizer()
    controller = SystemController()

    fps_counter = FPSCounter()
    
    # Smooth filters for UI and Control
    vol_filter = SmoothFilter(alpha=0.3)
    bright_filter = SmoothFilter(alpha=0.2)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame")
            break

        # Flip horizontally for selfie-view
        img = cv2.flip(img, 1)

        img = tracker.find_hands(img)
        lm_list = tracker.get_positions(img, draw=False)

        current_vol = controller.get_volume()
        current_bright = controller.get_brightness()

        vol_bar = np.interp(current_vol, [0, 100], [400, 150])
        bright_bar = np.interp(current_bright, [0, 100], [400, 150])

        if len(lm_list) != 0:
            fingers = tracker.fingers_up(lm_list)
            
            # Check for activation toggle
            toggled = recognizer.check_activation(fingers)
            
            if recognizer.is_active:
                
                # 1. Pinch for Volume
                # Only check if index and thumb are primary factors, 
                # but to avoid conflicts with swipe/fist let's check holding index/thumb out
                if fingers[1] == 1 and sum(fingers[2:]) == 0: 
                    distance, center = recognizer.detect_pinch(lm_list)
                    cv2.circle(img, center, 15, (0, 255, 0), cv2.FILLED)
                    
                    # Map distance to percentage (usually 20 to 200 pixels)
                    target_vol = np.interp(distance, [20, 200], [0, 100])
                    smooth_vol = vol_filter.update(target_vol)
                    controller.set_volume(smooth_vol)
                    vol_bar = np.interp(smooth_vol, [0, 100], [400, 150])

                # 2. Vertical movement for Brightness
                # Let's use an open hand (excluding thumb) to slide up/down, or pointer finger
                # Actually, requirement: "Vertical hand movement -> Control screen brightness". 
                # Let's say if all fingers are up (except maybe thumb), control brightness via wrist Y coordinate.
                elif sum(fingers[1:]) == 4:
                    wrist_y = lm_list[0][2]
                    # Map y from 100 (top of screen) to 400 (bottom of screen) reversed.
                    # Higher up (lower Y) -> higher brightness
                    target_bright = np.interp(wrist_y, [100, hCam - 100], [100, 0])
                    smooth_bright = bright_filter.update(target_bright)
                    controller.set_brightness(smooth_bright)
                    bright_bar = np.interp(smooth_bright, [0, 100], [400, 150])
                    cv2.circle(img, (lm_list[0][1], lm_list[0][2]), 15, (0, 255, 255), cv2.FILLED)

                # 3. Fist -> Play/Pause
                elif recognizer.detect_fist(fingers):
                    if controller.play_pause_media():
                        cv2.putText(img, "PLAY/PAUSE", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                # 4. Swipe -> Next/Prev track
                # Useful when changing tracks. Requires an open hand doing sideways swipe
                # Let's define swipe when index, middle, ring are up. Or just rely on standard detection.
                elif sum(fingers) >= 3: 
                    swipe_dir = recognizer.detect_swipe(lm_list)
                    if swipe_dir == 'right':
                        if controller.next_track():
                             cv2.putText(img, "NEXT TRACK", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                    elif swipe_dir == 'left':
                        if controller.prev_track():
                             cv2.putText(img, "PREV TRACK", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

                # 5. Peace Sign -> Screenshot
                elif recognizer.detect_peace(fingers):
                    if controller.take_screenshot():
                        cv2.putText(img, "SCREENSHOT!", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        # -- UI Rending --
        # Mode Status
        mode_text = "ACTIVE" if recognizer.is_active else "INACTIVE"
        mode_color = (0, 255, 0) if recognizer.is_active else (0, 0, 255)
        cv2.putText(img, f'State: {mode_text}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 3)

        # Volume Bar
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(current_vol)}%', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Brightness Bar
        cv2.rectangle(img, (wCam - 85, 150), (wCam - 50, 400), (0, 255, 255), 3)
        cv2.rectangle(img, (wCam - 85, int(bright_bar)), (wCam - 50, 400), (0, 255, 255), cv2.FILLED)
        cv2.putText(img, f'{int(current_bright)}%', (wCam - 90, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # FPS
        fps = fps_counter.update()
        cv2.putText(img, f'FPS: {int(fps)}', (20, hCam - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Show Output
        cv2.imshow("AirControl System", img)
        
        # Check if 'q' is pressed or if the window 'X' button was clicked
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("AirControl System", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

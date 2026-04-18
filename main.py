import cv2
import numpy as np
from hand_tracker import HandTracker
from gesture_logic import GestureRecognizer
from system_control import SystemController
from utils import SmoothFilter, FPSCounter, draw_neon_text, draw_futuristic_bar, draw_hud_background

def main():
    # Desired webcam dimensions
    wCam, hCam = 640, 480

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, wCam)
    cap.set(4, hCam)

    tracker = HandTracker(detection_con=0.8, track_con=0.8)
    recognizer = GestureRecognizer()
    controller = SystemController()

    fps_counter = FPSCounter()
    
    # Smooth filters for UI and Control
    vol_filter = SmoothFilter(alpha=0.3)
    bright_filter = SmoothFilter(alpha=0.2)

    bright_ref_y = None
    bright_ref_val = None

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame")
            break

        # Flip horizontally for selfie-view
        img = cv2.flip(img, 1)

        # 1. Detect hands on the clean image BEFORE applying the dark HUD tint
        # (MediaPipe struggles to see skin tones if the image is too dark/purple)
        tracker.find_hands(img, draw=False)

        # 2. Draw Futuristic Background over the feed
        draw_hud_background(img)

        # 3. Draw the neon hand landmarks ON TOP of the dark background
        if tracker.results and tracker.results.hand_landmarks:
            for hl in tracker.results.hand_landmarks:
                tracker.draw_landmarks(img, hl)

        lm_list = tracker.get_positions(img, draw=False)

        current_vol = controller.get_volume()
        current_bright = controller.get_brightness()

        vol_bar = np.interp(current_vol, [0, 100], [400, 150])
        bright_bar = np.interp(current_bright, [0, 100], [400, 150])

        if len(lm_list) != 0:
            fingers = tracker.fingers_up(lm_list)
            
            # Check for activation toggle
            toggled = recognizer.check_activation(fingers)
            
            # Reset the relative brightness anchor if not actively doing the brightness gesture
            if not (recognizer.is_active and sum(fingers[1:]) == 4):
                bright_ref_y = None
                
            if recognizer.is_active:
                
                # 1. Pinch for Volume
                # Only check if index and thumb are primary factors, 
                # but to avoid conflicts with swipe/fist let's check holding index/thumb out
                if fingers[1] == 1 and sum(fingers[2:]) == 0: 
                    distance, center = recognizer.detect_pinch(lm_list)
                    cv2.circle(img, center, 15, (255, 0, 255), cv2.FILLED)
                    cv2.circle(img, center, 20, (255, 255, 0), 2)
                    
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
                    
                    if bright_ref_y is None:
                        bright_ref_y = wrist_y
                        bright_ref_val = controller.get_brightness()
                        bright_filter.value = bright_ref_val
                        target_bright = bright_ref_val
                    else:
                        # Hand moving UP means smaller Y coordinate.
                        # So (bright_ref_y - wrist_y) is positive when moving UP.
                        delta_y = bright_ref_y - wrist_y
                        target_bright = np.clip(bright_ref_val + (delta_y * 0.6), 0, 100)
                    smooth_bright = bright_filter.update(target_bright)
                    controller.set_brightness(smooth_bright)
                    bright_bar = np.interp(smooth_bright, [0, 100], [400, 150])
                    cv2.circle(img, (lm_list[0][1], lm_list[0][2]), 15, (255, 255, 0), cv2.FILLED)
                    cv2.circle(img, (lm_list[0][1], lm_list[0][2]), 20, (255, 0, 255), 2)

                # 3. Fist -> Play/Pause
                elif recognizer.detect_fist(fingers):
                    if controller.play_pause_media():
                        draw_neon_text(img, "MEDIA TOGGLE", (wCam//2 - 80, 80), 0.8, 2, (255, 255, 255), (255, 50, 50))

                # 4. Swipe -> Next/Prev track
                # Useful when changing tracks. Requires an open hand doing sideways swipe
                # Let's define swipe when index, middle, ring are up. Or just rely on standard detection.
                elif sum(fingers) >= 3: 
                    swipe_dir = recognizer.detect_swipe(lm_list)
                    if swipe_dir == 'right':
                        if controller.next_track():
                             draw_neon_text(img, "NEXT TRACK ->", (wCam//2 - 80, 80), 0.8, 2, (255, 255, 255), (0, 255, 255))
                    elif swipe_dir == 'left':
                        if controller.prev_track():
                             draw_neon_text(img, "<- PREV TRACK", (wCam//2 - 80, 80), 0.8, 2, (255, 255, 255), (0, 255, 255))

                # 5. Peace Sign -> Screenshot
                elif recognizer.detect_peace(fingers):
                    if controller.take_screenshot():
                        draw_neon_text(img, "SCREENSHOT CAPTURED", (wCam//2 - 120, 80), 0.8, 2, (255, 255, 255), (50, 255, 50))

        # -- UI Rending --
        # Mode Status
        if recognizer.is_active:
            mode_text = "SYSTEM ACTIVE"
            mode_color = (255, 255, 0)
        elif recognizer.open_palm_start_time > 0:
            # Show activation progress
            import time
            elapsed = time.time() - recognizer.open_palm_start_time
            progress = min(100, int((elapsed / recognizer.activation_hold_time) * 100))
            mode_text = f"ACTIVATING: {progress}%"
            mode_color = (0, 165, 255) # Orange
        else:
            mode_text = "SYSTEM STANDBY"
            mode_color = (50, 50, 255)
        draw_neon_text(img, mode_text, (40, 50), 0.6, 1, (255, 255, 255), mode_color)

        # Volume Bar
        draw_futuristic_bar(img, 40, 150, 30, 200, current_vol, fill_color=(255, 0, 200), label=f'VOL {int(current_vol)}%')

        # Brightness Bar
        draw_futuristic_bar(img, wCam - 70, 150, 30, 200, current_bright, fill_color=(255, 255, 0), label=f'BRT {int(current_bright)}%')

        # FPS
        fps = fps_counter.update()
        draw_neon_text(img, f'FPS: {int(fps)}', (40, hCam - 30), 0.5, 1, (200, 200, 200), (100, 0, 150))

        # Show Output
        cv2.imshow("AirControl System", img)
        
        # Check if 'q' is pressed or if the window 'X' button was clicked
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("AirControl System", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

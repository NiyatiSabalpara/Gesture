from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import pyautogui
import numpy as np
import time

class SystemController:
    def __init__(self):
        # 1. Init volume control (pycaw)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Get volume range
        self.vol_range = self.volume.GetVolumeRange()
        self.min_vol = self.vol_range[0] # Usually -65.25
        self.max_vol = self.vol_range[1] # Usually 0.0

        # Delay tracking for media keys (prevent spamming)
        self.last_media_time = 0
        self.last_screenshot_time = 0
        self.cooldown = 1.0 # 1 second cooldown for key strokes
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False

    def set_volume(self, percentage):
        """
        Set Windows volume based on percentage (0-100).
        """
        vol = np.interp(percentage, [0, 100], [self.min_vol, self.max_vol])
        self.volume.SetMasterVolumeLevel(vol, None)
        
    def get_volume(self):
        """
        Get current system volume as percentage.
        """
        vol = self.volume.GetMasterVolumeLevel()
        return np.interp(vol, [self.min_vol, self.max_vol], [0, 100])

    def set_brightness(self, percentage):
        """
        Set display brightness (0-100).
        """
        percentage = max(0, min(100, percentage))
        try:
            sbc.set_brightness(int(percentage))
        except Exception as e:
            # Handle situations where brightness can't be controlled (e.g. desktop monitors)
            pass

    def get_brightness(self):
        """
        Get current display brightness.
        """
        try:
            b = sbc.get_brightness()
            if isinstance(b, list): 
                return b[0]
            return b
        except:
            return 100

    def play_pause_media(self):
        if time.time() - self.last_media_time > self.cooldown:
            pyautogui.press('playpause')
            self.last_media_time = time.time()
            return True
        return False

    def next_track(self):
        if time.time() - self.last_media_time > self.cooldown:
            pyautogui.press('nexttrack')
            self.last_media_time = time.time()
            return True
        return False

    def prev_track(self):
        if time.time() - self.last_media_time > self.cooldown:
            pyautogui.press('prevtrack')
            self.last_media_time = time.time()
            return True
        return False

    def take_screenshot(self):
        if time.time() - self.last_screenshot_time > self.cooldown:
            pyautogui.press('printscreen')
            self.last_screenshot_time = time.time()
            return True
        return False

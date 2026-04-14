# AirControl: Touchless Gesture-Based System Interface

AirControl is a computer vision project that leverages OpenCV and MediaPipe Tasks API to detect real-time hand gestures via your webcam and map them to OS-level functions.

## Capabilities

| Gesture | Action | Instructions |
| --- | --- | --- |
| **Open Palm hold (2s)** | Toggle State (Activate/Deactivate) | Hold up an open hand for 2 seconds. The upper-left state will switch. |
| **Thumb + Index Pinch** | Set System Volume | While Active, pinch your thumb and index finger together. Distance sets 0-100% volume. |
| **Vertical Hand Slide** | Set Screen Brightness | Keep 4 fingers up (thumb down) and move your hand vertically across the camera frame. |
| **Closed Fist** | Play / Pause Media | Form a hard fist (0 fingers visible). |
| **Horizontal Swipe** | Next / Previous Track | With an open hand, swipe swiftly left or right. |
| **Peace Sign** | Take Screenshot | Index and Middle fingers up, other fingers down. |

## Running the Application

### 1. Prerequisites
Ensure you have Python installed. The project runs seamlessly on modern Python versions (including Python 3.13).

### 2. Install Dependencies
Open your terminal in the project directory and run:

    pip install -r requirements.txt

### 3. Start the Project
To launch the webcam interface and initialize gesture controls, run:

    python main.py

To gracefully stop the application, ensure the camera preview window is focused, and press the `q` key on your keyboard. Alternatively, you can press `Ctrl + C` in the terminal window.

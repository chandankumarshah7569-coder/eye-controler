#!/usr/bin/env python
"""
Eye Blink Controlled Video Scroller
Detects eye blinks using MediaPipe and scrolls videos automatically
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Eye landmark indices for MediaPipe Face Mesh
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

class BlinkDetector:
    def __init__(self):
        self.ear_threshold = 0.21  # Eye Aspect Ratio threshold for blink
        self.blink_frames = 2  # Consecutive frames below threshold to confirm blink
        self.intentional_blink_duration = 0.3  # seconds for intentional blink
        self.scroll_cooldown = 1.5  # seconds between scrolls
        
        self.left_blink_counter = 0
        self.right_blink_counter = 0
        self.both_blink_counter = 0
        self.last_scroll_time = 0
        self.blink_start_time = None
        self.last_blink_state = False
        
        # Track recent blinks for double blink detection
        self.recent_blinks = deque(maxlen=2)
        self.double_blink_window = 0.5  # seconds
        
    def calculate_ear(self, eye_landmarks):
        """Calculate Eye Aspect Ratio"""
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR formula
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def get_eye_landmarks(self, landmarks, eye_indices, frame_width, frame_height):
        """Extract eye landmark coordinates"""
        coords = []
        for idx in eye_indices:
            landmark = landmarks[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            coords.append([x, y])
        return np.array(coords)
    
    def detect_wink(self, left_ear, right_ear):
        """Detect left or right eye wink"""
        wink_threshold = 0.19
        open_threshold = 0.25
        
        # Left eye wink (left closed, right open)
        if left_ear < wink_threshold and right_ear > open_threshold:
            return "left"
        # Right eye wink (right closed, left open)
        elif right_ear < wink_threshold and left_ear > open_threshold:
            return "right"
        return None
    
    def process_frame(self, frame, face_landmarks):
        """Process frame and detect blinks/winks"""
        h, w, _ = frame.shape
        current_time = time.time()
        
        # Get eye landmarks
        left_eye = self.get_eye_landmarks(face_landmarks.landmark, LEFT_EYE, w, h)
        right_eye = self.get_eye_landmarks(face_landmarks.landmark, RIGHT_EYE, w, h)
        
        # Calculate EAR for both eyes
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Draw eye landmarks
        for point in left_eye:
            cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
        for point in right_eye:
            cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
        
        # Display EAR values
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        action = None
        
        # Check for winks first
        wink = self.detect_wink(left_ear, right_ear)
        if wink and (current_time - self.last_scroll_time) > 0.5:
            if wink == "left":
                action = "like"
                cv2.putText(frame, "LEFT WINK - LIKE!", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif wink == "right":
                action = "pause"
                cv2.putText(frame, "RIGHT WINK - PAUSE/PLAY!", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            self.last_scroll_time = current_time
            return frame, action
        
        # Detect blink
        is_blinking = avg_ear < self.ear_threshold
        
        if is_blinking and not self.last_blink_state:
            # Blink started
            self.blink_start_time = current_time
            self.both_blink_counter += 1
        elif not is_blinking and self.last_blink_state and self.blink_start_time:
            # Blink ended
            blink_duration = current_time - self.blink_start_time
            
            # Check cooldown
            if (current_time - self.last_scroll_time) > self.scroll_cooldown:
                # Record blink time for double blink detection
                self.recent_blinks.append(current_time)
                
                # Check for double blink
                if len(self.recent_blinks) == 2:
                    time_between_blinks = self.recent_blinks[1] - self.recent_blinks[0]
                    if time_between_blinks < self.double_blink_window:
                        action = "scroll_up"
                        cv2.putText(frame, "DOUBLE BLINK - SCROLL UP!", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        self.last_scroll_time = current_time
                        self.recent_blinks.clear()
                        self.blink_start_time = None
                        self.last_blink_state = is_blinking
                        return frame, action
                
                # Regular blink - scroll down
                if blink_duration >= self.intentional_blink_duration:
                    action = "scroll_down"
                    cv2.putText(frame, "BLINK DETECTED - SCROLLING!", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.last_scroll_time = current_time
            
            self.blink_start_time = None
        
        self.last_blink_state = is_blinking
        
        # Display blink status
        if is_blinking:
            cv2.putText(frame, "BLINKING", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, action

def main():
    print("=== Eye Blink Video Scroller ===")
    print("Controls:")
    print("- Single blink (hold 0.3s): Scroll down to next video")
    print("- Double blink: Scroll up to previous video")
    print("- Wink left eye: Like the video")
    print("- Wink right eye: Pause/Play")
    print("- Press 'q' to quit")
    print("\nStarting webcam...")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Initialize blink detector
    detector = BlinkDetector()
    
    # Initialize MediaPipe Face Mesh
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to read from webcam")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Process frame and detect actions
                frame, action = detector.process_frame(frame, face_landmarks)
                
                # Execute actions
                if action == "scroll_down":
                    pyautogui.press('down')
                    print("Action: Scrolled down")
                elif action == "scroll_up":
                    pyautogui.press('up')
                    print("Action: Scrolled up")
                elif action == "like":
                    pyautogui.press('l')  # Common like shortcut
                    print("Action: Liked video")
                elif action == "pause":
                    pyautogui.press('space')  # Common pause/play shortcut
                    print("Action: Pause/Play")
            else:
                cv2.putText(frame, "No face detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display frame
            cv2.imshow('Eye Blink Video Scroller', frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed")

if __name__ == "__main__":
    main()

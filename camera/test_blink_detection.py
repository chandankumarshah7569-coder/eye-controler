"""
Simple Eye Blink Detection Test - Terminal Output Only
No scrolling, just prints detection events
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Eye landmark indices
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

class BlinkDetector:
    def __init__(self):
        self.ear_threshold = 0.21
        self.intentional_blink_duration = 0.3
        self.cooldown = 1.5
        
        self.last_action_time = 0
        self.blink_start_time = None
        self.last_blink_state = False
        self.recent_blinks = deque(maxlen=2)
        self.double_blink_window = 0.5
        
    def calculate_ear(self, eye_landmarks):
        """Calculate Eye Aspect Ratio"""
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (v1 + v2) / (2.0 * h)
    
    def get_eye_landmarks(self, landmarks, eye_indices, w, h):
        """Extract eye coordinates"""
        coords = []
        for idx in eye_indices:
            landmark = landmarks[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            coords.append([x, y])
        return np.array(coords)
    
    def detect_wink(self, left_ear, right_ear):
        """Detect wink"""
        wink_threshold = 0.19
        open_threshold = 0.25
        
        if left_ear < wink_threshold and right_ear > open_threshold:
            return "left"
        elif right_ear < wink_threshold and left_ear > open_threshold:
            return "right"
        return None
    
    def process(self, landmarks, w, h):
        """Process and detect blinks/winks"""
        current_time = time.time()
        
        # Get eye landmarks
        left_eye = self.get_eye_landmarks(landmarks, LEFT_EYE, w, h)
        right_eye = self.get_eye_landmarks(landmarks, RIGHT_EYE, w, h)
        
        # Calculate EAR
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        action = None
        
        # Check for winks
        wink = self.detect_wink(left_ear, right_ear)
        if wink and (current_time - self.last_action_time) > 0.5:
            action = f"wink_{wink}"
            self.last_action_time = current_time
            return avg_ear, left_ear, right_ear, action
        
        # Detect blink
        is_blinking = avg_ear < self.ear_threshold
        
        if is_blinking and not self.last_blink_state:
            self.blink_start_time = current_time
        elif not is_blinking and self.last_blink_state and self.blink_start_time:
            blink_duration = current_time - self.blink_start_time
            
            if (current_time - self.last_action_time) > self.cooldown:
                self.recent_blinks.append(current_time)
                
                # Check double blink
                if len(self.recent_blinks) == 2:
                    time_between = self.recent_blinks[1] - self.recent_blinks[0]
                    if time_between < self.double_blink_window:
                        action = "double_blink"
                        self.last_action_time = current_time
                        self.recent_blinks.clear()
                        self.blink_start_time = None
                        self.last_blink_state = is_blinking
                        return avg_ear, left_ear, right_ear, action
                
                # Regular blink
                if blink_duration >= self.intentional_blink_duration:
                    action = "single_blink"
                    self.last_action_time = current_time
            
            self.blink_start_time = None
        
        self.last_blink_state = is_blinking
        return avg_ear, left_ear, right_ear, action

def main():
    print("=" * 60)
    print("EYE BLINK DETECTION TEST - TERMINAL OUTPUT ONLY")
    print("=" * 60)
    print("\nDetection Events:")
    print("  - Single blink (hold 0.3s) -> 'SCROLL DOWN'")
    print("  - Double blink -> 'SCROLL UP'")
    print("  - Wink left eye -> 'LIKE'")
    print("  - Wink right eye -> 'PAUSE/PLAY'")
    print("\nPress 'q' in the video window to quit\n")
    print("-" * 60)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam")
        return
    
    detector = BlinkDetector()
    
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        
        frame_count = 0
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                avg_ear, left_ear, right_ear, action = detector.process(
                    face_landmarks.landmark, w, h
                )
                
                # Display EAR on frame
                cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Print action to terminal
                if action == "single_blink":
                    print(f"[{time.strftime('%H:%M:%S')}] >>> SCROLL DOWN (Single Blink)")
                elif action == "double_blink":
                    print(f"[{time.strftime('%H:%M:%S')}] >>> SCROLL UP (Double Blink)")
                elif action == "wink_left":
                    print(f"[{time.strftime('%H:%M:%S')}] >>> LIKE (Left Wink)")
                elif action == "wink_right":
                    print(f"[{time.strftime('%H:%M:%S')}] >>> PAUSE/PLAY (Right Wink)")
                
                # Show status every 30 frames
                if frame_count % 30 == 0:
                    status = "BLINKING" if avg_ear < detector.ear_threshold else "OPEN"
                    print(f"[Monitor] EAR: {avg_ear:.3f} | L: {left_ear:.3f} | R: {right_ear:.3f} | {status}")
                
                # Draw eyes on frame
                for idx in LEFT_EYE + RIGHT_EYE:
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                
                cv2.putText(frame, "Face Detected", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No Face Detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Blink Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n" + "-" * 60)
    print("Test completed. Application closed.")

if __name__ == "__main__":
    main()

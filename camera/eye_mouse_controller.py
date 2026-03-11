"""
Eye & Hand Gesture Mouse Controller
Control mouse with eye gaze and hand gestures
"""

import tkinter as tk
from tkinter import messagebox
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading
from PIL import Image, ImageTk
from collections import deque

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False

# Eye landmark indices
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

class MouseController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.smoothing = 5
        self.mouse_positions = deque(maxlen=self.smoothing)
        
        # Blink detection
        self.ear_threshold = 0.21
        self.last_blink_state = False
        self.blink_start_time = None
        self.recent_blinks = deque(maxlen=2)
        self.double_blink_window = 0.5
        self.last_click_time = 0
        self.click_cooldown = 0.5
        
        # Statistics
        self.stats = {
            'left_clicks': 0,
            'right_clicks': 0,
            'scrolls_up': 0,
            'scrolls_down': 0
        }
    
    def calculate_ear(self, eye_landmarks):
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (v1 + v2) / (2.0 * h)
    
    def get_landmarks(self, landmarks, indices, w, h):
        coords = []
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            coords.append([x, y])
        return np.array(coords)
    
    def get_gaze_position(self, landmarks, w, h):
        """Calculate gaze position from iris landmarks"""
        left_iris = self.get_landmarks(landmarks, LEFT_IRIS, w, h)
        right_iris = self.get_landmarks(landmarks, RIGHT_IRIS, w, h)
        
        # Get center of both irises
        left_center = np.mean(left_iris, axis=0)
        right_center = np.mean(right_iris, axis=0)
        gaze_center = (left_center + right_center) / 2
        
        # Map to screen coordinates
        screen_x = int(np.interp(gaze_center[0], [w * 0.3, w * 0.7], [0, self.screen_w]))
        screen_y = int(np.interp(gaze_center[1], [h * 0.3, h * 0.7], [0, self.screen_h]))
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        return screen_x, screen_y
    
    def smooth_mouse_position(self, x, y):
        """Apply smoothing to mouse movement"""
        self.mouse_positions.append((x, y))
        if len(self.mouse_positions) > 0:
            avg_x = int(np.mean([pos[0] for pos in self.mouse_positions]))
            avg_y = int(np.mean([pos[1] for pos in self.mouse_positions]))
            return avg_x, avg_y
        return x, y
    
    def detect_blink(self, landmarks, w, h):
        """Detect single and double blinks"""
        current_time = time.time()
        
        left_eye = self.get_landmarks(landmarks, LEFT_EYE, w, h)
        right_eye = self.get_landmarks(landmarks, RIGHT_EYE, w, h)
        
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        is_blinking = avg_ear < self.ear_threshold
        action = None
        
        if is_blinking and not self.last_blink_state:
            self.blink_start_time = current_time
        elif not is_blinking and self.last_blink_state and self.blink_start_time:
            if (current_time - self.last_click_time) > self.click_cooldown:
                self.recent_blinks.append(current_time)
                
                if len(self.recent_blinks) == 2:
                    time_between = self.recent_blinks[1] - self.recent_blinks[0]
                    if time_between < self.double_blink_window:
                        action = "right_click"
                        self.stats['right_clicks'] += 1
                        self.last_click_time = current_time
                        self.recent_blinks.clear()
                        self.blink_start_time = None
                        self.last_blink_state = is_blinking
                        return avg_ear, action
                
                action = "left_click"
                self.stats['left_clicks'] += 1
                self.last_click_time = current_time
            
            self.blink_start_time = None
        
        self.last_blink_state = is_blinking
        return avg_ear, action

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
    
    def detect_finger_direction(self, hand_landmarks):
        """Detect if finger is pointing up or down"""
        if not hand_landmarks:
            return None
        
        # Get index finger tip and base
        index_tip = hand_landmarks.landmark[8]
        index_base = hand_landmarks.landmark[5]
        wrist = hand_landmarks.landmark[0]
        
        # Check if index finger is extended
        finger_length = abs(index_tip.y - index_base.y)
        
        if finger_length > 0.1:  # Finger is extended
            if index_tip.y < wrist.y - 0.1:
                return "up"
            elif index_tip.y > wrist.y + 0.1:
                return "down"
        
        return None

class MouseControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye & Gesture Mouse Controller")
        self.root.geometry("1100x750")
        self.root.configure(bg='#1e1e1e')
        
        self.is_running = False
        self.cap = None
        self.mouse_controller = None
        self.gesture_detector = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header.pack(fill='x', padx=10, pady=10)
        
        title = tk.Label(header, text="🖱️ Eye & Gesture Mouse Controller", 
                        font=('Arial', 18, 'bold'), bg='#2d2d2d', fg='#00ff88')
        title.pack(side='left', padx=20, pady=10)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel
        left_panel = tk.Frame(main_container, bg='#2d2d2d')
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(left_panel, text="Video Feed", 
                font=('Arial', 14, 'bold'), bg='#2d2d2d', fg='white').pack(pady=10)
        
        self.video_canvas = tk.Label(left_panel, bg='black')
        self.video_canvas.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Right panel
        right_panel = tk.Frame(main_container, bg='#2d2d2d', width=320)
        right_panel.pack(side='right', fill='y', padx=5)
        right_panel.pack_propagate(False)
        
        # Controls
        control_frame = tk.Frame(right_panel, bg='#2d2d2d')
        control_frame.pack(pady=20, padx=20, fill='x')
        
        self.start_btn = tk.Button(control_frame, text="▶️ START MOUSE CONTROL", 
                                   command=self.start_controller,
                                   font=('Arial', 12, 'bold'), bg='#00ff88', fg='black',
                                   relief='flat', padx=20, pady=15)
        self.start_btn.pack(fill='x', pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP", 
                                  command=self.stop_controller,
                                  font=('Arial', 12, 'bold'), bg='#ff4444', fg='white',
                                  relief='flat', padx=20, pady=15, state='disabled')
        self.stop_btn.pack(fill='x', pady=5)
        
        # Status
        status_frame = tk.LabelFrame(right_panel, text="Status", 
                                    font=('Arial', 11, 'bold'),
                                    bg='#2d2d2d', fg='white', padx=10, pady=10)
        status_frame.pack(pady=10, padx=20, fill='x')
        
        self.status_label = tk.Label(status_frame, text="⚫ Stopped", 
                                     font=('Arial', 10), bg='#2d2d2d', fg='#ff4444')
        self.status_label.pack()
        
        self.ear_label = tk.Label(status_frame, text="EAR: --", 
                                  font=('Arial', 9), bg='#2d2d2d', fg='white')
        self.ear_label.pack(pady=3)
        
        # Statistics
        stats_frame = tk.LabelFrame(right_panel, text="Statistics", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#2d2d2d', fg='white', padx=10, pady=10)
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        self.stats_labels = {}
        stats_items = [
            ('left_clicks', '🖱️ Left Clicks'),
            ('right_clicks', '🖱️ Right Clicks'),
            ('scrolls_up', '⬆️ Scrolls Up'),
            ('scrolls_down', '⬇️ Scrolls Down')
        ]
        
        for key, label in stats_items:
            frame = tk.Frame(stats_frame, bg='#2d2d2d')
            frame.pack(fill='x', pady=2)
            tk.Label(frame, text=label, font=('Arial', 9), 
                    bg='#2d2d2d', fg='white').pack(side='left')
            self.stats_labels[key] = tk.Label(frame, text="0", 
                                             font=('Arial', 9, 'bold'),
                                             bg='#2d2d2d', fg='#00ff88')
            self.stats_labels[key].pack(side='right')
        
        # Instructions
        inst_frame = tk.LabelFrame(right_panel, text="Controls", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#2d2d2d', fg='white', padx=10, pady=10)
        inst_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        instructions = [
            "👁️ Move eyes: Move cursor",
            "👁️ Single blink: Left click",
            "👁️👁️ Double blink: Right click",
            "☝️ Point finger up: Scroll up",
            "👇 Point finger down: Scroll down"
        ]
        
        for inst in instructions:
            tk.Label(inst_frame, text=inst, font=('Arial', 9), 
                    bg='#2d2d2d', fg='white', anchor='w').pack(fill='x', pady=3)

    
    def start_controller(self):
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam!")
            return
        
        self.mouse_controller = MouseController()
        self.gesture_detector = GestureDetector()
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="🟢 Running", fg='#00ff88')
        
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()
    
    def stop_controller(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⚫ Stopped", fg='#ff4444')
        self.video_canvas.config(image='', bg='black')

    
    def control_loop(self):
        mp_face_mesh = mp.solutions.face_mesh
        mp_hands = mp.solutions.hands
        
        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh, mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands:
            
            while self.is_running:
                success, frame = self.cap.read()
                if not success:
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_results = face_mesh.process(rgb_frame)
                hand_results = hands.process(rgb_frame)
                
                # Process face for eye tracking and blinks
                if face_results.multi_face_landmarks:
                    face_landmarks = face_results.multi_face_landmarks[0]
                    
                    # Get gaze position and move mouse
                    screen_x, screen_y = self.mouse_controller.get_gaze_position(
                        face_landmarks.landmark, w, h
                    )
                    smooth_x, smooth_y = self.mouse_controller.smooth_mouse_position(
                        screen_x, screen_y
                    )
                    pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                    
                    # Detect blinks for clicks
                    avg_ear, action = self.mouse_controller.detect_blink(
                        face_landmarks.landmark, w, h
                    )
                    
                    if action == "left_click":
                        pyautogui.click()
                    elif action == "right_click":
                        pyautogui.rightClick()
                    
                    # Update UI
                    self.root.after(0, self.ear_label.config, 
                                   {'text': f"EAR: {avg_ear:.3f}"})
                    
                    # Draw iris landmarks
                    for idx in LEFT_IRIS + RIGHT_IRIS:
                        landmark = face_landmarks.landmark[idx]
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
                
                # Process hand gestures for scrolling
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        # Draw hand landmarks
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                        )
                        
                        # Detect gesture
                        current_time = time.time()
                        if (current_time - self.gesture_detector.last_gesture_time) > \
                           self.gesture_detector.gesture_cooldown:
                            
                            direction = self.gesture_detector.detect_finger_direction(
                                hand_landmarks
                            )
                            
                            if direction == "up":
                                pyautogui.scroll(3)
                                self.mouse_controller.stats['scrolls_up'] += 1
                                self.gesture_detector.last_gesture_time = current_time
                                cv2.putText(frame, "SCROLL UP", (10, 60),
                                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            elif direction == "down":
                                pyautogui.scroll(-3)
                                self.mouse_controller.stats['scrolls_down'] += 1
                                self.gesture_detector.last_gesture_time = current_time
                                cv2.putText(frame, "SCROLL DOWN", (10, 60),
                                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Update stats
                for key, label in self.stats_labels.items():
                    self.root.after(0, label.config, 
                                   {'text': str(self.mouse_controller.stats[key])})
                
                # Display frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (720, 540))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.root.after(0, self.video_canvas.config, {'image': imgtk})
                self.video_canvas.imgtk = imgtk
                
                time.sleep(0.01)

def main():
    root = tk.Tk()
    app = MouseControllerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

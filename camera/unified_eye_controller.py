"""
Unified Eye Controller - Switch between Video Scroll and Mouse Control modes
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

class EyeController:
    def __init__(self, mode="video_scroll"):
        self.mode = mode
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Common settings
        self.ear_threshold = 0.21
        self.last_blink_state = False
        self.blink_start_time = None
        self.recent_blinks = deque(maxlen=2)
        self.double_blink_window = 0.5
        self.last_action_time = 0
        
        # Mode-specific settings
        if mode == "video_scroll":
            self.cooldown = 1.5
            self.blink_duration = 0.3
        else:  # mouse_control
            self.cooldown = 0.5
            self.blink_duration = 0.1
            self.smoothing = 5
            self.mouse_positions = deque(maxlen=self.smoothing)
        
        # Statistics
        self.stats = {
            'single_blinks': 0,
            'double_blinks': 0,
            'left_winks': 0,
            'right_winks': 0,
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
    
    def detect_wink(self, left_ear, right_ear):
        wink_threshold = 0.19
        open_threshold = 0.25
        
        if left_ear < wink_threshold and right_ear > open_threshold:
            return "left"
        elif right_ear < wink_threshold and left_ear > open_threshold:
            return "right"
        return None
    
    def get_gaze_position(self, landmarks, w, h):
        """Calculate gaze position for mouse control"""
        left_iris = self.get_landmarks(landmarks, LEFT_IRIS, w, h)
        right_iris = self.get_landmarks(landmarks, RIGHT_IRIS, w, h)
        
        left_center = np.mean(left_iris, axis=0)
        right_center = np.mean(right_iris, axis=0)
        gaze_center = (left_center + right_center) / 2
        
        # Map to screen coordinates with better calibration
        screen_x = int(np.interp(gaze_center[0], [w * 0.25, w * 0.75], [0, self.screen_w]))
        screen_y = int(np.interp(gaze_center[1], [h * 0.25, h * 0.75], [0, self.screen_h]))
        
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        return screen_x, screen_y
    
    def smooth_mouse_position(self, x, y):
        self.mouse_positions.append((x, y))
        if len(self.mouse_positions) > 0:
            avg_x = int(np.mean([pos[0] for pos in self.mouse_positions]))
            avg_y = int(np.mean([pos[1] for pos in self.mouse_positions]))
            return avg_x, avg_y
        return x, y
    
    def process(self, landmarks, w, h):
        current_time = time.time()
        
        left_eye = self.get_landmarks(landmarks, LEFT_EYE, w, h)
        right_eye = self.get_landmarks(landmarks, RIGHT_EYE, w, h)
        
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        action = None
        mouse_pos = None
        
        # Mouse control mode - get gaze position
        if self.mode == "mouse_control":
            mouse_pos = self.get_gaze_position(landmarks, w, h)
        
        # Check for winks (only in video_scroll mode)
        if self.mode == "video_scroll":
            wink = self.detect_wink(left_ear, right_ear)
            if wink and (current_time - self.last_action_time) > 0.5:
                action = f"wink_{wink}"
                self.stats[f'{wink}_winks'] += 1
                self.last_action_time = current_time
                return avg_ear, left_eye, right_eye, action, mouse_pos
        
        # Detect blinks
        is_blinking = avg_ear < self.ear_threshold
        
        if is_blinking and not self.last_blink_state:
            self.blink_start_time = current_time
        elif not is_blinking and self.last_blink_state and self.blink_start_time:
            blink_duration = current_time - self.blink_start_time
            
            if (current_time - self.last_action_time) > self.cooldown:
                self.recent_blinks.append(current_time)
                
                # Check for double blink
                if len(self.recent_blinks) == 2:
                    time_between = self.recent_blinks[1] - self.recent_blinks[0]
                    if time_between < self.double_blink_window:
                        if self.mode == "video_scroll":
                            action = "double_blink"
                            self.stats['double_blinks'] += 1
                        else:  # mouse_control
                            action = "right_click"
                            self.stats['right_clicks'] += 1
                        
                        self.last_action_time = current_time
                        self.recent_blinks.clear()
                        self.blink_start_time = None
                        self.last_blink_state = is_blinking
                        return avg_ear, left_eye, right_eye, action, mouse_pos
                
                # Single blink
                if blink_duration >= self.blink_duration:
                    if self.mode == "video_scroll":
                        action = "single_blink"
                        self.stats['single_blinks'] += 1
                    else:  # mouse_control
                        action = "left_click"
                        self.stats['left_clicks'] += 1
                    
                    self.last_action_time = current_time
            
            self.blink_start_time = None
        
        self.last_blink_state = is_blinking
        return avg_ear, left_eye, right_eye, action, mouse_pos

class GestureDetector:
    def __init__(self):
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
    
    def detect_finger_direction(self, hand_landmarks):
        if not hand_landmarks:
            return None
        
        index_tip = hand_landmarks.landmark[8]
        index_base = hand_landmarks.landmark[5]
        wrist = hand_landmarks.landmark[0]
        
        finger_length = abs(index_tip.y - index_base.y)
        
        if finger_length > 0.1:
            if index_tip.y < wrist.y - 0.1:
                return "up"
            elif index_tip.y > wrist.y + 0.1:
                return "down"
        
        return None

class UnifiedEyeControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unified Eye Controller")
        self.root.geometry("1100x750")
        self.root.configure(bg='#1e1e1e')
        
        self.is_running = False
        self.current_mode = "video_scroll"
        self.cap = None
        self.controller = None
        self.gesture_detector = None
        
        self.setup_ui()

    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#2d2d2d', height=70)
        header.pack(fill='x', padx=10, pady=10)
        
        title = tk.Label(header, text="👁️ Unified Eye Controller", 
                        font=('Arial', 20, 'bold'), bg='#2d2d2d', fg='#00ff88')
        title.pack(side='left', padx=20, pady=10)
        
        # Mode selector
        mode_frame = tk.Frame(header, bg='#2d2d2d')
        mode_frame.pack(side='right', padx=20)
        
        tk.Label(mode_frame, text="Mode:", font=('Arial', 11), 
                bg='#2d2d2d', fg='white').pack(side='left', padx=5)
        
        self.mode_var = tk.StringVar(value="video_scroll")
        
        self.video_mode_btn = tk.Radiobutton(
            mode_frame, text="📱 Video Scroll", variable=self.mode_var,
            value="video_scroll", command=self.switch_mode,
            font=('Arial', 11, 'bold'), bg='#2d2d2d', fg='white',
            selectcolor='#00ff88', activebackground='#2d2d2d',
            activeforeground='white', indicatoron=False,
            padx=15, pady=8, relief='raised'
        )
        self.video_mode_btn.pack(side='left', padx=3)
        
        self.mouse_mode_btn = tk.Radiobutton(
            mode_frame, text="🖱️ Mouse Control", variable=self.mode_var,
            value="mouse_control", command=self.switch_mode,
            font=('Arial', 11, 'bold'), bg='#2d2d2d', fg='white',
            selectcolor='#ff8800', activebackground='#2d2d2d',
            activeforeground='white', indicatoron=False,
            padx=15, pady=8, relief='raised'
        )
        self.mouse_mode_btn.pack(side='left', padx=3)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Video feed
        left_panel = tk.Frame(main_container, bg='#2d2d2d')
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        self.mode_label = tk.Label(left_panel, text="📱 VIDEO SCROLL MODE", 
                                   font=('Arial', 14, 'bold'), bg='#2d2d2d', fg='#00ff88')
        self.mode_label.pack(pady=10)
        
        self.video_canvas = tk.Label(left_panel, bg='black')
        self.video_canvas.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Right panel - Controls
        right_panel = tk.Frame(main_container, bg='#2d2d2d', width=320)
        right_panel.pack(side='right', fill='y', padx=5)
        right_panel.pack_propagate(False)
        
        # Control buttons
        control_frame = tk.Frame(right_panel, bg='#2d2d2d')
        control_frame.pack(pady=20, padx=20, fill='x')
        
        self.start_btn = tk.Button(control_frame, text="▶️ START", 
                                   command=self.start_controller,
                                   font=('Arial', 14, 'bold'), bg='#00ff88', fg='black',
                                   relief='flat', padx=30, pady=15)
        self.start_btn.pack(fill='x', pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP", 
                                  command=self.stop_controller,
                                  font=('Arial', 14, 'bold'), bg='#ff4444', fg='white',
                                  relief='flat', padx=30, pady=15, state='disabled')
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
        self.stats_frames = {}
        
        # Video scroll stats
        self.video_stats = [
            ('single_blinks', '⬇️ Scrolls Down'),
            ('double_blinks', '⬆️ Scrolls Up'),
            ('left_winks', '❤️ Likes'),
            ('right_winks', '⏸️ Pause/Play')
        ]
        
        # Mouse control stats
        self.mouse_stats = [
            ('left_clicks', '🖱️ Left Clicks'),
            ('right_clicks', '🖱️ Right Clicks'),
            ('scrolls_up', '⬆️ Scrolls Up'),
            ('scrolls_down', '⬇️ Scrolls Down')
        ]
        
        for key, label in self.video_stats + self.mouse_stats:
            frame = tk.Frame(stats_frame, bg='#2d2d2d')
            self.stats_frames[key] = frame
            tk.Label(frame, text=label, font=('Arial', 9), 
                    bg='#2d2d2d', fg='white').pack(side='left')
            self.stats_labels[key] = tk.Label(frame, text="0", 
                                             font=('Arial', 9, 'bold'),
                                             bg='#2d2d2d', fg='#00ff88')
            self.stats_labels[key].pack(side='right')
        
        # Instructions
        self.inst_frame = tk.LabelFrame(right_panel, text="Controls", 
                                       font=('Arial', 11, 'bold'),
                                       bg='#2d2d2d', fg='white', padx=10, pady=10)
        self.inst_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.instruction_labels = []
        
        # Update UI for initial mode
        self.update_mode_ui()
    
    def update_mode_ui(self):
        """Update UI based on current mode"""
        # Clear instruction labels
        for label in self.instruction_labels:
            label.destroy()
        self.instruction_labels.clear()
        
        # Hide all stat frames
        for frame in self.stats_frames.values():
            frame.pack_forget()
        
        if self.current_mode == "video_scroll":
            self.mode_label.config(text="📱 VIDEO SCROLL MODE", fg='#00ff88')
            
            # Show video scroll stats
            for key, _ in self.video_stats:
                self.stats_frames[key].pack(fill='x', pady=2)
            
            # Video scroll instructions
            instructions = [
                "👁️ Hold blink 0.3s: Scroll down",
                "👁️👁️ Double blink: Scroll up",
                "😉 Wink left: Like video",
                "😉 Wink right: Pause/Play"
            ]
        else:  # mouse_control
            self.mode_label.config(text="🖱️ MOUSE CONTROL MODE", fg='#ff8800')
            
            # Show mouse control stats
            for key, _ in self.mouse_stats:
                self.stats_frames[key].pack(fill='x', pady=2)
            
            # Mouse control instructions
            instructions = [
                "👁️ Move eyes: Move cursor",
                "👁️ Single blink: Left click",
                "👁️👁️ Double blink: Right click",
                "☝️ Point up: Scroll up",
                "👇 Point down: Scroll down"
            ]
        
        for inst in instructions:
            label = tk.Label(self.inst_frame, text=inst, font=('Arial', 9), 
                           bg='#2d2d2d', fg='white', anchor='w')
            label.pack(fill='x', pady=3)
            self.instruction_labels.append(label)
    
    def switch_mode(self):
        """Switch between video scroll and mouse control modes"""
        new_mode = self.mode_var.get()
        
        if self.is_running:
            response = messagebox.askyesno(
                "Switch Mode",
                "Stop current session and switch mode?"
            )
            if response:
                self.stop_controller()
                self.current_mode = new_mode
                self.update_mode_ui()
        else:
            self.current_mode = new_mode
            self.update_mode_ui()

    
    def start_controller(self):
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam!")
            return
        
        self.controller = EyeController(mode=self.current_mode)
        
        if self.current_mode == "mouse_control":
            self.gesture_detector = GestureDetector()
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="🟢 Running", fg='#00ff88')
        
        # Disable mode switching while running
        self.video_mode_btn.config(state='disabled')
        self.mouse_mode_btn.config(state='disabled')
        
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
        
        # Enable mode switching
        self.video_mode_btn.config(state='normal')
        self.mouse_mode_btn.config(state='normal')
    
    def control_loop(self):
        mp_face_mesh = mp.solutions.face_mesh
        mp_hands = mp.solutions.hands if self.current_mode == "mouse_control" else None
        
        face_mesh_context = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        hands_context = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) if mp_hands else None
        
        with face_mesh_context as face_mesh:
            if hands_context:
                with hands_context as hands:
                    self._process_frames(face_mesh, hands)
            else:
                self._process_frames(face_mesh, None)
    
    def _process_frames(self, face_mesh, hands):
        while self.is_running:
            success, frame = self.cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = face_mesh.process(rgb_frame)
            hand_results = hands.process(rgb_frame) if hands else None
            
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                
                avg_ear, left_eye, right_eye, action, mouse_pos = \
                    self.controller.process(face_landmarks.landmark, w, h)
                
                # Draw eye landmarks
                for point in left_eye:
                    cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
                for point in right_eye:
                    cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
                
                # Mouse control mode
                if self.current_mode == "mouse_control" and mouse_pos:
                    smooth_x, smooth_y = self.controller.smooth_mouse_position(
                        mouse_pos[0], mouse_pos[1]
                    )
                    pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                    
                    # Draw iris landmarks
                    for idx in LEFT_IRIS + RIGHT_IRIS:
                        landmark = face_landmarks.landmark[idx]
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
                
                # Update EAR
                self.root.after(0, self.ear_label.config, 
                               {'text': f"EAR: {avg_ear:.3f}"})
                
                # Execute actions
                if action:
                    if self.current_mode == "video_scroll":
                        if action == "single_blink":
                            pyautogui.press('down')
                            cv2.putText(frame, "SCROLL DOWN", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif action == "double_blink":
                            pyautogui.press('up')
                            cv2.putText(frame, "SCROLL UP", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        elif action == "wink_left":
                            pyautogui.press('l')
                            cv2.putText(frame, "LIKE", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                        elif action == "wink_right":
                            pyautogui.press('space')
                            cv2.putText(frame, "PAUSE/PLAY", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    
                    elif self.current_mode == "mouse_control":
                        if action == "left_click":
                            pyautogui.click()
                            cv2.putText(frame, "LEFT CLICK", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif action == "right_click":
                            pyautogui.rightClick()
                            cv2.putText(frame, "RIGHT CLICK", (10, 60),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            # Hand gesture detection (mouse control mode only)
            if self.current_mode == "mouse_control" and hand_results and \
               hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, 
                        mp.solutions.hands.HAND_CONNECTIONS
                    )
                    
                    current_time = time.time()
                    if (current_time - self.gesture_detector.last_gesture_time) > \
                       self.gesture_detector.gesture_cooldown:
                        
                        direction = self.gesture_detector.detect_finger_direction(
                            hand_landmarks
                        )
                        
                        if direction == "up":
                            pyautogui.scroll(3)
                            self.controller.stats['scrolls_up'] += 1
                            self.gesture_detector.last_gesture_time = current_time
                            cv2.putText(frame, "SCROLL UP", (10, 100),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif direction == "down":
                            pyautogui.scroll(-3)
                            self.controller.stats['scrolls_down'] += 1
                            self.gesture_detector.last_gesture_time = current_time
                            cv2.putText(frame, "SCROLL DOWN", (10, 100),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Update stats
            for key, label in self.stats_labels.items():
                self.root.after(0, label.config, 
                               {'text': str(self.controller.stats[key])})
            
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
    app = UnifiedEyeControllerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

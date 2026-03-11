"""
Eye Blink Scroller - GUI Application
Modern interface with profile settings and controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading
from PIL import Image, ImageTk
from collections import deque

# Eye landmark indices
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

class BlinkDetector:
    def __init__(self, ear_threshold=0.21, blink_duration=0.3, cooldown=1.5):
        self.ear_threshold = ear_threshold
        self.intentional_blink_duration = blink_duration
        self.cooldown = cooldown
        
        self.last_action_time = 0
        self.blink_start_time = None
        self.last_blink_state = False
        self.recent_blinks = deque(maxlen=2)
        self.double_blink_window = 0.5
        
        # Statistics
        self.stats = {
            'single_blinks': 0,
            'double_blinks': 0,
            'left_winks': 0,
            'right_winks': 0
        }
    
    def calculate_ear(self, eye_landmarks):
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (v1 + v2) / (2.0 * h)
    
    def get_eye_landmarks(self, landmarks, eye_indices, w, h):
        coords = []
        for idx in eye_indices:
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
    
    def process(self, landmarks, w, h):
        current_time = time.time()
        
        left_eye = self.get_eye_landmarks(landmarks, LEFT_EYE, w, h)
        right_eye = self.get_eye_landmarks(landmarks, RIGHT_EYE, w, h)
        
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        action = None
        
        wink = self.detect_wink(left_ear, right_ear)
        if wink and (current_time - self.last_action_time) > 0.5:
            action = f"wink_{wink}"
            self.stats[f'{wink}_winks'] += 1
            self.last_action_time = current_time
            return avg_ear, left_ear, right_ear, left_eye, right_eye, action
        
        is_blinking = avg_ear < self.ear_threshold
        
        if is_blinking and not self.last_blink_state:
            self.blink_start_time = current_time
        elif not is_blinking and self.last_blink_state and self.blink_start_time:
            blink_duration = current_time - self.blink_start_time
            
            if (current_time - self.last_action_time) > self.cooldown:
                self.recent_blinks.append(current_time)
                
                if len(self.recent_blinks) == 2:
                    time_between = self.recent_blinks[1] - self.recent_blinks[0]
                    if time_between < self.double_blink_window:
                        action = "double_blink"
                        self.stats['double_blinks'] += 1
                        self.last_action_time = current_time
                        self.recent_blinks.clear()
                        self.blink_start_time = None
                        self.last_blink_state = is_blinking
                        return avg_ear, left_ear, right_ear, left_eye, right_eye, action
                
                if blink_duration >= self.intentional_blink_duration:
                    action = "single_blink"
                    self.stats['single_blinks'] += 1
                    self.last_action_time = current_time
            
            self.blink_start_time = None
        
        self.last_blink_state = is_blinking
        return avg_ear, left_ear, right_ear, left_eye, right_eye, action

class BlinkScrollerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye Blink Video Scroller")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        
        self.is_running = False
        self.cap = None
        self.detector = None
        self.face_mesh = None
        
        # Profile settings
        self.profile = {
            'name': 'User',
            'ear_threshold': 0.21,
            'blink_duration': 0.3,
            'cooldown': 1.5,
            'enable_scroll': True,
            'enable_wink': True
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header.pack(fill='x', padx=10, pady=10)
        
        title = tk.Label(header, text="👁️ Eye Blink Video Scroller", 
                        font=('Arial', 20, 'bold'), bg='#2d2d2d', fg='#00ff88')
        title.pack(side='left', padx=20, pady=10)
        
        # Mouse Controller button
        self.mouse_btn = tk.Button(header, text="🖱️ Mouse Controller", 
                                   command=self.open_mouse_controller,
                                   font=('Arial', 12), bg='#ff8800', fg='white',
                                   relief='flat', padx=20, pady=5)
        self.mouse_btn.pack(side='right', padx=5)
        
        # Profile button
        self.profile_btn = tk.Button(header, text="⚙️ Profile", 
                                     command=self.open_profile,
                                     font=('Arial', 12), bg='#3d3d3d', fg='white',
                                     relief='flat', padx=20, pady=5)
        self.profile_btn.pack(side='right', padx=5)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Video feed
        left_panel = tk.Frame(main_container, bg='#2d2d2d')
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        video_label = tk.Label(left_panel, text="Video Feed", 
                              font=('Arial', 14, 'bold'), bg='#2d2d2d', fg='white')
        video_label.pack(pady=10)
        
        self.video_canvas = tk.Label(left_panel, bg='black')
        self.video_canvas.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Right panel - Controls and stats
        right_panel = tk.Frame(main_container, bg='#2d2d2d', width=300)
        right_panel.pack(side='right', fill='y', padx=5)
        right_panel.pack_propagate(False)
        
        # Control buttons
        control_frame = tk.Frame(right_panel, bg='#2d2d2d')
        control_frame.pack(pady=20, padx=20, fill='x')
        
        self.start_btn = tk.Button(control_frame, text="▶️ START", 
                                   command=self.start_detection,
                                   font=('Arial', 14, 'bold'), bg='#00ff88', fg='black',
                                   relief='flat', padx=30, pady=15)
        self.start_btn.pack(fill='x', pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP", 
                                  command=self.stop_detection,
                                  font=('Arial', 14, 'bold'), bg='#ff4444', fg='white',
                                  relief='flat', padx=30, pady=15, state='disabled')
        self.stop_btn.pack(fill='x', pady=5)
        
        # Status
        status_frame = tk.LabelFrame(right_panel, text="Status", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2d2d2d', fg='white', padx=10, pady=10)
        status_frame.pack(pady=10, padx=20, fill='x')
        
        self.status_label = tk.Label(status_frame, text="⚫ Stopped", 
                                     font=('Arial', 11), bg='#2d2d2d', fg='#ff4444')
        self.status_label.pack()
        
        self.ear_label = tk.Label(status_frame, text="EAR: --", 
                                  font=('Arial', 10), bg='#2d2d2d', fg='white')
        self.ear_label.pack(pady=5)
        
        # Statistics
        stats_frame = tk.LabelFrame(right_panel, text="Statistics", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#2d2d2d', fg='white', padx=10, pady=10)
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        self.stats_labels = {}
        stats_items = [
            ('single_blinks', '⬇️ Scrolls Down'),
            ('double_blinks', '⬆️ Scrolls Up'),
            ('left_winks', '❤️ Likes'),
            ('right_winks', '⏸️ Pause/Play')
        ]
        
        for key, label in stats_items:
            frame = tk.Frame(stats_frame, bg='#2d2d2d')
            frame.pack(fill='x', pady=3)
            tk.Label(frame, text=label, font=('Arial', 9), 
                    bg='#2d2d2d', fg='white').pack(side='left')
            self.stats_labels[key] = tk.Label(frame, text="0", 
                                             font=('Arial', 9, 'bold'),
                                             bg='#2d2d2d', fg='#00ff88')
            self.stats_labels[key].pack(side='right')
        
        # Instructions
        inst_frame = tk.LabelFrame(right_panel, text="Controls", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2d2d2d', fg='white', padx=10, pady=10)
        inst_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        instructions = [
            "👁️ Hold blink 0.3s: Scroll down",
            "👁️👁️ Double blink: Scroll up",
            "😉 Wink left: Like video",
            "😉 Wink right: Pause/Play"
        ]
        
        for inst in instructions:
            tk.Label(inst_frame, text=inst, font=('Arial', 9), 
                    bg='#2d2d2d', fg='white', anchor='w').pack(fill='x', pady=2)
    
    def open_profile(self):
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Profile Settings")
        profile_window.geometry("400x500")
        profile_window.configure(bg='#2d2d2d')
        
        tk.Label(profile_window, text="⚙️ Profile Settings", 
                font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='#00ff88').pack(pady=20)
        
        # Name
        frame = tk.Frame(profile_window, bg='#2d2d2d')
        frame.pack(pady=10, padx=30, fill='x')
        tk.Label(frame, text="Name:", font=('Arial', 10), 
                bg='#2d2d2d', fg='white').pack(anchor='w')
        name_entry = tk.Entry(frame, font=('Arial', 10))
        name_entry.insert(0, self.profile['name'])
        name_entry.pack(fill='x', pady=5)
        
        # EAR Threshold
        frame = tk.Frame(profile_window, bg='#2d2d2d')
        frame.pack(pady=10, padx=30, fill='x')
        tk.Label(frame, text="EAR Threshold (Sensitivity):", 
                font=('Arial', 10), bg='#2d2d2d', fg='white').pack(anchor='w')
        ear_scale = tk.Scale(frame, from_=0.15, to=0.30, resolution=0.01,
                            orient='horizontal', bg='#3d3d3d', fg='white',
                            highlightthickness=0)
        ear_scale.set(self.profile['ear_threshold'])
        ear_scale.pack(fill='x', pady=5)
        
        # Blink Duration
        frame = tk.Frame(profile_window, bg='#2d2d2d')
        frame.pack(pady=10, padx=30, fill='x')
        tk.Label(frame, text="Blink Duration (seconds):", 
                font=('Arial', 10), bg='#2d2d2d', fg='white').pack(anchor='w')
        duration_scale = tk.Scale(frame, from_=0.1, to=0.5, resolution=0.05,
                                 orient='horizontal', bg='#3d3d3d', fg='white',
                                 highlightthickness=0)
        duration_scale.set(self.profile['blink_duration'])
        duration_scale.pack(fill='x', pady=5)
        
        # Cooldown
        frame = tk.Frame(profile_window, bg='#2d2d2d')
        frame.pack(pady=10, padx=30, fill='x')
        tk.Label(frame, text="Cooldown (seconds):", 
                font=('Arial', 10), bg='#2d2d2d', fg='white').pack(anchor='w')
        cooldown_scale = tk.Scale(frame, from_=0.5, to=3.0, resolution=0.1,
                                 orient='horizontal', bg='#3d3d3d', fg='white',
                                 highlightthickness=0)
        cooldown_scale.set(self.profile['cooldown'])
        cooldown_scale.pack(fill='x', pady=5)
        
        # Checkboxes
        frame = tk.Frame(profile_window, bg='#2d2d2d')
        frame.pack(pady=10, padx=30, fill='x')
        
        scroll_var = tk.BooleanVar(value=self.profile['enable_scroll'])
        tk.Checkbutton(frame, text="Enable Scrolling", variable=scroll_var,
                      font=('Arial', 10), bg='#2d2d2d', fg='white',
                      selectcolor='#3d3d3d').pack(anchor='w', pady=5)
        
        wink_var = tk.BooleanVar(value=self.profile['enable_wink'])
        tk.Checkbutton(frame, text="Enable Wink Controls", variable=wink_var,
                      font=('Arial', 10), bg='#2d2d2d', fg='white',
                      selectcolor='#3d3d3d').pack(anchor='w', pady=5)
        
        def save_profile():
            self.profile['name'] = name_entry.get()
            self.profile['ear_threshold'] = ear_scale.get()
            self.profile['blink_duration'] = duration_scale.get()
            self.profile['cooldown'] = cooldown_scale.get()
            self.profile['enable_scroll'] = scroll_var.get()
            self.profile['enable_wink'] = wink_var.get()
            
            if self.detector:
                self.detector.ear_threshold = self.profile['ear_threshold']
                self.detector.intentional_blink_duration = self.profile['blink_duration']
                self.detector.cooldown = self.profile['cooldown']
            
            messagebox.showinfo("Success", "Profile settings saved!")
            profile_window.destroy()
        
        tk.Button(profile_window, text="💾 Save Settings", command=save_profile,
                 font=('Arial', 12, 'bold'), bg='#00ff88', fg='black',
                 relief='flat', padx=30, pady=10).pack(pady=20)
    
    def open_mouse_controller(self):
        """Launch the mouse controller in a new window"""
        import subprocess
        import sys
        
        # Stop current detection if running
        if self.is_running:
            self.stop_detection()
        
        # Launch mouse controller
        try:
            subprocess.Popen([sys.executable, "eye_mouse_controller.py"])
            messagebox.showinfo("Mouse Controller", 
                              "Mouse Controller launched in a new window!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch Mouse Controller:\n{e}")
    
    def start_detection(self):
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam!")
            return
        
        self.detector = BlinkDetector(
            self.profile['ear_threshold'],
            self.profile['blink_duration'],
            self.profile['cooldown']
        )
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="🟢 Running", fg='#00ff88')
        
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
    
    def stop_detection(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⚫ Stopped", fg='#ff4444')
        self.video_canvas.config(image='', bg='black')
    
    def detection_loop(self):
        mp_face_mesh = mp.solutions.face_mesh
        
        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:
            
            while self.is_running:
                success, frame = self.cap.read()
                if not success:
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    
                    avg_ear, left_ear, right_ear, left_eye, right_eye, action = \
                        self.detector.process(face_landmarks.landmark, w, h)
                    
                    # Draw eyes
                    for point in left_eye:
                        cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
                    for point in right_eye:
                        cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
                    
                    # Update UI
                    self.root.after(0, self.ear_label.config, 
                                   {'text': f"EAR: {avg_ear:.3f}"})
                    
                    # Execute actions
                    if action and self.profile['enable_scroll']:
                        if action == "single_blink":
                            pyautogui.press('down')
                        elif action == "double_blink":
                            pyautogui.press('up')
                        elif action == "wink_left" and self.profile['enable_wink']:
                            pyautogui.press('l')
                        elif action == "wink_right" and self.profile['enable_wink']:
                            pyautogui.press('space')
                    
                    # Update stats
                    for key, label in self.stats_labels.items():
                        self.root.after(0, label.config, 
                                       {'text': str(self.detector.stats[key])})
                
                # Display frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.root.after(0, self.video_canvas.config, {'image': imgtk})
                self.video_canvas.imgtk = imgtk
                
                time.sleep(0.03)

def main():
    root = tk.Tk()
    app = BlinkScrollerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

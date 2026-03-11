# Unified Eye Controller - Complete Guide

ONE application with TWO powerful modes you can switch between!

## 🎯 Two Modes in One App

### 📱 Mode 1: Video Scroll Mode
Perfect for watching reels, shorts, and videos hands-free!
- **Single blink** (hold 0.3s): Scroll down to next video
- **Double blink**: Scroll up to previous video
- **Wink left eye**: Like the video
- **Wink right eye**: Pause/Play

### 🖱️ Mode 2: Mouse Control Mode
Complete computer control with your eyes and hands!
- **Move eyes**: Control mouse cursor
- **Single blink**: Left click
- **Double blink**: Right click
- **Point finger up**: Scroll up
- **Point finger down**: Scroll down

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python unified_eye_controller.py
```

Or with Python 3.11:
```bash
C:\Users\rajku\AppData\Local\Programs\Python\Python311\python.exe unified_eye_controller.py
```

## 📖 How to Use

### Step 1: Choose Your Mode
At the top of the window, you'll see two mode buttons:
- **📱 Video Scroll** - For watching videos
- **🖱️ Mouse Control** - For controlling your computer

Click the mode you want to use.

### Step 2: Start the Controller
1. Position yourself in front of your webcam
2. Ensure good lighting on your face
3. Click the **▶️ START** button
4. The webcam feed will appear with eye tracking

### Step 3: Use the Controls
The instructions panel on the right shows what each action does in your current mode.

### Step 4: Switch Modes Anytime
1. Click **⏹️ STOP** to stop the current session
2. Select the other mode button at the top
3. Click **▶️ START** again

## 🎮 Detailed Controls

### Video Scroll Mode (📱)

| Action | How To Do It | Result |
|--------|-------------|--------|
| Scroll Down | Hold blink for 0.3 seconds | Next video ⬇️ |
| Scroll Up | Blink twice quickly | Previous video ⬆️ |
| Like | Wink left eye | Like video ❤️ |
| Pause/Play | Wink right eye | Toggle playback ⏸️ |

**Best For:**
- YouTube Shorts
- Instagram Reels
- TikTok
- Facebook Reels
- Any vertical video platform

### Mouse Control Mode (🖱️)

| Action | How To Do It | Result |
|--------|-------------|--------|
| Move Cursor | Look where you want to go | Cursor follows your gaze |
| Left Click | Single blink | Click 🖱️ |
| Right Click | Double blink quickly | Right-click menu 🖱️ |
| Scroll Up | Point index finger up | Page scrolls up ⬆️ |
| Scroll Down | Point index finger down | Page scrolls down ⬇️ |

**Best For:**
- Web browsing
- Reading documents
- Navigating menus
- Accessibility needs
- Hands-free computing

## 📊 Interface Overview

```
┌────────────────────────────────────────────────────────────┐
│  👁️ Unified Eye Controller                                │
│                    [📱 Video Scroll] [🖱️ Mouse Control]    │
├─────────────────────────────┬──────────────────────────────┤
│                             │  ▶️ START                    │
│   📱 VIDEO SCROLL MODE      │  ⏹️ STOP                     │
│                             │                              │
│     [Webcam Feed]           │  Status: 🟢 Running          │
│   (Eye tracking visible)    │  EAR: 0.245                  │
│                             │                              │
│                             │  Statistics:                 │
│                             │  ⬇️ Scrolls Down: 12         │
│                             │  ⬆️ Scrolls Up: 3            │
│                             │  ❤️ Likes: 5                 │
│                             │  ⏸️ Pause/Play: 2            │
│                             │                              │
│                             │  Controls:                   │
│                             │  👁️ Hold blink: Scroll down  │
│                             │  👁️👁️ Double blink: Scroll up│
│                             │  😉 Wink left: Like          │
│                             │  😉 Wink right: Pause/Play   │
└─────────────────────────────┴──────────────────────────────┘
```

## ⚙️ Technical Details

### Video Scroll Mode Settings
- **EAR Threshold**: 0.21 (blink sensitivity)
- **Blink Duration**: 0.3 seconds (minimum hold time)
- **Cooldown**: 1.5 seconds (prevents accidental scrolls)
- **Double Blink Window**: 0.5 seconds

### Mouse Control Mode Settings
- **EAR Threshold**: 0.21 (blink sensitivity)
- **Blink Duration**: 0.1 seconds (faster clicks)
- **Cooldown**: 0.5 seconds (faster response)
- **Mouse Smoothing**: 5 frames (smooth cursor movement)
- **Gesture Cooldown**: 0.5 seconds

### How Eye Tracking Works
1. **MediaPipe Face Mesh** detects 468 facial landmarks
2. **Iris landmarks** (4 points per eye) track gaze direction
3. **Eye Aspect Ratio (EAR)** calculated to detect blinks
4. **Smoothing algorithm** prevents jittery cursor movement
5. **Screen mapping** converts eye position to screen coordinates

### How Gesture Detection Works
1. **MediaPipe Hands** detects 21 hand landmarks
2. **Index finger** tip and base positions analyzed
3. **Vertical direction** determined relative to wrist
4. **Scroll action** triggered based on direction

## 💡 Tips for Best Results

### General Tips
- **Lighting**: Ensure your face is well-lit, avoid backlighting
- **Distance**: Sit 1-2 feet from the webcam
- **Camera Position**: Place camera at eye level
- **Stability**: Keep your head relatively still

### Video Scroll Mode Tips
- Practice intentional blinks vs natural blinks
- Hold blinks slightly longer for better detection
- Wait for cooldown between actions
- Use winks deliberately (close one eye fully)

### Mouse Control Mode Tips
- Look at the target before blinking to click
- Move eyes smoothly for better cursor control
- Extend finger clearly for gesture detection
- Keep hand in camera view for scrolling

## 🔧 Customization

Edit `unified_eye_controller.py` to adjust settings:

```python
# Video Scroll Mode
self.cooldown = 1.5  # Time between scrolls
self.blink_duration = 0.3  # Minimum blink time

# Mouse Control Mode
self.cooldown = 0.5  # Time between clicks
self.smoothing = 5  # Cursor smoothing (higher = smoother)
```

## 🐛 Troubleshooting

### Video Scroll Mode Issues

**Problem**: Too sensitive, scrolls accidentally
- **Solution**: Increase `self.cooldown` or `self.blink_duration`

**Problem**: Not detecting blinks
- **Solution**: Decrease `self.ear_threshold` or improve lighting

**Problem**: Winks not working
- **Solution**: Close one eye completely, keep other eye open

### Mouse Control Mode Issues

**Problem**: Cursor too jittery
- **Solution**: Increase `self.smoothing` value (try 7-10)

**Problem**: Cursor not moving
- **Solution**: Check if iris landmarks are visible (yellow dots)

**Problem**: Accidental clicks
- **Solution**: Increase `self.cooldown` or `self.ear_threshold`

**Problem**: Gestures not detected
- **Solution**: Extend finger more clearly, improve hand lighting

### General Issues

**Problem**: Webcam not opening
- **Solution**: Close other apps using the camera, check permissions

**Problem**: App freezes
- **Solution**: Click STOP, restart the application

**Problem**: Mode switch not working
- **Solution**: Stop current session before switching modes

## 📋 Requirements

- Python 3.8 or higher
- Webcam (built-in or external)
- Windows/Mac/Linux
- Required packages (see requirements.txt):
  - opencv-python
  - mediapipe
  - pyautogui
  - numpy
  - Pillow

## 🎯 Use Cases

### Video Scroll Mode
- Watching videos while eating
- Hands-free entertainment
- Accessibility for limited mobility
- Multitasking (cooking, exercising, etc.)

### Mouse Control Mode
- Accessibility for motor impairments
- Hands-free computer operation
- Gaming (limited applications)
- Presentations and demos
- Situations where hands are occupied

## 🔒 Privacy & Safety

- All processing happens locally on your computer
- No video or images are uploaded anywhere
- Webcam feed is only used for real-time detection
- No data is stored or recorded
- PyAutoGUI failsafe disabled for smooth operation

## 🚀 Future Enhancements

- Calibration wizard for personalized settings
- Profile saving and loading
- Customizable keyboard shortcuts
- Drag and drop in mouse mode
- Triple blink for additional actions
- Voice command integration
- Multi-monitor support
- Gesture customization

## 📝 Keyboard Shortcuts Used

### Video Scroll Mode
- `Down Arrow`: Scroll to next video
- `Up Arrow`: Scroll to previous video
- `L`: Like video (platform-specific)
- `Space`: Pause/Play

### Mouse Control Mode
- Mouse movement: Cursor control
- Left click: Primary action
- Right click: Context menu
- Scroll: Page navigation

## 🎓 Learning Curve

- **Video Scroll Mode**: 2-5 minutes to get comfortable
- **Mouse Control Mode**: 10-15 minutes to master cursor control
- **Mode Switching**: Instant, no learning required

## ⚡ Performance

- Runs at 30-60 FPS depending on hardware
- Low CPU usage with MediaPipe optimization
- Minimal latency for responsive control
- Works on most modern computers

---

Enjoy hands-free control of your computer! 👁️✨

For issues or questions, check the troubleshooting section above.

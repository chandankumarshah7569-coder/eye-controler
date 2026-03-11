# Eye & Gesture Mouse Controller

Control your mouse cursor with your eyes and perform actions with blinks and hand gestures!

## Features

### Eye Gaze Tracking
- **Move cursor**: Simply look where you want the cursor to go
- **Smooth movement**: Built-in smoothing for natural cursor control
- **Real-time tracking**: Uses MediaPipe iris landmarks for precise tracking

### Blink Controls
- **Single blink**: Left mouse click
- **Double blink**: Right mouse click
- **Cooldown system**: Prevents accidental multiple clicks

### Hand Gesture Controls
- **Point finger up** ☝️: Scroll up
- **Point finger down** 👇: Scroll down
- **Automatic detection**: Works alongside eye tracking

### Live Statistics
- Track left clicks, right clicks, and scrolls
- Real-time EAR (Eye Aspect Ratio) monitoring
- Visual feedback for all actions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Launch from Main GUI
```bash
python gui_app.py
```
Then click the "🖱️ Mouse Controller" button

### Option 2: Direct Launch
```bash
python eye_mouse_controller.py
```

Or with Python 3.11:
```bash
C:\Users\rajku\AppData\Local\Programs\Python\Python311\python.exe eye_mouse_controller.py
```

## How It Works

### Eye Tracking
1. MediaPipe detects your face and iris landmarks
2. Iris center position is calculated
3. Position is mapped to screen coordinates
4. Smoothing algorithm prevents jittery movement
5. Cursor moves to the calculated position

### Blink Detection
1. Eye Aspect Ratio (EAR) is calculated continuously
2. When EAR drops below threshold, a blink is detected
3. Single blink triggers left click
4. Two blinks within 0.5 seconds triggers right click

### Gesture Recognition
1. MediaPipe Hands detects hand landmarks
2. Index finger tip and base positions are analyzed
3. Vertical direction is determined
4. Scroll action is triggered based on direction

## Controls Summary

| Action | Result |
|--------|--------|
| Move eyes | Move cursor |
| Single blink | Left click |
| Double blink | Right click |
| Point finger up | Scroll up |
| Point finger down | Scroll down |

## Tips for Best Results

### Eye Tracking
- Sit 1-2 feet from the camera
- Ensure good, even lighting on your face
- Camera should be at eye level
- Minimize head movement for better accuracy

### Blink Detection
- Practice intentional vs natural blinks
- Adjust sensitivity if needed (modify `ear_threshold` in code)
- Wait for cooldown between clicks

### Gesture Control
- Extend your index finger clearly
- Keep hand in camera view
- Point distinctly up or down
- Wait for cooldown between scrolls

## Customization

Edit `eye_mouse_controller.py` to adjust:

```python
# Mouse smoothing (higher = smoother but slower)
self.smoothing = 5

# Blink sensitivity
self.ear_threshold = 0.21

# Click cooldown (seconds)
self.click_cooldown = 0.5

# Gesture cooldown (seconds)
self.gesture_cooldown = 0.5
```

## Troubleshooting

### Cursor too jittery
- Increase `self.smoothing` value (try 7-10)
- Ensure stable lighting
- Minimize head movement

### Cursor not moving
- Check if face is detected (green dots on eyes)
- Adjust camera angle
- Improve lighting conditions

### Too many accidental clicks
- Increase `self.click_cooldown`
- Increase `self.ear_threshold` (less sensitive)

### Gestures not detected
- Ensure hand is clearly visible
- Extend index finger more prominently
- Check lighting on hand

### Cursor moving in wrong direction
- Adjust the interpolation ranges in `get_gaze_position()`
- Calibrate based on your screen size

## Safety Features

- PyAutoGUI failsafe disabled for smooth operation
- Cooldown periods prevent accidental spam
- Smoothing prevents erratic movements
- Clear visual feedback for all actions

## Requirements

- Python 3.8+
- Webcam
- Windows/Mac/Linux
- Screen resolution: Any (auto-adapts)

## Performance

- Runs at ~30-60 FPS depending on hardware
- Low latency cursor movement
- Minimal CPU usage with MediaPipe optimization

## Known Limitations

- Works best in well-lit environments
- Requires clear view of face and hand
- May need calibration for different users
- Screen edges may be harder to reach

## Future Enhancements

- Calibration wizard for personalized settings
- Multiple gesture support
- Drag and drop functionality
- Customizable sensitivity profiles
- Multi-monitor support

Enjoy hands-free computing! 🖱️👁️✨

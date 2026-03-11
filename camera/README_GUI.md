# Eye Blink Video Scroller - GUI Version

Modern graphical interface for controlling videos with eye blinks and winks.

## Features

### Main Interface
- **Video Feed**: Real-time webcam display with eye tracking visualization
- **Control Panel**: Start/Stop buttons for easy control
- **Live Statistics**: Track your blinks and winks in real-time
- **Status Monitor**: See current EAR (Eye Aspect Ratio) values

### Profile Settings
- **Customizable Sensitivity**: Adjust EAR threshold (0.15-0.30)
- **Blink Duration**: Set minimum blink time (0.1-0.5 seconds)
- **Cooldown Period**: Configure delay between actions (0.5-3.0 seconds)
- **Toggle Features**: Enable/disable scrolling and wink controls
- **User Profile**: Save your name and preferences

### Controls
- Single blink (hold 0.3s): Scroll down ⬇️
- Double blink: Scroll up ⬆️
- Wink left eye: Like video ❤️
- Wink right eye: Pause/Play ⏸️

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the GUI application:
```bash
python gui_app.py
```

Or with Python 3.11:
```bash
C:\Users\rajku\AppData\Local\Programs\Python\Python311\python.exe gui_app.py
```

### Steps:
1. Click the "⚙️ Profile" button to configure settings
2. Adjust sensitivity and preferences
3. Click "▶️ START" to begin detection
4. Position yourself in front of the webcam
5. Open your video platform and start blinking!
6. Click "⏹️ STOP" when done

## Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  👁️ Eye Blink Video Scroller          ⚙️ Profile       │
├──────────────────────────┬──────────────────────────────┤
│                          │  ▶️ START                    │
│                          │  ⏹️ STOP                     │
│     Video Feed           │                              │
│   (Webcam Display)       │  Status: 🟢 Running          │
│                          │  EAR: 0.245                  │
│                          │                              │
│                          │  Statistics:                 │
│                          │  ⬇️ Scrolls Down: 5          │
│                          │  ⬆️ Scrolls Up: 2            │
│                          │  ❤️ Likes: 3                 │
│                          │  ⏸️ Pause/Play: 1            │
│                          │                              │
│                          │  Controls:                   │
│                          │  👁️ Hold blink: Scroll down  │
│                          │  👁️👁️ Double blink: Scroll up│
│                          │  😉 Wink left: Like          │
│                          │  😉 Wink right: Pause/Play   │
└──────────────────────────┴──────────────────────────────┘
```

## Customization

Access the Profile Settings to adjust:
- **EAR Threshold**: Lower = more sensitive, Higher = less sensitive
- **Blink Duration**: Minimum time to hold blink for detection
- **Cooldown**: Prevents accidental multiple triggers
- **Enable/Disable**: Turn features on/off as needed

## Troubleshooting

- **Webcam not opening**: Close other apps using the camera
- **Too sensitive**: Increase EAR threshold in Profile settings
- **Not detecting**: Decrease EAR threshold or ensure good lighting
- **GUI not responding**: Make sure all dependencies are installed

## Requirements

- Python 3.8+
- Webcam
- Windows/Mac/Linux
- All packages in requirements.txt

## Tips for Best Results

1. Ensure good lighting on your face
2. Position camera at eye level
3. Sit 1-2 feet from the camera
4. Adjust sensitivity in Profile settings
5. Practice intentional vs natural blinks

Enjoy hands-free video control! 👁️✨

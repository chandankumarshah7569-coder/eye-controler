# Changelog

All notable changes to the Eye Controller project will be documented in this file.

## [1.0.0] - 2024-03-11

### Added
- **Unified Eye Controller** - Single application with two modes
- **Video Scroll Mode**
  - Single blink to scroll down (next video)
  - Double blink to scroll up (previous video)
  - Left eye wink to like videos
  - Right eye wink to pause/play
  - Optimized for YouTube Shorts, Instagram Reels, TikTok
- **Mouse Control Mode**
  - Eye gaze tracking for cursor movement
  - Single blink for left click
  - Double blink for right click
  - Hand gesture detection for scrolling
  - Point finger up to scroll up
  - Point finger down to scroll down
- **User Interface**
  - Modern dark theme GUI
  - Real-time video feed with eye tracking visualization
  - Live statistics tracking
  - Mode switching with radio buttons
  - Status monitoring (EAR display)
  - Dynamic instructions based on mode
- **Core Features**
  - MediaPipe Face Mesh for facial landmark detection
  - MediaPipe Hands for gesture recognition
  - Eye Aspect Ratio (EAR) calculation for blink detection
  - Smooth cursor movement with averaging algorithm
  - Cooldown system to prevent accidental actions
  - Configurable sensitivity and timing parameters

### Technical Details
- Built with Python 3.8+
- Uses OpenCV for video processing
- MediaPipe for AI-powered detection
- PyAutoGUI for system control
- Tkinter for GUI
- Pillow for image handling

### Documentation
- Comprehensive README with usage instructions
- Publishing guide for distribution
- Troubleshooting section
- Tips for optimal performance

## [Future Releases]

### Planned Features
- Calibration wizard for personalized settings
- Profile saving and loading
- Customizable keyboard shortcuts
- Drag and drop in mouse mode
- Triple blink actions
- Multi-monitor support
- Voice command integration
- Settings export/import
- Performance optimization
- Additional gesture controls

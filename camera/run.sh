#!/bin/bash

echo "========================================"
echo "  Eye Controller - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Checking dependencies..."
if ! python3 -c "import cv2" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting Eye Controller..."
echo ""
python3 unified_eye_controller.py

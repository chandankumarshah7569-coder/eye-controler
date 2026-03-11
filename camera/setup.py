"""
Setup script for Eye Controller package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="unified-eye-controller",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Control videos and mouse with your eyes - AI-powered accessibility tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/eye-controller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Hardware :: Universal Serial Bus (USB) :: Human Interface Device (HID)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="eye-tracking computer-vision accessibility mediapipe opencv hands-free",
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "pyautogui>=0.9.50",
        "numpy>=1.24.0",
        "Pillow>=9.3.0",
    ],
    entry_points={
        "console_scripts": [
            "eye-controller=unified_eye_controller:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/eye-controller/issues",
        "Source": "https://github.com/yourusername/eye-controller",
    },
)

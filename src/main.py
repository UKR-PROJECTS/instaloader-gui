"""
insta-downloader-gui - Professional Instagram Reel Downloader  with transcription
==============================================

insta-downloader-gui with Queue Management
A professional PyQt6 application for downloading Instagram Reels

Author: Ujjwal Nova
Version: 3.0.0
License: MIT
Repository: https://github.com/ukr-projects/insta-downloader-gui

Features:
- Dual download engines: yt-dlp and instaloader.
- Automatic fallback to the secondary downloader if the primary one fails.
- User-selectable preferred downloader.
- Download Instagram Reels as .mp4 files.
- Extract and save video thumbnails as .jpg files.
- Save captions as .txt files.
- Extract audio tracks as .mp3 files.
- Optional transcription of audio to text using OpenAI Whisper.
- Responsive, user-friendly GUI built with PyQt6.
- Session-based organization: downloads are grouped by timestamped session folders.
- Queue management for batch downloads with real-time progress.

Dependencies:
- PyQt6: GUI framework
- instaloader: Instagram Media Downloader Engine (LAZY LOADED)
- moviepy==1.0.3: Extracting mp3 (LAZY LOADED)
- Pillow: Image Processing (LAZY LOADED)
- openai-whisper: Reel Transcription (LAZY LOADED)
- yt-dlp.exe: included in the bin folder

Usage:
- cd src
- python main.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

# Add parent directory to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import InstagramDownloaderGUI
from src.resources.splash import SplashScreen
from src.utils.resource_loader import get_resource_path


def main():
    """
    Main application entry point.

    Initializes the PyQt6 application, configures logging for frozen environments,
    sets application metadata and styles, displays a splash screen,
    and launches the main GUI window.
    """
    # Redirect stdout and stderr to a log file in frozen environment (e.g., PyInstaller)
    if getattr(sys, "frozen", False):
        log_path = Path(sys.executable).parent / "app.log"
        sys.stdout = open(log_path, "w")
        sys.stderr = sys.stdout
        print(f"Logging started at {datetime.now()}")

    # Create the QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("insta-downloader-gui")
    app.setApplicationVersion("3.0.0")
    app.setStyle("Fusion")

    # Print environment information for debugging purposes
    print(f"Python version: {sys.version}")
    print(f"Current directory: {Path.cwd()}")
    print(f"Executable path: {sys.executable}")

    # Set global application stylesheet for consistent look and feel
    app.setStyleSheet(
        """
        * {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }
        QToolTip {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 5px;
        }
    """
    )

    # Show splash screen during application initialization
    splash = SplashScreen()
    splash.show()
    splash.show_message("Initializing...")

    # Create and show the main application window
    window = InstagramDownloaderGUI()
    # Finish the splash screen and display the main window
    splash.finish(window)

    # Set application icon from resources
    icon_path = get_resource_path("favicon.ico")
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
        window.setWindowIcon(app_icon)

    # Display the main window
    window.showMaximized()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

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
- cd src/transcriptionEnabled
- python -m src.main
"""

import sys
import os

# Set the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import InstagramDownloaderGUI
from src.resources.splash import SplashScreen


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("insta-downloader-gui")
    app.setApplicationVersion("3.0.0")
    app.setStyle("Fusion")

    # Set global application style
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

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    splash.show_message("Initializing...")

    # Create and show main window
    window = InstagramDownloaderGUI()
    splash.finish(window)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

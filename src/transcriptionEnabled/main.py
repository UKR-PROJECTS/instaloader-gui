"""
Instagram Media Downloader - Professional Instagram Reel Downloader
==============================================

Instagram Media Downloader with Queue Management
A professional PyQt6 application for downloading Instagram Reels with transcription

Author: Ujjwal Nova
Version: 2.0.1
License: MIT
Repository: https://github.com/UKR-PROJECTS/Instagram-Media-Downloader

OPTIMIZATION CHANGES:
- Lazy loading of heavy imports (instaloader, moviepy, whisper)
- Delayed initialization of components
- Reduced import time by moving imports to when needed
- Splash screen for better UX during startup
- Optimized dependencies loading

Features:
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
- openai-whisper: Reel Transcription (LAZY LOADED)
- Pillow: Image Processing (LAZY LOADED)

Usage:
- cd src
- cd transcriptionEnabled
- python main.py
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import traceback
from datetime import datetime

# PyQt6 imports (these are fast to import)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QListWidget, QListWidgetItem, QTabWidget, QFrame, QScrollArea,
    QGridLayout, QSpacerItem, QSizePolicy, QMessageBox, QFileDialog,
    QComboBox, QCheckBox, QGroupBox, QSplitter, QSplashScreen
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QRunnable, QThreadPool
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPalette, QColor, QIcon, QPainter,
    QBrush, QLinearGradient
)

# Global variables for lazy-loaded modules
_instaloader = None
_moviepy = None
_whisper = None
_requests = None
_PIL = None


def lazy_import_instaloader():
    """Lazy import instaloader when needed"""
    global _instaloader
    if _instaloader is None:
        try:
            import instaloader
            _instaloader = instaloader
        except ImportError as e:
            raise ImportError(f"Missing instaloader package: {e}")
    return _instaloader


def lazy_import_moviepy():
    """Lazy import moviepy when needed"""
    global _moviepy
    if _moviepy is None:
        try:
            from moviepy.editor import VideoFileClip
            _moviepy = VideoFileClip
        except ImportError as e:
            raise ImportError(f"Missing moviepy package: {e}")
    return _moviepy


def lazy_import_whisper():
    """Lazy import whisper when needed"""
    global _whisper
    if _whisper is None:
        try:
            import whisper
            _whisper = whisper
        except ImportError as e:
            raise ImportError(f"Missing whisper package: {e}")
    return _whisper


def lazy_import_requests():
    """Lazy import requests when needed"""
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError as e:
            raise ImportError(f"Missing requests package: {e}")
    return _requests


def lazy_import_pil():
    """Lazy import PIL when needed"""
    global _PIL
    if _PIL is None:
        try:
            from PIL import Image
            _PIL = Image
        except ImportError as e:
            raise ImportError(f"Missing PIL package: {e}")
    return _PIL


class SplashScreen(QSplashScreen):
    """Custom splash screen with loading progress"""

    def __init__(self):
        super().__init__()
        self.setup_splash()

    def setup_splash(self):
        """Setup splash screen appearance"""
        # Create splash screen pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#2c3e50"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw gradient background
        gradient = QLinearGradient(0, 0, 400, 300)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, 400, 300)

        # Draw app name
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        painter.drawText(50, 100, "Instagram Downloader")

        painter.setFont(QFont("Arial", 14))
        painter.drawText(50, 130, "Professional Media Downloader")

        # Draw loading text
        painter.setFont(QFont("Arial", 12))
        painter.drawText(50, 200, "Loading components...")
        painter.drawText(50, 220, "Please wait...")

        # Draw version
        painter.setFont(QFont("Arial", 10))
        painter.drawText(50, 270, "Version 2.0.1 - PyInstaller Optimized")

        painter.end()

        self.setPixmap(pixmap)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)

    def show_message(self, message: str):
        """Show loading message on splash screen"""
        self.showMessage(message, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                         QColor("white"))
        QApplication.processEvents()


@dataclass
class ReelItem:
    """
    Data class for reel download items

    Attributes:
        url: Instagram reel URL
        title: Display title for the reel
        status: Current download status
        progress: Download progress percentage
        thumbnail_path: Path to saved thumbnail
        video_path: Path to saved video file
        audio_path: Path to extracted audio
        caption: Reel caption text
        transcript: Audio transcription
        error_message: Error details if download fails
        folder_path: Path to reel's download folder
    """
    url: str
    title: str = ""
    status: str = "Pending"
    progress: int = 0
    thumbnail_path: str = ""
    video_path: str = ""
    audio_path: str = ""
    caption: str = ""
    transcript: str = ""
    error_message: str = ""
    folder_path: str = ""


class ModernButton(QPushButton):
    """Custom styled button with modern gradient design"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_button()

    def _setup_button(self):
        """Initialize button styling and properties"""
        self.setStyleSheet(self._get_button_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setFont(QFont("Arial", 9))

    def _get_button_style(self):
        """Return modern button stylesheet"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
            color: white;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
        }
        QPushButton:hover { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd8, stop:1 #6a4190);
        }
        QPushButton:pressed { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4e63c6, stop:1 #58377e);
        }
        QPushButton:disabled { 
            background: #bdc3c7; 
            color: #7f8c8d; 
        }
        """


class ModernProgressBar(QProgressBar):
    """Custom styled progress bar with modern design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_progress_bar()

    def _setup_progress_bar(self):
        """Initialize progress bar styling"""
        self.setMinimumHeight(20)
        self.setStyleSheet(self._get_progress_style())

    def _get_progress_style(self):
        """Return modern progress bar stylesheet"""
        return """
        QProgressBar {
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            text-align: center;
            background-color: #f8f9fa;
            font-size: 10px;
            color: #2c3e50;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            margin: 1px;
        }
        """


class ReelDownloader(QThread):
    """
    Background thread for downloading Instagram reels with lazy loading

    Signals:
        progress_updated: Emitted when download progress changes
        download_completed: Emitted when a download finishes successfully
        error_occurred: Emitted when an error occurs during download
    """

    # Signal definitions
    progress_updated = pyqtSignal(str, int, str)  # url, progress, status
    download_completed = pyqtSignal(str, dict)  # url, result_data
    error_occurred = pyqtSignal(str, str)  # url, error_message

    def __init__(self, reel_items: List[ReelItem], download_options: Dict[str, bool]):
        """
        Initialize downloader thread

        Args:
            reel_items: List of reels to download
            download_options: Dictionary of download preferences
        """
        super().__init__()
        self.reel_items = reel_items
        self.download_options = download_options
        self.is_running = True
        self.whisper_model = None
        self.session_folder = None
        self.loader = None

    def run(self):
        """Main download thread execution with lazy loading"""
        try:
            self._setup_session()
            self._lazy_load_dependencies()
            self._setup_instaloader()
            self._process_downloads()

        except Exception as e:
            self.error_occurred.emit("", f"Thread error: {str(e)}")

    def _lazy_load_dependencies(self):
        """Load dependencies only when needed"""
        self.progress_updated.emit("", 0, "Loading dependencies...")

        # Load whisper only if transcription is enabled
        if self.download_options.get('transcribe', False):
            self.progress_updated.emit("", 5, "Loading Whisper model...")
            try:
                whisper_module = lazy_import_whisper()
                self.whisper_model = whisper_module.load_model("base")
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
                self.whisper_model = None

    def _setup_session(self):
        """Create timestamped session folder for downloads"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = Path("downloads") / f"session_{timestamp}"
        self.session_folder.mkdir(parents=True, exist_ok=True)

    def _setup_instaloader(self):
        """Initialize Instaloader with optimal settings"""
        self.progress_updated.emit("", 10, "Setting up downloader...")
        instaloader_module = lazy_import_instaloader()

        self.loader = instaloader_module.Instaloader(
            download_video_thumbnails=True,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=str(self.session_folder)
        )

    def _process_downloads(self):
        """Process all downloads in the queue"""
        for i, item in enumerate(self.reel_items, 1):
            if not self.is_running:
                break

            try:
                self.progress_updated.emit(item.url, 0, "Starting download...")
                result = self._download_reel(item, i)
                self.download_completed.emit(item.url, result)

            except Exception as e:
                error_msg = f"Download failed: {str(e)}"
                self.error_occurred.emit(item.url, error_msg)

    def _download_reel(self, item: ReelItem, reel_number: int) -> Dict[str, Any]:
        """
        Download individual reel and process it

        Args:
            item: ReelItem to download
            reel_number: Sequential number for file naming

        Returns:
            Dictionary containing paths to downloaded files
        """
        result = {}
        temp_video_path = None

        try:
            # Validate URL and extract shortcode
            shortcode = self._extract_shortcode(item.url)
            if not shortcode:
                raise ValueError("Invalid Instagram URL")

            self.progress_updated.emit(item.url, 10, "Fetching reel data...")

            # Get Instagram post (lazy load instaloader)
            instaloader_module = lazy_import_instaloader()
            post = instaloader_module.Post.from_shortcode(self.loader.context, shortcode)

            # Create individual reel folder
            reel_folder = self.session_folder / f"reel{reel_number}"
            reel_folder.mkdir(exist_ok=True)
            result['folder_path'] = str(reel_folder)

            # Process downloads based on user options
            self._download_video(post, reel_folder, reel_number, result)
            self._download_thumbnail(post, reel_folder, reel_number, result)
            self._extract_audio(reel_folder, reel_number, result)
            self._save_caption(post, reel_folder, reel_number, result)
            self._transcribe_audio(reel_folder, reel_number, result)

            result['title'] = f"Reel {reel_number}"
            self.progress_updated.emit(item.url, 100, "Completed")

        except Exception as e:
            raise Exception(f"Download error: {str(e)}")

        finally:
            # Cleanup temporary files
            if temp_video_path and os.path.exists(str(temp_video_path)):
                self._safe_file_removal(str(temp_video_path))

        return result

    def _download_video(self, post, reel_folder: Path, reel_number: int, result: Dict):
        """Download video file if enabled"""
        need_video_for_audio = (self.download_options.get('audio', False) or
                                self.download_options.get('transcribe', False))

        if self.download_options.get('video', True) or need_video_for_audio:
            self.progress_updated.emit("", 20, "Downloading video...")

            video_path = reel_folder / f"video{reel_number}.mp4"

            try:
                # Lazy load requests
                requests_module = lazy_import_requests()
                response = requests_module.get(post.video_url, stream=True, timeout=30)
                response.raise_for_status()

                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                if self.download_options.get('video', True):
                    result['video_path'] = str(video_path)

            except Exception as e:
                raise Exception(f"Video download failed: {str(e)}")

    def _download_thumbnail(self, post, reel_folder: Path, reel_number: int, result: Dict):
        """Download thumbnail image if enabled"""
        if self.download_options.get('thumbnail', True):
            self.progress_updated.emit("", 40, "Downloading thumbnail...")

            thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"

            try:
                # Lazy load requests
                requests_module = lazy_import_requests()
                response = requests_module.get(post.display_url, timeout=30)
                response.raise_for_status()

                with open(thumb_path, 'wb') as f:
                    f.write(response.content)

                result['thumbnail_path'] = str(thumb_path)

            except Exception as e:
                print(f"Thumbnail download failed: {e}")

    def _extract_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Extract audio from video if enabled"""
        if not self.download_options.get('audio', True):
            return

        self.progress_updated.emit("", 60, "Extracting audio...")

        video_path = result.get('video_path') or str(reel_folder / f"video{reel_number}.mp4")

        if not os.path.exists(video_path):
            return

        audio_path = reel_folder / f"audio{reel_number}.mp3"
        video_clip = None
        audio_clip = None

        try:
            # Lazy load moviepy
            VideoFileClip = lazy_import_moviepy()
            video_clip = VideoFileClip(video_path)
            if video_clip.audio is not None:
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(str(audio_path), verbose=False, logger=None)
                result['audio_path'] = str(audio_path)

        except Exception as e:
            print(f"Audio extraction failed: {e}")

        finally:
            # Ensure proper cleanup of video resources
            self._cleanup_video_resources(audio_clip, video_clip)

    def _save_caption(self, post, reel_folder: Path, reel_number: int, result: Dict):
        """Save caption text if enabled"""
        if self.download_options.get('caption', True):
            self.progress_updated.emit("", 80, "Getting caption...")

            caption_text = post.caption or "No caption available"
            result['caption'] = caption_text

            caption_path = reel_folder / f"caption{reel_number}.txt"

            try:
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption_text)
                result['caption_path'] = str(caption_path)

            except Exception as e:
                print(f"Caption save failed: {e}")

    def _transcribe_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Transcribe audio using Whisper if enabled"""
        if not (self.download_options.get('transcribe', False) and self.whisper_model):
            return

        self.progress_updated.emit("", 90, "Transcribing audio...")

        # Use existing audio file or extract temporarily
        audio_source = result.get('audio_path')
        temp_audio_path = None

        if not audio_source:
            audio_source, temp_audio_path = self._extract_temp_audio(reel_folder, reel_number, result)

        if not (audio_source and os.path.exists(audio_source)):
            return

        try:
            transcript_result = self.whisper_model.transcribe(audio_source)
            transcript_text = transcript_result['text']
            result['transcript'] = transcript_text

            transcript_path = reel_folder / f"transcript{reel_number}.txt"
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            result['transcript_path'] = str(transcript_path)

        except Exception as e:
            result['transcript'] = f"Transcription failed: {str(e)}"

        finally:
            # Cleanup temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                self._safe_file_removal(temp_audio_path)

    def _extract_temp_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Extract audio temporarily for transcription"""
        video_path = result.get('video_path') or str(reel_folder / f"video{reel_number}.mp4")
        temp_audio_path = str(reel_folder / f"temp_audio{reel_number}.mp3")

        if not os.path.exists(video_path):
            return None, None

        video_clip = None
        audio_clip = None

        try:
            # Lazy load moviepy
            VideoFileClip = lazy_import_moviepy()
            video_clip = VideoFileClip(video_path)
            if video_clip.audio is not None:
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
                return temp_audio_path, temp_audio_path

        except Exception as e:
            print(f"Temporary audio extraction failed: {e}")

        finally:
            self._cleanup_video_resources(audio_clip, video_clip)

        return None, None

    def _cleanup_video_resources(self, audio_clip, video_clip):
        """Safely cleanup video and audio resources"""
        if audio_clip:
            try:
                audio_clip.close()
            except Exception:
                pass

        if video_clip:
            try:
                video_clip.close()
            except Exception:
                pass

    def _safe_file_removal(self, file_path: str):
        """Safely remove a file with error handling"""
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Could not remove file {file_path}: {e}")

    def _extract_shortcode(self, url: str) -> Optional[str]:
        """
        Extract shortcode from Instagram URL

        Args:
            url: Instagram URL

        Returns:
            Shortcode string or None if invalid
        """
        try:
            if '/reel/' in url:
                return url.split('/reel/')[1].split('/')[0].split('?')[0]
            elif '/p/' in url:
                return url.split('/p/')[1].split('/')[0].split('?')[0]
            return None
        except Exception:
            return None

    def stop(self):
        """Stop the download thread gracefully"""
        self.is_running = False


class InstagramDownloaderGUI(QMainWindow):
    """
    Main GUI application for Instagram Reels downloader

    This class manages the user interface and coordinates between
    the UI components and the download thread.
    """

    def __init__(self):
        super().__init__()
        self.reel_queue: List[ReelItem] = []
        self.download_thread = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface"""
        self._setup_window()
        self._create_main_layout()
        self._setup_status_bar()

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Instagram Media Downloader")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        self.setStyleSheet(self._get_main_style())
        self.create_app_icon()

    def _create_main_layout(self):
        """Create and setup the main application layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Create panels
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        # Setup splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def _setup_status_bar(self):
        """Configure the status bar"""
        self.statusBar().showMessage("Ready to download Instagram Reels")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
                padding: 5px;
                border-top: 1px solid #34495e;
            }
        """)

    def create_app_icon(self):
        """Create a simple app icon programmatically"""
        try:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#667eea"))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw camera icon
            painter.setBrush(QBrush(QColor("white")))
            painter.setPen(QColor("white"))

            # Camera body
            painter.drawRoundedRect(10, 20, 44, 30, 5, 5)

            # Camera lens
            painter.setBrush(QBrush(QColor("#667eea")))
            painter.drawEllipse(20, 28, 24, 24)

            # Camera lens center
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(26, 34, 12, 12)

            painter.end()

            self.setWindowIcon(QIcon(pixmap))

        except Exception as e:
            print(f"Could not create app icon: {e}")

    def _get_panel_style(self):
        """Style for left panel with modern design"""
        return """
        QFrame {
            background-color: #ffffff;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            padding: 1px;
        }
        """

    def _get_danger_button_style(self):
        """Style for danger/delete buttons"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
            border-radius: 10px;
            color: white;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
        }
        QPushButton:hover { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d62c1a, stop:1 #a93226);
        }
        QPushButton:pressed { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c0392b, stop:1 #922b21);
        }
        QPushButton:disabled { 
            background: #bdc3c7; 
            color: #7f8c8d; 
        }
        """

    def _get_success_button_style(self):
        """Style for success/folder buttons"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27ae60, stop:1 #229954);
            border-radius: 10px;
            color: white;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
        }
        QPushButton:hover { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2ecc71, stop:1 #27ae60);
        }
        QPushButton:pressed { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #229954, stop:1 #1e8449);
        }
        QPushButton:disabled { 
            background: #bdc3c7; 
            color: #7f8c8d; 
        }
        """

    def _create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(self._get_panel_style())
        panel.setMaximumWidth(350)
        panel.setMinimumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Add components to left panel
        self._add_title_section(layout)
        self._add_url_input_section(layout)
        self._add_download_options_section(layout)
        self._add_control_buttons_section(layout)
        self._add_progress_section(layout)

        layout.addStretch()

        return panel

    def _add_title_section(self, layout: QVBoxLayout):
        """Add title and subtitle to the layout"""
        title_label = QLabel("Instagram Reels\nDownloader")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Download, Extract & Transcribe")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)

    def _add_url_input_section(self, layout: QVBoxLayout):
        """Add URL input section to the layout"""
        url_group = QGroupBox("📎 Add Reel URL")
        url_group.setStyleSheet(self._get_group_style())
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Instagram Reel URL here...")
        self.url_input.setStyleSheet(self._get_input_style())
        self.url_input.returnPressed.connect(self.add_to_queue)

        self.add_button = ModernButton("➕ Add to Queue")
        self.add_button.clicked.connect(self.add_to_queue)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_button)

        layout.addWidget(url_group)

    def _add_download_options_section(self, layout: QVBoxLayout):
        """Add download options section to the layout"""
        options_group = QGroupBox("⚙️ Download Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        # Create checkboxes for download options
        self.video_check = QCheckBox("📹 Download Video")
        self.video_check.setChecked(True)

        self.thumbnail_check = QCheckBox("🖼️ Download Thumbnail")
        self.thumbnail_check.setChecked(True)

        self.audio_check = QCheckBox("🎵 Extract Audio")
        self.audio_check.setChecked(True)

        self.caption_check = QCheckBox("📝 Get Caption")
        self.caption_check.setChecked(True)

        self.transcribe_check = QCheckBox("🎤 Transcribe Audio")
        self.transcribe_check.setChecked(False)

        # Apply styling and add to layout
        checkboxes = [self.video_check, self.thumbnail_check, self.audio_check,
                      self.caption_check, self.transcribe_check]

        for checkbox in checkboxes:
            checkbox.setStyleSheet(self._get_checkbox_style())
            checkbox.setMinimumHeight(35)
            options_layout.addWidget(checkbox)

        layout.addWidget(options_group)

    def _add_control_buttons_section(self, layout: QVBoxLayout):
        """Add control buttons section to the layout"""
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)

        # Download button
        self.download_button = ModernButton("🚀 Start Download")
        self.download_button.clicked.connect(self.start_download)

        # Clear button
        self.clear_button = ModernButton("🗑️ Clear Queue")
        self.clear_button.clicked.connect(self.clear_queue)
        self.clear_button.setStyleSheet(self._get_danger_button_style())

        # Folder button
        self.folder_button = ModernButton("📁 Open Downloads")
        self.folder_button.clicked.connect(self.open_downloads_folder)
        self.folder_button.setStyleSheet(self._get_success_button_style())

        controls_layout.addWidget(self.download_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.folder_button)

        layout.addLayout(controls_layout)

    def _add_progress_section(self, layout: QVBoxLayout):
        """Add progress section to the layout"""
        progress_group = QGroupBox("📊 Overall Progress")
        progress_group.setStyleSheet(self._get_group_style())
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)

        self.overall_progress = ModernProgressBar()

        self.progress_label = QLabel("Ready to start downloading...")
        self.progress_label.setStyleSheet("""
            color: #2c3e50; 
            font-size: 13px; 
            font-weight: bold; 
            padding: 2px;
        """)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._get_tab_style())

        # Add tabs
        queue_widget = self._create_queue_tab()
        results_widget = self._create_results_tab()

        self.tab_widget.addTab(queue_widget, "📋 Download Queue")
        self.tab_widget.addTab(results_widget, "✅ Results")

        layout.addWidget(self.tab_widget)

        return panel

    def _create_queue_tab(self) -> QWidget:
        """Create the queue management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Download Queue")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(header)

        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet(self._get_list_style())
        self.queue_list.setMinimumHeight(400)

        layout.addWidget(self.queue_list)

        return widget

    def _create_results_tab(self) -> QWidget:
        """Create the results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Download Results")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(header)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setStyleSheet(self._get_text_style())
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(400)

        layout.addWidget(self.results_text)

        return widget

    def add_to_queue(self):
        """Add URL to download queue with validation"""
        url = self.url_input.text().strip()

        # Validate URL input
        if not url:
            return

        if not self._is_valid_instagram_url(url):
            QMessageBox.warning(self, "Invalid URL",
                                "Please enter a valid Instagram Reel URL")
            return

        # Check for duplicate URLs
        for item in self.reel_queue:
            if item.url == url:
                QMessageBox.information(self, "Duplicate URL",
                                        "This URL is already in the queue")
                return

        # Create new reel item and add to queue
        reel_item = ReelItem(url=url)
        self.reel_queue.append(reel_item)

        # Add to UI list with truncated URL display
        display_url = f"🔗 {url[:50]}{'...' if len(url) > 50 else ''}"
        list_item = QListWidgetItem(display_url)
        list_item.setData(Qt.ItemDataRole.UserRole, reel_item)
        self.queue_list.addItem(list_item)

        # Clear input field and update status
        self.url_input.clear()
        self.statusBar().showMessage(f"Added to queue. Total items: {len(self.reel_queue)}")

    def clear_queue(self):
        """Clear the download queue and reset UI"""
        # Prevent clearing during active download
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(self, "Download in Progress",
                                "Cannot clear queue while downloading")
            return

        # Clear all data and reset UI
        self.reel_queue.clear()
        self.queue_list.clear()
        self.results_text.clear()
        self.overall_progress.setValue(0)
        self.progress_label.setText("Ready to start downloading...")
        self.statusBar().showMessage("Queue cleared")

    def start_download(self):
        """Start downloading all items in queue"""
        # Validate queue has items
        if not self.reel_queue:
            QMessageBox.information(self, "Empty Queue",
                                    "Please add some URLs to the queue first")
            return

        # Check if download is already in progress
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.information(self, "Download in Progress",
                                    "Download is already in progress")
            return

        # Collect download options from checkboxes
        options = {
            'video': self.video_check.isChecked(),
            'thumbnail': self.thumbnail_check.isChecked(),
            'audio': self.audio_check.isChecked(),
            'caption': self.caption_check.isChecked(),
            'transcribe': self.transcribe_check.isChecked()
        }

        # Create and configure download thread
        self.download_thread = ReelDownloader(self.reel_queue.copy(), options)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_completed.connect(self.download_completed)
        self.download_thread.error_occurred.connect(self.download_error)
        self.download_thread.finished.connect(self.download_finished)

        # Start download and update UI
        self.download_thread.start()
        self.download_button.setEnabled(False)
        self.download_button.setText("⏳ Downloading...")
        self.statusBar().showMessage("Download started...")

    def update_progress(self, url: str, progress: int, status: str):
        """Update progress display for downloads"""
        if url:  # Update individual item progress
            # Find and update the specific queue item
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                reel_item = item.data(Qt.ItemDataRole.UserRole)
                if reel_item.url == url:
                    # Update reel item data
                    reel_item.progress = progress
                    reel_item.status = status

                    # Update display text
                    url_short = url[:40] + '...' if len(url) > 40 else url
                    if progress == 100:
                        item.setText(f"✅ {url_short} - {status}")
                    else:
                        item.setText(f"📥 {url_short} - {status} ({progress}%)")
                    break
        else:  # Update overall status
            self.progress_label.setText(status)

        # Calculate and update overall progress bar
        if self.reel_queue:
            total_progress = sum(item.progress for item in self.reel_queue)
            overall_progress = total_progress // len(self.reel_queue)
            self.overall_progress.setValue(overall_progress)

    def download_completed(self, url: str, result_data: Dict[str, Any]):
        """Handle successful download completion"""
        # Update reel item with results
        for item in self.reel_queue:
            if item.url == url:
                item.status = "Completed"
                item.progress = 100
                item.title = result_data.get('title', 'Unknown')
                item.video_path = result_data.get('video_path', '')
                item.audio_path = result_data.get('audio_path', '')
                item.thumbnail_path = result_data.get('thumbnail_path', '')
                item.caption = result_data.get('caption', '')
                item.transcript = result_data.get('transcript', '')
                item.folder_path = result_data.get('folder_path', '')
                break

        # Add results to results tab
        self._add_to_results(url, result_data)

        # Update queue list display
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + '...' if len(url) > 40 else url
                list_item.setText(f"✅ {url_short} - Completed")
                break

    def download_error(self, url: str, error_message: str):
        """Handle download errors"""
        # Update reel item with error info
        for item in self.reel_queue:
            if item.url == url:
                item.status = "Error"
                item.error_message = error_message
                break

        # Add error to results display
        self.results_text.append(f"\n❌ ERROR for {url}:\n{error_message}\n" + "=" * 60)

        # Update queue list display
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + '...' if len(url) > 40 else url
                list_item.setText(f"❌ {url_short} - Error")
                break

    def download_finished(self):
        """Handle download thread completion"""
        # Reset download button state
        self.download_button.setEnabled(True)
        self.download_button.setText("🚀 Start Download")
        self.overall_progress.setValue(100)
        self.progress_label.setText("All downloads completed!")
        self.statusBar().showMessage("All downloads completed")

        # Show completion summary
        completed = sum(1 for item in self.reel_queue if item.status == "Completed")
        total = len(self.reel_queue)

        QMessageBox.information(self, "Download Complete",
                                f"Completed {completed}/{total} downloads\n\n"
                                f"Files are organized in individual reel folders")

    def _add_to_results(self, url: str, result_data: Dict[str, Any]):
        """Add download results to results tab"""
        result_text = f"\n✅ COMPLETED: {url}\n"
        result_text += f"Title: {result_data.get('title', 'N/A')}\n"

        # Add file paths to results
        if 'video_path' in result_data:
            result_text += f"📹 Video: {result_data['video_path']}\n"
        if 'thumbnail_path' in result_data:
            result_text += f"🖼️ Thumbnail: {result_data['thumbnail_path']}\n"
        if 'audio_path' in result_data:
            result_text += f"🎵 Audio: {result_data['audio_path']}\n"
        if 'caption_path' in result_data:
            result_text += f"📝 Caption: {result_data['caption_path']}\n"
        if 'transcript_path' in result_data:
            result_text += f"🎤 Transcript: {result_data['transcript_path']}\n"

        result_text += "=" * 50
        self.results_text.append(result_text)

        # Switch to results tab to show completion
        self.tab_widget.setCurrentIndex(1)

    def open_downloads_folder(self):
        """Open the downloads folder in system file manager"""
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)

        import subprocess
        import platform

        try:
            # Open folder based on operating system
            if platform.system() == "Windows":
                os.startfile(str(download_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(download_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(download_dir)])
        except Exception:
            # Fallback: show folder path in message box
            QMessageBox.information(self, "Downloads Folder",
                                    f"Downloads are saved to: {download_dir.absolute()}")

    def _is_valid_instagram_url(self, url: str) -> bool:
        """Validate if URL is a valid Instagram reel/post URL"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc in ['instagram.com', 'www.instagram.com'] and
                    ('/reel/' in url or '/p/' in url))
        except:
            return False

    def load_settings(self):
        """Load application settings from JSON file"""
        try:
            settings_file = Path("settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                # Apply saved settings to checkboxes
                self.video_check.setChecked(settings.get('video', True))
                self.thumbnail_check.setChecked(settings.get('thumbnail', True))
                self.audio_check.setChecked(settings.get('audio', True))
                self.caption_check.setChecked(settings.get('caption', True))
                self.transcribe_check.setChecked(settings.get('transcribe', False))

        except Exception as e:
            print(f"Could not load settings: {e}")

    def save_settings(self):
        """Save application settings to JSON file"""
        try:
            settings = {
                'video': self.video_check.isChecked(),
                'thumbnail': self.thumbnail_check.isChecked(),
                'audio': self.audio_check.isChecked(),
                'caption': self.caption_check.isChecked(),
                'transcribe': self.transcribe_check.isChecked()
            }

            with open("settings.json", 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            print(f"Could not save settings: {e}")

    def closeEvent(self, event):
        """Handle application close event"""
        # Stop download thread if running
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(5000)  # Wait up to 5 seconds

        # Save current settings
        self.save_settings()
        event.accept()

    # =============================================================================
    # STYLE METHODS - UI Styling and Appearance
    # =============================================================================

    def _get_main_style(self):
        """Main window gradient background style"""
        return """
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #2c3e50, stop: 1 #34495e);
            color: #ecf0f1;
        }
        """

    def _get_group_style(self):
        """Style for group boxes with rounded borders"""
        return """
        QGroupBox {
            font-weight: bold;
            font-size: 15px;
            color: #2c3e50;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            background-color: #ffffff;
        }
        """

    def _get_input_style(self):
        """Style for input fields with focus states"""
        return """
        QLineEdit {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 14px;
            background-color: #ffffff;
            color: #2c3e50;
            min-height: 20px;
        }
        QLineEdit:focus {
            border-color: #667eea;
            outline: none;
        }
        QLineEdit::placeholder {
            color: #95a5a6;
        }
        """

    def _get_checkbox_style(self):
        """Style for checkboxes with custom indicators"""
        return """
        QCheckBox {
            font-size: 14px;
            color: #2c3e50;
            padding: 8px 5px;
            spacing: 10px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            border: 2px solid #667eea;
            border-radius: 4px;
            background-color: #667eea;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMiAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDJMNC41IDhMMiA1LjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
        }
        QCheckBox::indicator:hover {
            border-color: #667eea;
        }
        """

    def _get_tab_style(self):
        """Style for tab widget with rounded corners"""
        return """
        QTabWidget::pane {
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            background-color: #ffffff;
            padding: 10px;
        }
        QTabBar::tab {
            background: #ecf0f1;
            border: 2px solid #bdc3c7;
            padding: 15px 25px;
            margin-right: 3px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            min-width: 100px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom-color: #ffffff;
            color: #667eea;
        }
        QTabBar::tab:hover:!selected {
            background: #d5dbdb;
        }
        """

    def _get_list_style(self):
        """Style for list widgets with hover effects"""
        return """
        QListWidget {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            font-size: 14px;
            padding: 8px;
            color: #2c3e50;
        }
        QListWidget::item {
            padding: 12px 8px;
            border-bottom: 1px solid #ecf0f1;
            border-radius: 4px;
            margin: 2px 0;
        }
        QListWidget::item:selected {
            background-color: #667eea;
            color: #ffffff;
            border: none;
        }
        QListWidget::item:hover {
            background-color: #f1f2f6;
        }
        """

    def _get_text_style(self):
        """Style for text edit widgets with monospace font"""
        return """
        QTextEdit {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            padding: 15px;
            color: #2c3e50;
            line-height: 1.4;
        }
        """


def main():
    """Main application entry point"""
    # Create application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Instagram Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("UKR-PROJECTS")
    app.setStyle('Fusion')

    # Set global application style
    app.setStyleSheet("""
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
    """)

    # Create and show main window
    window = InstagramDownloaderGUI()
    window.show()

    # Start application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
"""
Instagram Media Downloader with Queue Management
A professional PyQt6 application for downloading Instagram Reels with transcription
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

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QListWidget, QListWidgetItem, QTabWidget, QFrame, QScrollArea,
    QGridLayout, QSpacerItem, QSizePolicy, QMessageBox, QFileDialog,
    QComboBox, QCheckBox, QGroupBox, QSplitter
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPalette, QColor, QIcon, QPainter,
    QBrush, QLinearGradient
)

# Third-party imports
try:
    import instaloader
    from moviepy.editor import VideoFileClip
    import whisper
    import requests
    from PIL import Image
except ImportError as e:
    print(f"Missing required packages. Please install: {e}")
    sys.exit(1)

@dataclass
class ReelItem:
    """Data class for reel download items"""
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
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(self._style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setFont(QFont("Arial", 9))

    def _style(self):
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
            color: white;
            padding: 8px 16px;
            font-size: 11px;
        }
        QPushButton:hover { opacity: 0.9; }
        QPushButton:pressed { opacity: 0.8; }
        QPushButton:disabled { background: #bdc3c7; color: #7f8c8d; }
        """

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
        QProgressBar {
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            text-align: center;
            background-color: #f8f9fa;
            font-size: 10px;
            color: #2c3e50;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            margin: 1px;
        }
        """)

class ReelDownloader(QThread):
    """Thread for downloading Instagram reels"""

    progress_updated = pyqtSignal(str, int, str)  # url, progress, status
    download_completed = pyqtSignal(str, dict)  # url, result_data
    error_occurred = pyqtSignal(str, str)  # url, error_message

    def __init__(self, reel_items: List[ReelItem], download_options: Dict[str, bool]):
        super().__init__()
        self.reel_items = reel_items
        self.download_options = download_options
        self.is_running = True

    def run(self):
        """Main download thread execution"""
        try:
            # Create session folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_folder = Path("downloads") / f"session_{timestamp}"
            self.session_folder.mkdir(parents=True, exist_ok=True)

            # Load Whisper model if transcription is enabled
            if self.download_options.get('transcribe', False):
                self.progress_updated.emit("", 0, "Loading Whisper model...")
                self.whisper_model = whisper.load_model("base")

            # Create instaloader instance
            loader = instaloader.Instaloader(
                download_video_thumbnails=True,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                dirname_pattern=str(self.session_folder)
            )

            for i, item in enumerate(self.reel_items):
                if not self.is_running:
                    break

                try:
                    self.progress_updated.emit(item.url, 0, "Starting download...")
                    result = self._download_reel(loader, item, i + 1)
                    self.download_completed.emit(item.url, result)

                except Exception as e:
                    error_msg = f"Download failed: {str(e)}"
                    self.error_occurred.emit(item.url, error_msg)

        except Exception as e:
            self.error_occurred.emit("", f"Thread error: {str(e)}")

    def _download_reel(self, loader: instaloader.Instaloader, item: ReelItem, reel_number: int) -> Dict[str, Any]:
        """Download individual reel and process it"""
        result = {}
        temp_video_path = None

        try:
            # Extract shortcode from URL
            shortcode = self._extract_shortcode(item.url)
            if not shortcode:
                raise ValueError("Invalid Instagram URL")

            self.progress_updated.emit(item.url, 10, "Fetching reel data...")

            # Get post
            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            # Create reel folder
            reel_folder = self.session_folder / f"reel{reel_number}"
            reel_folder.mkdir(exist_ok=True)
            result['folder_path'] = str(reel_folder)

            # Check if we need video for audio extraction or transcription
            need_video_for_audio = (self.download_options.get('audio', False) or
                                    self.download_options.get('transcribe', False))

            # Download video (either permanently or temporarily)
            if self.download_options.get('video', True) or need_video_for_audio:
                self.progress_updated.emit(item.url, 20, "Downloading video...")

                if self.download_options.get('video', True):
                    # Permanent video download
                    video_path = reel_folder / f"video{reel_number}.mp4"
                    with open(video_path, 'wb') as f:
                        f.write(requests.get(post.video_url).content)
                    result['video_path'] = str(video_path)
                else:
                    # Temporary video download for audio extraction
                    temp_video_path = reel_folder / f"temp_video{reel_number}.mp4"
                    with open(temp_video_path, 'wb') as f:
                        f.write(requests.get(post.video_url).content)

            self.progress_updated.emit(item.url, 40, "Downloading thumbnail...")

            # Download thumbnail
            if self.download_options.get('thumbnail', True):
                thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"
                with open(thumb_path, 'wb') as f:
                    # Fixed: Use display_url instead of url for thumbnail
                    f.write(requests.get(post.display_url).content)
                result['thumbnail_path'] = str(thumb_path)

            self.progress_updated.emit(item.url, 60, "Extracting audio...")

            # Extract audio
            if self.download_options.get('audio', True):
                audio_path = reel_folder / f"audio{reel_number}.mp3"
                video_clip = None
                audio_clip = None
                try:
                    # Use either permanent video or temp video
                    video_source = result.get('video_path') or str(temp_video_path)

                    if video_source and os.path.exists(video_source):
                        video_clip = VideoFileClip(video_source)
                        if video_clip.audio is not None:
                            audio_clip = video_clip.audio
                            audio_clip.write_audiofile(str(audio_path), verbose=False, logger=None)
                            result['audio_path'] = str(audio_path)
                except Exception as e:
                    print(f"Audio extraction failed: {e}")
                finally:
                    # Proper resource cleanup
                    if audio_clip:
                        try:
                            audio_clip.close()
                        except:
                            pass
                    if video_clip:
                        try:
                            video_clip.close()
                        except:
                            pass

            self.progress_updated.emit(item.url, 80, "Getting caption...")

            # Get caption and save to file
            if self.download_options.get('caption', True):
                caption_text = post.caption or "No caption available"
                result['caption'] = caption_text

                caption_path = reel_folder / f"caption{reel_number}.txt"
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption_text)
                result['caption_path'] = str(caption_path)

            self.progress_updated.emit(item.url, 90, "Transcribing audio...")

            # Transcribe audio and save to file
            if (self.download_options.get('transcribe', False) and self.whisper_model):
                video_clip = None
                audio_clip = None
                temp_audio_path = None
                try:
                    # Use audio file if available, otherwise extract from video temporarily
                    audio_source = result.get('audio_path')

                    if not audio_source:
                        # Extract audio temporarily for transcription
                        temp_audio_path = reel_folder / f"temp_audio{reel_number}.mp3"
                        video_source = result.get('video_path') or str(temp_video_path)

                        if video_source and os.path.exists(video_source):
                            video_clip = VideoFileClip(video_source)
                            if video_clip.audio is not None:
                                audio_clip = video_clip.audio
                                audio_clip.write_audiofile(str(temp_audio_path), verbose=False, logger=None)
                                audio_source = str(temp_audio_path)

                    if audio_source and os.path.exists(audio_source):
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
                    # Proper resource cleanup
                    if audio_clip:
                        try:
                            audio_clip.close()
                        except:
                            pass
                    if video_clip:
                        try:
                            video_clip.close()
                        except:
                            pass
                    # Clean up temporary audio file if it was created
                    if temp_audio_path and os.path.exists(str(temp_audio_path)):
                        try:
                            os.remove(str(temp_audio_path))
                        except OSError:
                            pass

            self.progress_updated.emit(item.url, 100, "Completed")
            result['title'] = f"Reel {reel_number}"

        except Exception as e:
            raise Exception(f"Download error: {str(e)}")
        finally:
            # Clean up temporary video file if it was created
            if temp_video_path and os.path.exists(str(temp_video_path)):
                try:
                    os.remove(str(temp_video_path))
                except OSError:
                    pass

        return result

    def _extract_shortcode(self, url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        try:
            if '/reel/' in url:
                return url.split('/reel/')[1].split('/')[0].split('?')[0]
            elif '/p/' in url:
                return url.split('/p/')[1].split('/')[0].split('?')[0]
            return None
        except:
            return None

    def stop(self):
        """Stop the download thread"""
        self.is_running = False


class InstagramDownloaderGUI(QMainWindow):
    """Main GUI application for Instagram Reels downloader"""

    def __init__(self):
        super().__init__()
        self.reel_queue: List[ReelItem] = []
        self.download_thread = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("Instagram Media Downloader")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        self.setStyleSheet(self._get_main_style())

        self.create_app_icon()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        left_panel = self._create_left_panel()
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)

        right_panel = self._create_right_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        self.statusBar().showMessage("Ready to download Instagram Reels")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
        """)

    def create_app_icon(self):
        """Create a simple app icon"""
        try:
            # Create a simple icon programmatically
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#667eea"))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw a simple camera icon
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

            icon = QIcon(pixmap)
            self.setWindowIcon(icon)
        except Exception as e:
            print(f"Could not create app icon: {e}")

    def _create_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #ecf0f1;
            }
            """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(1)

        title_label = QLabel("Instagram Reels\nDownloader")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Download, Extract & Transcribe")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(subtitle_label)

        url_group = QGroupBox("📎 Add Reel URL")
        url_group.setStyleSheet(self._get_group_style())
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Instagram Reel URL here...")
        self.url_input.setStyleSheet(self._get_input_style())
        self.url_input.returnPressed.connect(self.add_to_queue)
        # Removed redundant setMinimumHeight

        self.add_button = ModernButton("➕ Add to Queue")
        self.add_button.clicked.connect(self.add_to_queue)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_button)

        layout.addWidget(url_group)

        # Download options
        options_group = QGroupBox("⚙️ Download Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)  # Fixed spacing between options

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

        for checkbox in [self.video_check, self.thumbnail_check, self.audio_check,
                         self.caption_check, self.transcribe_check]:
            checkbox.setStyleSheet(self._get_checkbox_style())
            checkbox.setMinimumHeight(35)
            options_layout.addWidget(checkbox)

        layout.addWidget(options_group)

        # Control buttons
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(20)

        self.download_button = ModernButton("🚀 Start Download")
        self.download_button.clicked.connect(self.start_download)

        self.clear_button = ModernButton("🗑️ Clear Queue")
        self.clear_button.clicked.connect(self.clear_queue)
        self.clear_button.setStyleSheet(self.clear_button.styleSheet().replace(
            "#667eea", "#e74c3c").replace("#764ba2", "#c0392b"))

        self.folder_button = ModernButton("📁 Open Downloads")
        self.folder_button.clicked.connect(self.open_downloads_folder)
        self.folder_button.setStyleSheet(self.folder_button.styleSheet().replace(
            "#667eea", "#27ae60").replace("#764ba2", "#229954"))

        controls_layout.addWidget(self.download_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.folder_button)

        layout.addLayout(controls_layout)

        # Progress section
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

        layout.addStretch()

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self._get_tab_style())

        # Queue tab
        queue_widget = self._create_queue_tab()
        self.tab_widget.addTab(queue_widget, "📋 Download Queue")

        # Results tab
        results_widget = self._create_results_tab()
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

        # Queue list - removed setAlternatingRowColors
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet(self._get_list_style())
        self.queue_list.setMinimumHeight(400)

        layout.addWidget(self.queue_list)

        return widget

    # Fixed closeEvent method - increase wait time
    def closeEvent(self, event):
        """Handle application close"""
        # Stop download thread if running
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(5000)  # Wait 5 seconds instead of 3

        # Save settings
        self.save_settings()

        event.accept()

    def _create_results_tab(self) -> QWidget:
        """Create the results tab"""
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
        """Add URL to download queue"""
        url = self.url_input.text().strip()

        if not url:
            return

        if not self._is_valid_instagram_url(url):
            QMessageBox.warning(self, "Invalid URL",
                                "Please enter a valid Instagram Reel URL")
            return

        # Check if URL already exists
        for item in self.reel_queue:
            if item.url == url:
                QMessageBox.information(self, "Duplicate URL",
                                        "This URL is already in the queue")
                return

        # Add to queue
        reel_item = ReelItem(url=url)
        self.reel_queue.append(reel_item)

        # Add to UI list
        list_item = QListWidgetItem(f"🔗 {url[:50]}{'...' if len(url) > 50 else ''}")
        list_item.setData(Qt.ItemDataRole.UserRole, reel_item)
        self.queue_list.addItem(list_item)

        # Clear input
        self.url_input.clear()

        # Update status
        self.statusBar().showMessage(f"Added to queue. Total items: {len(self.reel_queue)}")

    def clear_queue(self):
        """Clear the download queue"""
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(self, "Download in Progress",
                                "Cannot clear queue while downloading")
            return

        self.reel_queue.clear()
        self.queue_list.clear()
        self.results_text.clear()
        self.overall_progress.setValue(0)
        self.progress_label.setText("Ready to start downloading...")
        self.statusBar().showMessage("Queue cleared")

    def start_download(self):
        """Start downloading all items in queue"""
        if not self.reel_queue:
            QMessageBox.information(self, "Empty Queue",
                                    "Please add some URLs to the queue first")
            return

        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.information(self, "Download in Progress",
                                    "Download is already in progress")
            return

        # Get download options
        options = {
            'video': self.video_check.isChecked(),
            'thumbnail': self.thumbnail_check.isChecked(),
            'audio': self.audio_check.isChecked(),
            'caption': self.caption_check.isChecked(),
            'transcribe': self.transcribe_check.isChecked()
        }

        # Create and start download thread
        self.download_thread = ReelDownloader(self.reel_queue.copy(), options)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_completed.connect(self.download_completed)
        self.download_thread.error_occurred.connect(self.download_error)
        self.download_thread.finished.connect(self.download_finished)

        self.download_thread.start()

        # Update UI
        self.download_button.setEnabled(False)
        self.download_button.setText("⏳ Downloading...")
        self.statusBar().showMessage("Download started...")

    def update_progress(self, url: str, progress: int, status: str):
        """Update progress for specific URL"""
        # Update overall progress
        if url:  # Individual item progress
            # Find and update the specific item
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                reel_item = item.data(Qt.ItemDataRole.UserRole)
                if reel_item.url == url:
                    reel_item.progress = progress
                    reel_item.status = status
                    url_short = url[:40] + '...' if len(url) > 40 else url
                    if progress == 100:
                        item.setText(f"✅ {url_short} - {status}")
                    else:
                        item.setText(f"📥 {url_short} - {status} ({progress}%)")
                    break
        else:  # Overall status
            self.progress_label.setText(status)

        # Calculate overall progress
        if self.reel_queue:
            total_progress = sum(item.progress for item in self.reel_queue)
            overall_progress = total_progress // len(self.reel_queue)
            self.overall_progress.setValue(overall_progress)

    def download_completed(self, url: str, result_data: Dict[str, Any]):
        """Handle completed download"""
        # Update reel item
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

        # Add to results
        self._add_to_results(url, result_data)

        # Update queue list
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + '...' if len(url) > 40 else url
                list_item.setText(f"✅ {url_short} - Completed")
                break

    def download_error(self, url: str, error_message: str):
        """Handle download error"""
        # Update reel item
        for item in self.reel_queue:
            if item.url == url:
                item.status = "Error"
                item.error_message = error_message
                break

        # Add error to results
        self.results_text.append(f"\n❌ ERROR for {url}:\n{error_message}\n" + "=" * 60)

        # Update queue list
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + '...' if len(url) > 40 else url
                list_item.setText(f"❌ {url_short} - Error")
                break

    def download_finished(self):
        """Handle download thread completion"""
        self.download_button.setEnabled(True)
        self.download_button.setText("🚀 Start Download")
        self.overall_progress.setValue(100)
        self.progress_label.setText("All downloads completed!")
        self.statusBar().showMessage("All downloads completed")

        # Show completion message
        completed = sum(1 for item in self.reel_queue if item.status == "Completed")
        total = len(self.reel_queue)

        QMessageBox.information(self, "Download Complete",
                                f"Completed {completed}/{total} downloads\n\n"
                                f"Files are organized in individual reel folders")

    def _add_to_results(self, url: str, result_data: Dict[str, Any]):
        """Add download results to results tab"""
        result_text = f"\n✅ COMPLETED: {url}\n"
        result_text += f"Title: {result_data.get('title', 'N/A')}\n"

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

        # Switch to results tab
        self.tab_widget.setCurrentIndex(1)

    def open_downloads_folder(self):
        """Open the downloads folder"""
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)

        import subprocess
        import platform

        try:
            if platform.system() == "Windows":
                os.startfile(str(download_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(download_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(download_dir)])
        except Exception as e:
            QMessageBox.information(self, "Downloads Folder",
                                    f"Downloads are saved to: {download_dir.absolute()}")

    def _is_valid_instagram_url(self, url: str) -> bool:
        """Validate Instagram URL"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc in ['instagram.com', 'www.instagram.com'] and
                    ('/reel/' in url or '/p/' in url))
        except:
            return False

    def load_settings(self):
        """Load application settings"""
        try:
            settings_file = Path("settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

                # Apply settings
                self.video_check.setChecked(settings.get('video', True))
                self.thumbnail_check.setChecked(settings.get('thumbnail', True))
                self.audio_check.setChecked(settings.get('audio', True))
                self.caption_check.setChecked(settings.get('caption', True))
                self.transcribe_check.setChecked(settings.get('transcribe', False))

        except Exception as e:
            print(f"Could not load settings: {e}")

    def save_settings(self):
        """Save application settings"""
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
        """Handle application close"""
        # Stop download thread if running
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(5000)  # Wait 5 seconds instead of 3

        # Save settings
        self.save_settings()

        event.accept()

    # Style methods
    def _get_main_style(self):
        return """
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #2c3e50, stop: 1 #34495e);
            color: #ecf0f1;
        }
        """

    def _get_group_style(self):
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
        return """
        QListWidget {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
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
    app = QApplication(sys.argv)
    app.setApplicationName("Instagram Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ReelsDownloader")
    app.setStyle('Fusion')
    # Global QSS unchanged (no unsupported props)
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
    window = InstagramDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

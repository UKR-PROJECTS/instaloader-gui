"""
Instagram Reels Downloader GUI

This module implements the main window for a PyQt6-based desktop application
that allows users to download Instagram Reels (and optionally posts) with a modern,
user-friendly interface. The GUI provides features such as:

- Adding Instagram Reel URLs to a download queue with validation and duplicate checks.
- Selecting download options: video, thumbnail, audio extraction, and caption retrieval.
- Managing and displaying the download queue and results in tabbed panels.
- Visual feedback with progress bars, status messages, and styled controls.
- Saving and loading user preferences for download options.
- Opening the downloads folder directly from the application.
- Graceful handling of download errors and application shutdown.

The application coordinates between UI components and a background download thread,
and uses custom-styled widgets for a modern look and feel.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

from src.core.data_models import ReelItem
from src.core.downloader import ReelDownloader
from src.ui.components import ModernButton, ModernProgressBar
from src.updater import check_for_updates

# PyQt6 imports (these are fast to import)
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QFrame,
    QMessageBox,
    QCheckBox,
    QGroupBox,
    QSplitter,
    QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QColor, QIcon, QPainter, QBrush


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
        QTimer.singleShot(1000, check_for_updates)  # Check for updates after 1 second

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
        self.statusBar().setStyleSheet(
            """
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
                padding: 5px;
                border-top: 1px solid #34495e;
            }
        """
        )

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
        self._add_downloader_selection_section(layout)
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

    def _add_downloader_selection_section(self, layout: QVBoxLayout):
        """Add downloader selection section to the layout"""
        downloader_group = QGroupBox("⬇️ Downloader")
        downloader_group.setStyleSheet(self._get_group_style())
        downloader_layout = QVBoxLayout(downloader_group)
        downloader_layout.setSpacing(10)

        self.downloader_combo = QComboBox()
        self.downloader_combo.addItems(["Instaloader", "yt-dlp"])
        self.downloader_combo.setStyleSheet(self._get_combo_box_style())

        downloader_layout.addWidget(self.downloader_combo)
        downloader_group.setLayout(downloader_layout)
        layout.addWidget(downloader_group)

    def _add_download_options_section(self, layout: QVBoxLayout):
        """Add download options section to the layout"""
        options_group = QGroupBox("⚙️ Download Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(5)

        # Create checkboxes for download options
        self.video_check = QCheckBox("📹 Download Video")
        self.video_check.setChecked(True)

        self.thumbnail_check = QCheckBox("🖼️ Download Thumbnail")
        self.thumbnail_check.setChecked(True)

        self.audio_check = QCheckBox("🎵 Extract Audio")
        self.audio_check.setChecked(True)

        self.caption_check = QCheckBox("📝 Get Caption")
        self.caption_check.setChecked(True)

        # Apply styling and add to layout
        checkboxes = [
            self.video_check,
            self.thumbnail_check,
            self.audio_check,
            self.caption_check,
        ]

        for checkbox in checkboxes:
            checkbox.setStyleSheet(self._get_checkbox_style())
            checkbox.setMinimumHeight(25)
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
        self.progress_label.setStyleSheet(
            """
            color: #2c3e50; 
            font-size: 13px; 
            font-weight: bold; 
            padding: 2px;
        """
        )
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
            QMessageBox.warning(
                self, "Invalid URL", "Please enter a valid Instagram Reel URL"
            )
            return

        # Check for duplicate URLs
        for item in self.reel_queue:
            if item.url == url:
                QMessageBox.information(
                    self, "Duplicate URL", "This URL is already in the queue"
                )
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
        self.statusBar().showMessage(
            f"Added to queue. Total items: {len(self.reel_queue)}"
        )

    def clear_queue(self):
        """Clear the download queue and reset UI"""
        # Prevent clearing during active download
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(
                self, "Download in Progress", "Cannot clear queue while downloading"
            )
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
            QMessageBox.information(
                self, "Empty Queue", "Please add some URLs to the queue first"
            )
            return

        # Check if download is already in progress
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.information(
                self, "Download in Progress", "Download is already in progress"
            )
            return

        # Collect download options from checkboxes
        options = {
            "video": self.video_check.isChecked(),
            "thumbnail": self.thumbnail_check.isChecked(),
            "audio": self.audio_check.isChecked(),
            "caption": self.caption_check.isChecked(),
            "downloader": self.downloader_combo.currentText(),
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
                    url_short = url[:40] + "..." if len(url) > 40 else url
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
                item.title = result_data.get("title", "Unknown")
                item.video_path = result_data.get("video_path", "")
                item.audio_path = result_data.get("audio_path", "")
                item.thumbnail_path = result_data.get("thumbnail_path", "")
                item.caption = result_data.get("caption", "")
                item.folder_path = result_data.get("folder_path", "")
                break

        # Add results to results tab
        self._add_to_results(url, result_data)

        # Update queue list display
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + "..." if len(url) > 40 else url
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
                url_short = url[:40] + "..." if len(url) > 40 else url
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

        QMessageBox.information(
            self,
            "Download Complete",
            f"Completed {completed}/{total} downloads\n\n"
            f"Files are organized in individual reel folders",
        )

    def _add_to_results(self, url: str, result_data: Dict[str, Any]):
        """Add download results to results tab"""
        result_text = f"\n✅ COMPLETED: {url}\n"
        result_text += f"Title: {result_data.get('title', 'N/A')}\n"

        # Add file paths to results
        if "video_path" in result_data:
            result_text += f"📹 Video: {result_data['video_path']}\n"
        if "thumbnail_path" in result_data:
            result_text += f"🖼️ Thumbnail: {result_data['thumbnail_path']}\n"
        if "audio_path" in result_data:
            result_text += f"🎵 Audio: {result_data['audio_path']}\n"
        if "caption_path" in result_data:
            result_text += f"📝 Caption: {result_data['caption_path']}\n"

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
            QMessageBox.information(
                self,
                "Downloads Folder",
                f"Downloads are saved to: {download_dir.absolute()}",
            )

    def _is_valid_instagram_url(self, url: str) -> bool:
        """Validate if URL is a valid Instagram reel/post URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc in ["instagram.com", "www.instagram.com"] and (
                "/reel/" in url or "/p/" in url
            )
        except:
            return False

    def load_settings(self):
        """Load application settings from JSON file"""
        try:
            settings_file = Path("settings.json")
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    settings = json.load(f)

                # Apply saved settings to checkboxes
                self.video_check.setChecked(settings.get("video", True))
                self.thumbnail_check.setChecked(settings.get("thumbnail", True))
                self.audio_check.setChecked(settings.get("audio", True))
                self.caption_check.setChecked(settings.get("caption", True))
                self.downloader_combo.setCurrentText(
                    settings.get("downloader", "Instaloader")
                )

        except Exception as e:
            print(f"Could not load settings: {e}")

    def save_settings(self):
        """Save application settings to JSON file"""
        try:
            settings = {
                "video": self.video_check.isChecked(),
                "thumbnail": self.thumbnail_check.isChecked(),
                "audio": self.audio_check.isChecked(),
                "caption": self.caption_check.isChecked(),
                "downloader": self.downloader_combo.currentText(),
            }

            with open("settings.json", "w") as f:
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
            background-color: #ffffff;
            margin-top: 3px;
            padding-top: 3px;            
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
        }
        QCheckBox::indicator {
            width: 10px;
            height: 10px;
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

    def _get_combo_box_style(self):
        """Style for QComboBox"""
        return """
        QComboBox {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 14px;
            background-color: #ffffff;
            color: #2c3e50;
            min-height: 20px;
        }
        QComboBox:focus {
            border-color: #667eea;
            outline: none;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDYiIHN0cm9rZT0iIzJjM2U1MCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            width: 16px;
            height: 16px;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2c3e50;
            selection-background-color: #667eea;
        }
        """

"""
Instagram Reels Downloader GUI

This module implements the main window for a PyQt6-based desktop application
that allows users to download Instagram Reels (and optionally posts) with
various options such as downloading video, thumbnail, extracting audio,
getting captions, and transcribing audio.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import platform

from src.core.data_models import ReelItem
from src.core.downloader import ReelDownloader
from src.updater import check_for_updates
from src.ui.styles import AppStyles
from src.core.settings_manager import SettingsManager
from src.utils.url_validator import is_valid_instagram_url
from src.ui.panel_builder import PanelBuilder

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon


class InstagramDownloaderGUI(QMainWindow):
    """
    Main GUI application for Instagram Reels downloader.

    This class manages the user interface, handles user interactions,
    and coordinates between the UI components and the background download thread.
    It provides features for adding URLs to a queue, selecting download options,
    monitoring progress, and managing application settings.
    """

    def __init__(self):
        """
        Initializes the InstagramDownloaderGUI window.

        Sets up the download queue, initializes managers for settings and UI panels,
        and calls methods to set up the user interface and load previous settings.
        """
        super().__init__()
        self.reel_queue: List[ReelItem] = []
        self.download_thread = None
        self.settings_manager = SettingsManager()
        self.panel_builder = PanelBuilder(self)
        self.ui_elements = {}  # To store references to UI elements

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """
        Initializes the main user interface components of the application.

        This includes setting up the main window properties, creating the layout,
        configuring the status bar, and scheduling an update check.
        """
        self._setup_window()
        self._create_main_layout()
        self._setup_status_bar()
        # Check for updates after 1 second to allow UI to load
        QTimer.singleShot(1000, check_for_updates)

    def _setup_window(self):
        """
        Configures the main window properties.

        Sets the window title, minimum size, initial size, stylesheet,
        and application icon.
        """
        self.setWindowTitle("Instagram Media Downloader")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        self.setStyleSheet(AppStyles.get_main_style())
        self.create_app_icon()

    def _create_main_layout(self):
        """
        Creates and sets up the main application layout.

        This method uses `PanelBuilder` to construct the various UI panels
        and then assigns references to key UI elements for easier access
        within the class.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.panel_builder.create_main_layout(central_widget)
        self.ui_elements = self.panel_builder.get_ui_elements()

        # Assign UI elements to self for easier access
        self.url_input = self.ui_elements["url_input"]
        self.add_button = self.ui_elements["add_button"]
        self.downloader_combo = self.ui_elements["downloader_combo"]
        self.video_check = self.ui_elements["video_check"]
        self.thumbnail_check = self.ui_elements["thumbnail_check"]
        self.audio_check = self.ui_elements["audio_check"]
        self.caption_check = self.ui_elements["caption_check"]
        self.transcribe_check = self.ui_elements["transcribe_check"]
        self.download_button = self.ui_elements["download_button"]
        self.clear_button = self.ui_elements["clear_button"]
        self.folder_button = self.ui_elements["folder_button"]
        self.overall_progress = self.ui_elements["overall_progress"]
        self.progress_label = self.ui_elements["progress_label"]
        self.queue_list = self.ui_elements["queue_list"]
        self.results_text = self.ui_elements["results_text"]
        self.tab_widget = self.ui_elements["tab_widget"]

    def _setup_status_bar(self):
        """
        Configures the application's status bar.

        Sets an initial message and applies custom styling.
        """
        self.statusBar().showMessage("Ready to download Instagram Reels")
        self.statusBar().setStyleSheet(
            """
            QStatusBar {
                background-color: #1a1a1a;
                color: #ecf0f1;
                font-size: 12px;
                padding: 5px;
                border-top: 1px solid #333333;
            }
        """
        )

    def create_app_icon(self):
        """
        Creates and sets the application icon programmatically.

        Uses `AppStyles.create_app_icon_pixmap()` to generate a pixmap
        and sets it as the window icon. Handles potential errors during icon creation.
        """
        try:
            pixmap = AppStyles.create_app_icon_pixmap()
            self.setWindowIcon(QIcon(pixmap))
        except Exception:
            # Log the error if a proper logging mechanism is in place
            pass

    def add_to_queue(self):
        """
        Adds a URL from the input field to the download queue.

        Performs URL validation and checks for duplicates before adding.
        Updates the UI list and status bar accordingly.
        """
        url = self.url_input.text().strip()

        if not url:
            return

        if not is_valid_instagram_url(url):
            QMessageBox.warning(
                self, "Invalid URL", "Please enter a valid Instagram Reel URL"
            )
            return

        for item in self.reel_queue:
            if item.url == url:
                QMessageBox.information(
                    self, "Duplicate URL", "This URL is already in the queue"
                )
                return

        reel_item = ReelItem(url=url)
        self.reel_queue.append(reel_item)

        display_url = f"🔗 {url[:50]}{'...' if len(url) > 50 else ''}"
        list_item = QListWidgetItem(display_url)
        list_item.setData(Qt.ItemDataRole.UserRole, reel_item)
        self.queue_list.addItem(list_item)

        self.url_input.clear()
        self.statusBar().showMessage(
            f"Added to queue. Total items: {len(self.reel_queue)}"
        )

    def clear_queue(self):
        """
        Clears the download queue and resets the UI elements related to the queue.

        Prevents clearing if a download is currently in progress.
        """
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(
                self, "Download in Progress", "Cannot clear queue while downloading"
            )
            return

        self.reel_queue.clear()
        self.queue_list.clear()
        self.results_text.clear()
        self.overall_progress.setValue(0)
        self.progress_label.setText("Ready to start downloading...")
        self.statusBar().showMessage("Queue cleared")

    def start_download(self):
        """
        Initiates the download process for all items in the queue.

        Validates the queue, collects selected download options,
        creates and starts a `ReelDownloader` thread, and updates the UI
        to reflect the active download state.
        """
        if not self.reel_queue:
            QMessageBox.information(
                self, "Empty Queue", "Please add some URLs to the queue first"
            )
            return

        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.information(
                self, "Download in Progress", "Download is already in progress"
            )
            return

        options = {
            "video": self.video_check.isChecked(),
            "thumbnail": self.thumbnail_check.isChecked(),
            "audio": self.audio_check.isChecked(),
            "caption": self.caption_check.isChecked(),
            "transcribe": self.transcribe_check.isChecked(),
            "downloader": self.downloader_combo.currentText(),
        }

        self.download_thread = ReelDownloader(self.reel_queue.copy(), options)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_completed.connect(self.download_completed)
        self.download_thread.error_occurred.connect(self.download_error)
        self.download_thread.finished.connect(self.download_finished)

        self.download_thread.start()
        self.download_button.setEnabled(False)
        self.download_button.setText("⏳ Downloading...")
        self.statusBar().showMessage("Download started...")

    def update_progress(self, url: str, progress: int, status: str):
        """
        Updates the progress display for individual downloads and the overall progress bar.

        Args:
            url (str): The URL of the reel being downloaded.
            progress (int): The current progress percentage (0-100).
            status (str): A descriptive status message for the current operation.
        """
        if url:
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                reel_item = item.data(Qt.ItemDataRole.UserRole)
                if reel_item.url == url:
                    reel_item.progress = progress
                    reel_item.status = status

                    url_short = url[:40] + "..." if len(url) > 40 else url
                    if progress == 100:
                        item.setText(f"✅ {url_short} - {status}")
                    else:
                        item.setText(f"📥 {url_short} - {status} ({progress}%)")
                    break
        else:
            self.progress_label.setText(status)

        if self.reel_queue:
            total_progress = sum(item.progress for item in self.reel_queue)
            overall_progress = total_progress // len(self.reel_queue)
            self.overall_progress.setValue(overall_progress)

    def download_completed(self, url: str, result_data: Dict[str, Any]):
        """
        Handles the successful completion of a single reel download.

        Updates the corresponding `ReelItem` with the download results,
        adds the results to the results tab, and updates the queue list display.

        Args:
            url (str): The URL of the completed reel.
            result_data (Dict[str, Any]): A dictionary containing paths and metadata
                                          of the downloaded files.
        """
        for item in self.reel_queue:
            if item.url == url:
                item.status = "Completed"
                item.progress = 100
                item.title = result_data.get("title", "Unknown")
                item.video_path = result_data.get("video_path", "")
                item.audio_path = result_data.get("audio_path", "")
                item.thumbnail_path = result_data.get("thumbnail_path", "")
                item.caption = result_data.get("caption", "")
                item.transcript = result_data.get("transcript", "")
                item.folder_path = result_data.get("folder_path", "")
                break

        self._add_to_results(url, result_data)

        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + "..." if len(url) > 40 else url
                list_item.setText(f"✅ {url_short} - Completed")
                break

    def download_error(self, url: str, error_message: str):
        """
        Handles errors that occur during a single reel download.

        Updates the corresponding `ReelItem` with error information,
        appends the error message to the results tab, and updates the
        queue list display to indicate an error.

        Args:
            url (str): The URL of the reel that encountered an error.
            error_message (str): The error message describing the failure.
        """
        for item in self.reel_queue:
            if item.url == url:
                item.status = "Error"
                item.error_message = error_message
                break

        self.results_text.append(f"\n❌ ERROR for {url}:\n{error_message}\n" + "=" * 60)

        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            reel_item = list_item.data(Qt.ItemDataRole.UserRole)
            if reel_item.url == url:
                url_short = url[:40] + "..." if len(url) > 40 else url
                list_item.setText(f"❌ {url_short} - Error")
                break

    def download_finished(self):
        """
        Handles the completion of the entire download thread.

        Resets the download button state, updates overall progress and status messages,
        and displays a summary message box to the user.
        """
        self.download_button.setEnabled(True)
        self.download_button.setText("🚀 Start Download")
        self.overall_progress.setValue(100)
        self.progress_label.setText("All downloads completed!")
        self.statusBar().showMessage("All downloads completed")

        completed = sum(1 for item in self.reel_queue if item.status == "Completed")
        total = len(self.reel_queue)

        QMessageBox.information(
            self,
            "Download Complete",
            f"Completed {completed}/{total} downloads\n\n"
            f"Files are organized in individual reel folders",
        )

    def _add_to_results(self, url: str, result_data: Dict[str, Any]):
        """
        Adds formatted download results to the results text area.

        Also switches the active tab to the results tab to show the new entry.

        Args:
            url (str): The URL of the downloaded reel.
            result_data (Dict[str, Any]): A dictionary containing paths and metadata
                                          of the downloaded files.
        """
        result_text = f"\n✅ COMPLETED: {url}\n"
        result_text += f"Title: {result_data.get('title', 'N/A')}\n"

        if "video_path" in result_data:
            result_text += f"📹 Video: {result_data['video_path']}\n"
        if "thumbnail_path" in result_data:
            result_text += f"🖼️ Thumbnail: {result_data['thumbnail_path']}\n"
        if "audio_path" in result_data:
            result_text += f"🎵 Audio: {result_data['audio_path']}\n"
        if "caption_path" in result_data:
            result_text += f"📝 Caption: {result_data['caption_path']}\n"
        if "transcript_path" in result_data:
            result_text += f"🎤 Transcript: {result_data['transcript_path']}\n"

        result_text += "=" * 50
        self.results_text.append(result_text)

        self.tab_widget.setCurrentIndex(1)

    def open_downloads_folder(self):
        """
        Opens the application's default downloads folder in the system's file manager.

        Creates the 'downloads' directory if it doesn't exist.
        Handles opening the folder differently based on the operating system.
        If opening fails, it displays a message box with the folder path.
        """
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)

        try:
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

    def load_settings(self):
        """
        Loads application settings from the JSON file using `SettingsManager`.

        Applies the loaded settings to the UI checkboxes and downloader combobox.
        """
        settings = self.settings_manager.get_setting("ui_settings", {})
        self.video_check.setChecked(settings.get("video", True))
        self.thumbnail_check.setChecked(settings.get("thumbnail", True))
        self.audio_check.setChecked(settings.get("audio", True))
        self.caption_check.setChecked(settings.get("caption", True))
        self.transcribe_check.setChecked(settings.get("transcribe", False))
        self.downloader_combo.setCurrentText(settings.get("downloader", "Instaloader"))

    def save_settings(self):
        """
        Saves current application settings from the UI to the JSON file using `SettingsManager`.

        Collects the state of checkboxes and the selected downloader, then persists them.
        """
        settings = {
            "video": self.video_check.isChecked(),
            "thumbnail": self.thumbnail_check.isChecked(),
            "audio": self.audio_check.isChecked(),
            "caption": self.caption_check.isChecked(),
            "transcribe": self.transcribe_check.isChecked(),
            "downloader": self.downloader_combo.currentText(),
        }
        self.settings_manager.set_setting("ui_settings", settings)

    def closeEvent(self, event):
        """
        Handles the application close event.

        Stops any running download threads gracefully, saves current settings,
        and then accepts the close event.

        Args:
            event (QCloseEvent): The close event triggered by the system.
        """
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(5000)

        self.save_settings()
        event.accept()

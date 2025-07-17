"""
ReelDownloader: Instagram Reel Downloading Thread

This module defines the ReelDownloader class, a QThread-based background worker for downloading Instagram reels.
It supports lazy loading of dependencies (instaloader, moviepy, requests), and provides options to download video,
thumbnail, audio, and captions for each reel. Download progress and errors are communicated via Qt signals for UI updates.

Features:
- Dual download engines: yt-dlp and instaloader.
- Automatic fallback to the secondary downloader if the primary one fails.
- User-selectable preferred downloader.
- Downloads reels from a list of Instagram URLs (ReelItem objects)
- Supports user options for video, audio extraction, thumbnail, and caption saving
- Creates a timestamped session folder for each download batch
- Handles errors gracefully and emits progress updates
- Designed for integration with PyQt6 GUI applications

Dependencies are loaded only when needed to optimize startup time and resource usage.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

from src.core.data_models import ReelItem
from src.utils.lazy_imports import (
    lazy_import_instaloader,
    lazy_import_moviepy,
)
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent


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
        self.session_folder: Optional[Path] = None
        self.loader: Optional[Any] = None

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
            dirname_pattern=str(self.session_folder),
        )

    def _process_downloads(self):
        """Process all downloads in the queue"""
        for i, item in enumerate(self.reel_items, 1):
            if not self.is_running:
                break

            downloader_name = self.download_options.get("downloader", "Instaloader")

            primary_agent, fallback_agent = (
                (instaloader_agent, yt_dlp_agent)
                if downloader_name == "Instaloader"
                else (yt_dlp_agent, instaloader_agent)
            )

            primary_agent_name = (
                "Instaloader" if primary_agent == instaloader_agent else "yt-dlp"
            )
            fallback_agent_name = (
                "yt-dlp" if fallback_agent == yt_dlp_agent else "Instaloader"
            )

            try:
                self.progress_updated.emit(
                    item.url, 0, f"Starting download with {primary_agent_name}..."
                )
                result = self._download_with_agent(primary_agent, item, i)
                self.download_completed.emit(item.url, result)
            except Exception as e:
                self.progress_updated.emit(
                    item.url,
                    0,
                    f"{primary_agent_name} failed: {e}. Trying fallback {fallback_agent_name}...",
                )
                try:
                    result = self._download_with_agent(fallback_agent, item, i)
                    self.download_completed.emit(item.url, result)
                except Exception as e2:
                    error_msg = f"Both downloaders failed: {e} | {e2}"
                    self.error_occurred.emit(item.url, error_msg)

    def _download_with_agent(
        self, agent, item: ReelItem, reel_number: int
    ) -> Dict[str, Any]:
        """Download a reel using the specified agent."""
        if agent == instaloader_agent:
            result = agent.download_reel(
                item,
                reel_number,
                self.session_folder,
                self.loader,
                self.download_options,
                self.progress_updated.emit,
            )
        else:
            result = agent.download_reel(
                item,
                reel_number,
                self.session_folder,
                self.download_options,
                self.progress_updated.emit,
            )
        return result

    def stop(self):
        """Stop the download thread gracefully"""
        self.is_running = False

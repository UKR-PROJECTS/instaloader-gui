"""
ReelDownloader: Instagram Reel Download and Processing Thread

This module defines the ReelDownloader class, a QThread-based background worker for downloading
Instagram reels and associated media (video, thumbnail, audio, captions, and transcripts).
It supports lazy loading of heavy dependencies (instaloader, moviepy, whisper, requests) to optimize
startup time and memory usage.

Features:
- Dual download engines: yt-dlp and instaloader, with automatic fallback.
- User-selectable preferred downloader.
- Downloads Instagram reels (video and thumbnail) to organized session folders.
- Extracts and saves audio from reels.
- Saves captions and generates transcripts using OpenAI's Whisper model.
- Emits Qt signals for progress updates, completion, and error handling.
- Designed for integration with PyQt6 GUI applications.

Dependencies are loaded only when required, and all file operations are handled with error checking
and resource cleanup.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Union
from PyQt6.QtCore import QThread, pyqtSignal

from src.core.data_models import ReelItem
from src.utils.lazy_imports import lazy_import_instaloader
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent
from src.core.transcriber import AudioTranscriber
from src.core.session_manager import SessionManager


class ReelDownloader(QThread):
    """
    Background thread for downloading Instagram reels.

    This thread manages the download process, including selecting the appropriate
    downloader agent (Instaloader or yt-dlp), handling progress updates,
    and managing errors. It also integrates with the audio transcriber.

    Signals:
        progress_updated(str, int, str): Emitted when download progress changes.
                                         Args: url, progress percentage, status message.
        download_completed(str, dict): Emitted when a download finishes successfully.
                                       Args: url, dictionary of result data (file paths, etc.).
        error_occurred(str, str): Emitted when an error occurs during download.
                                  Args: url, error message.
    """

    progress_updated = pyqtSignal(str, int, str)
    download_completed = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str, str)

    def __init__(
        self, reel_items: List[ReelItem], download_options: Dict[str, Union[bool, str]]
    ):
        """
        Initializes the ReelDownloader thread.

        Args:
            reel_items: A list of ReelItem objects to be downloaded.
            download_options: A dictionary containing download preferences,
                              e.g., whether to download video, audio, caption,
                              transcribe, and preferred downloader.
        """
        super().__init__()
        self.reel_items = reel_items
        self.download_options = download_options
        self.is_running = True
        self.session_manager = SessionManager()
        self.audio_transcriber = AudioTranscriber()
        self.loader: Any = (
            None  # Instaloader instance, initialized in _setup_instaloader
        )

    def run(self):
        """
        The main entry point for the thread's execution.

        Sets up the session folder, lazily loads necessary dependencies,
        initializes Instaloader, and processes all reel downloads in the queue.
        Emits an error_occurred signal if a critical thread error occurs.
        """
        try:
            self.session_manager.setup_session_folder()
            self._lazy_load_dependencies()
            self._setup_instaloader()
            self._process_downloads()

        except Exception as e:
            self.error_occurred.emit("", f"Thread error: {str(e)}")

    def _lazy_load_dependencies(self):
        """
        Lazily loads heavy dependencies like Whisper model if transcription is enabled.

        Emits progress updates during the loading process.
        """
        self.progress_updated.emit("", 0, "Loading dependencies...")

        if self.download_options.get("transcribe", False):
            self.audio_transcriber.load_whisper_model(self.progress_updated.emit)

    def _setup_instaloader(self):
        """
        Initializes the Instaloader instance with optimal settings for downloading.

        This method is called only if Instaloader is chosen as the primary or fallback
        downloader. It configures Instaloader to download video thumbnails,
        and disables comments and metadata saving to reduce overhead.
        """
        self.progress_updated.emit("", 10, "Setting up downloader...")
        instaloader_module = lazy_import_instaloader()

        self.loader = instaloader_module.Instaloader(
            download_video_thumbnails=True,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=str(self.session_manager.get_session_folder()),
        )

    def _process_downloads(self):
        """
        Iterates through the list of reel items and processes each download.

        It attempts to download each reel using the preferred downloader,
        and falls back to the secondary downloader if the primary one fails.
        Handles transcription if enabled and emits appropriate signals for
        completion or errors.
        """
        for i, item in enumerate(self.reel_items, 1):
            if not self.is_running:
                break

            downloader_name = self.download_options.get("downloader", "Instaloader")

            primary_agent, fallback_agent = (
                (self._download_with_instaloader, self._download_with_yt_dlp)
                if downloader_name == "Instaloader"
                else (self._download_with_yt_dlp, self._download_with_instaloader)
            )

            primary_agent_name = (
                "Instaloader"
                if primary_agent == self._download_with_instaloader
                else "yt-dlp"
            )
            fallback_agent_name = (
                "yt-dlp"
                if fallback_agent == self._download_with_yt_dlp
                else "Instaloader"
            )

            primary_error = None
            try:
                self.progress_updated.emit(
                    item.url, 0, f"Starting download with {primary_agent_name}..."
                )
                result = primary_agent(item, i)
                if self.download_options.get("transcribe", False):
                    self._handle_transcription(result, i, item)
                self.download_completed.emit(item.url, result)
                continue
            except Exception as e:
                primary_error = e
                self.progress_updated.emit(
                    item.url,
                    0,
                    f"{primary_agent_name} failed: {e}. Trying fallback {fallback_agent_name}...",
                )

            try:
                result = fallback_agent(item, i)
                if self.download_options.get("transcribe", False):
                    reel_folder = Path(result["folder_path"])
                    self.audio_transcriber.transcribe_audio_from_reel(
                        reel_folder, i, result, self.progress_updated.emit
                    )
                self.download_completed.emit(item.url, result)
            except Exception as e2:
                error_msg = f"Both downloaders failed: {primary_error} | {e2}"
                self.error_occurred.emit(item.url, error_msg)

    def _download_with_instaloader(
        self, item: ReelItem, reel_number: int
    ) -> Dict[str, Any]:
        """
        Initiates a reel download using the Instaloader agent.

        Args:
            item: The ReelItem object to download.
            reel_number: The sequential number of the reel in the current session.

        Returns:
            A dictionary containing the download results from the Instaloader agent.

        Raises:
            ValueError: If the session folder is not initialized.
        """
        session_folder = self.session_manager.get_session_folder()
        if not session_folder:
            raise ValueError("Session folder is not initialized.")
        return instaloader_agent.download_reel(
            item,
            reel_number,
            session_folder,
            self.loader,
            self.download_options,
            self.progress_updated.emit,
        )

    def _handle_transcription(
        self, result: Dict[str, Any], reel_number: int, item: ReelItem
    ):
        """Handles transcription for a downloaded reel."""
        if not self.download_options.get("transcribe", False):
            return

        try:
            reel_folder = Path(result["folder_path"])
            self.audio_transcriber.transcribe_audio_from_reel(
                reel_folder, reel_number, result, self.progress_updated.emit
            )
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            result["transcript"] = error_msg
            self.progress_updated.emit(item.url, 0, error_msg)
            print(f"Transcription error: {e}")
            import traceback

            traceback.print_exc()

    def _download_with_yt_dlp(self, item: ReelItem, reel_number: int) -> Dict[str, Any]:
        """
        Initiates a reel download using the yt-dlp agent.

        Args:
            item: The ReelItem object to download.
            reel_number: The sequential number of the reel in the current session.

        Returns:
            A dictionary containing the download results from the yt-dlp agent.

        Raises:
            ValueError: If the session folder is not initialized.
        """
        session_folder = self.session_manager.get_session_folder()
        if not session_folder:
            raise ValueError("Session folder is not initialized.")
        return yt_dlp_agent.download_reel(
            item,
            reel_number,
            session_folder,
            self.download_options,
            self.progress_updated.emit,
        )

    def stop(self):
        """
        Stops the download thread gracefully.

        Sets an internal flag to False, allowing the `run` method's loop
        to terminate on its next iteration.
        """
        self.is_running = False

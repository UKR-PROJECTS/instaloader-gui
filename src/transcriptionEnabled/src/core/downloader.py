"""
ReelDownloader: Instagram Reel Download and Processing Thread

This module defines the ReelDownloader class, a QThread-based background worker for downloading
Instagram reels and associated media (video, thumbnail, audio, captions, and transcripts).
It supports lazy loading of heavy dependencies (instaloader, moviepy, whisper, requests) to optimize
startup time and memory usage. The downloader can extract audio, save captions, and transcribe audio
using OpenAI's Whisper model if enabled in the download options.

Features:
- Dual download engines: yt-dlp and instaloader.
- Automatic fallback to the secondary downloader if the primary one fails.
- User-selectable preferred downloader.
- Download Instagram reels (video and thumbnail) to organized session folders
- Extract and save audio from reels
- Save captions and generate transcripts using Whisper
- Emits Qt signals for progress updates, completion, and error handling
- Designed for integration with PyQt6 GUI applications

Dependencies are loaded only when required, and all file operations are handled with error checking
and resource cleanup.
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
    lazy_import_whisper,
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
        self.whisper_model: Optional[Any] = None
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

        # Load whisper only if transcription is enabled
        if self.download_options.get("transcribe", False):
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
            
            primary_agent_name = "Instaloader" if primary_agent == instaloader_agent else "yt-dlp"
            fallback_agent_name = "yt-dlp" if fallback_agent == yt_dlp_agent else "Instaloader"

            try:
                self.progress_updated.emit(
                    item.url, 0, f"Starting download with {primary_agent_name}..."
                )
                result = self._download_with_agent(primary_agent, item, i)
                self.download_completed.emit(item.url, result)
            except Exception as e:
                self.progress_updated.emit(
                    item.url, 0, f"{primary_agent_name} failed: {e}. Trying fallback {fallback_agent_name}..."
                )
                try:
                    result = self._download_with_agent(fallback_agent, item, i)
                    self.download_completed.emit(item.url, result)
                except Exception as e2:
                    error_msg = f"Both downloaders failed: {e} | {e2}"
                    self.error_occurred.emit(item.url, error_msg)

    def _download_with_agent(self, agent, item: ReelItem, reel_number: int) -> Dict[str, Any]:
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
        
        # Transcription is handled here after the download is complete
        if self.download_options.get("transcribe"):
            reel_folder = Path(result["folder_path"])
            self._transcribe_audio(reel_folder, reel_number, result)
            
        return result

    def _transcribe_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Transcribe audio using Whisper if enabled"""
        if not (self.download_options.get("transcribe", False) and self.whisper_model):
            return

        self.progress_updated.emit("", 90, "Transcribing audio...")

        # Use existing audio file or extract temporarily
        audio_source = result.get("audio_path")
        temp_audio_path = None

        if not audio_source:
            audio_source, temp_audio_path = self._extract_temp_audio(
                reel_folder, reel_number, result
            )

        if not (audio_source and os.path.exists(audio_source)):
            return

        try:
            transcript_result = self.whisper_model.transcribe(audio_source)
            transcript_text = transcript_result["text"]
            result["transcript"] = transcript_text

            transcript_path = reel_folder / f"transcript{reel_number}.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            result["transcript_path"] = str(transcript_path)

        except Exception as e:
            result["transcript"] = f"Transcription failed: {str(e)}"

        finally:
            # Cleanup temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                self._safe_file_removal(temp_audio_path)

    def _extract_temp_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Extract audio temporarily for transcription"""
        video_path = result.get("video_path") or str(
            reel_folder / f"video{reel_number}.mp4"
        )
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

    def stop(self):
        """Stop the download thread gracefully"""
        self.is_running = False

"""
ReelDownloader: Instagram Reel Download and Processing Thread

This module defines the ReelDownloader class, a QThread-based background worker for downloading
Instagram reels and associated media (video, thumbnail, audio, captions, and transcripts).
It supports lazy loading of heavy dependencies (instaloader, moviepy, whisper, requests) to optimize
startup time and memory usage. The downloader can extract audio, save captions, and transcribe audio
using OpenAI's Whisper model if enabled in the download options.

Features:
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
    lazy_import_requests,
)


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
            post = instaloader_module.Post.from_shortcode(
                self.loader.context, shortcode
            )

            # Create individual reel folder
            reel_folder = self.session_folder / f"reel{reel_number}"
            reel_folder.mkdir(exist_ok=True)
            result["folder_path"] = str(reel_folder)

            # Process downloads based on user options
            self._download_video(post, reel_folder, reel_number, result)
            self._download_thumbnail(post, reel_folder, reel_number, result)
            self._extract_audio(reel_folder, reel_number, result)
            self._save_caption(post, reel_folder, reel_number, result)
            self._transcribe_audio(reel_folder, reel_number, result)

            result["title"] = f"Reel {reel_number}"
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
        need_video_for_audio = self.download_options.get(
            "audio", False
        ) or self.download_options.get("transcribe", False)

        if self.download_options.get("video", True) or need_video_for_audio:
            self.progress_updated.emit("", 20, "Downloading video...")

            video_path = reel_folder / f"video{reel_number}.mp4"

            try:
                # Lazy load requests
                requests_module = lazy_import_requests()
                response = requests_module.get(post.video_url, stream=True, timeout=30)
                response.raise_for_status()

                with open(video_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                if self.download_options.get("video", True):
                    result["video_path"] = str(video_path)

            except Exception as e:
                raise Exception(f"Video download failed: {str(e)}")

    def _download_thumbnail(
        self, post, reel_folder: Path, reel_number: int, result: Dict
    ):
        """Download thumbnail image if enabled"""
        if not self.download_options.get("thumbnail", True):
            return

        self.progress_updated.emit("", 40, "Downloading thumbnail.")
        thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"

        # Determine the correct attribute for the image URL
        if hasattr(post, "thumbnail_url"):
            thumb_url = post.thumbnail_url
        elif hasattr(post, "url"):
            thumb_url = post.url
        else:
            raise AttributeError(
                f"Cannot find thumbnail URL on Post object; "
                f"available attributes: {dir(post)}"
            )

        try:
            requests_module = lazy_import_requests()
            resp = requests_module.get(thumb_url, timeout=30)
            resp.raise_for_status()

            with open(thumb_path, "wb") as f:
                f.write(resp.content)

            result["thumbnail_path"] = str(thumb_path)

        except Exception as e:
            print(f"Thumbnail download failed: {e}")

    def _extract_audio(self, reel_folder: Path, reel_number: int, result: Dict):
        """Extract audio from video if enabled"""
        if not self.download_options.get("audio", True):
            return

        self.progress_updated.emit("", 60, "Extracting audio...")

        video_path = result.get("video_path") or str(
            reel_folder / f"video{reel_number}.mp4"
        )

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
                result["audio_path"] = str(audio_path)

        except Exception as e:
            print(f"Audio extraction failed: {e}")

        finally:
            # Ensure proper cleanup of video resources
            self._cleanup_video_resources(audio_clip, video_clip)

    def _save_caption(self, post, reel_folder: Path, reel_number: int, result: Dict):
        """Save caption text if enabled"""
        if self.download_options.get("caption", True):
            self.progress_updated.emit("", 80, "Getting caption...")

            caption_text = post.caption or "No caption available"
            result["caption"] = caption_text

            caption_path = reel_folder / f"caption{reel_number}.txt"

            try:
                with open(caption_path, "w", encoding="utf-8") as f:
                    f.write(caption_text)
                result["caption_path"] = str(caption_path)

            except Exception as e:
                print(f"Caption save failed: {e}")

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

    def _extract_shortcode(self, url: str) -> Optional[str]:
        """
        Extract shortcode from Instagram URL

        Args:
            url: Instagram URL

        Returns:
            Shortcode string or None if invalid
        """
        try:
            if "/reel/" in url:
                return url.split("/reel/")[1].split("/")[0].split("?")[0]
            elif "/p/" in url:
                return url.split("/p/")[1].split("/")[0].split("?")[0]
            return None
        except Exception:
            return None

    def stop(self):
        """Stop the download thread gracefully"""
        self.is_running = False

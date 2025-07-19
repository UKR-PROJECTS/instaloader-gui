"""
yt-dlp Agent: Handles all downloading operations using the yt-dlp executable.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Union

from src.utils.lazy_imports import lazy_import_requests, lazy_import_moviepy
from src.utils.bin_checker import ensure_yt_dlp, ensure_ffmpeg, get_bin_dir, is_frozen
from src.core.data_models import ReelItem
from src.utils.resource_loader import get_resource_path


def download_reel(
    item: ReelItem,
    reel_number: int,
    session_folder: Path,
    download_options: Dict[str, Union[bool, str]],
    progress_callback: Any,
) -> Dict[str, Any]:
    """
    Download individual reel and process it using yt-dlp.

    Args:
        item: ReelItem to download.
        reel_number: Sequential number for file naming.
        session_folder: The root folder for the current download session.
        download_options: A dictionary of download preferences.
        progress_callback: A function to report progress updates.

    Returns:
        A dictionary containing paths to downloaded files.
    """
    result = {}
    assert session_folder is not None, "Session folder not created"
    reel_folder = session_folder / f"reel{reel_number}"
    reel_folder.mkdir(exist_ok=True)
    result["folder_path"] = str(reel_folder)

    # Ensure yt-dlp is available in frozen state
    if not ensure_yt_dlp():
        raise FileNotFoundError(
            "Failed to download yt-dlp.exe. Please check your internet connection."
        )

    bin_dir = get_bin_dir()
    yt_dlp_path = Path(bin_dir) / "yt-dlp.exe"
    if not yt_dlp_path.exists():
        raise FileNotFoundError(f"yt-dlp.exe not found at {yt_dlp_path}")

    progress_callback(item.url, 10, "Downloading with yt-dlp...")

    video_path = reel_folder / f"video{reel_number}.mp4"
    cmd = [
        str(yt_dlp_path),
        item.url,
        "-o",
        str(video_path),
        "--quiet",
        "--no-warnings",
    ]

    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

    subprocess.run(cmd, check=True, startupinfo=startupinfo)
    result["video_path"] = str(video_path)

    info_cmd = [str(yt_dlp_path), item.url, "--dump-json", "--quiet"]
    process = subprocess.run(
        info_cmd, capture_output=True, text=True, check=True, startupinfo=startupinfo
    )
    metadata = json.loads(process.stdout)

    if download_options.get("thumbnail"):
        thumb_url = metadata.get("thumbnail")
        if thumb_url:
            thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"
            requests_module = lazy_import_requests()
            resp = requests_module.get(thumb_url, timeout=30)
            resp.raise_for_status()
            with open(thumb_path, "wb") as f:
                f.write(resp.content)
            result["thumbnail_path"] = str(thumb_path)

    if download_options.get("caption"):
        caption = metadata.get("description", "No caption available")
        caption_path = reel_folder / f"caption{reel_number}.txt"
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption)
        result["caption_path"] = str(caption_path)
        result["caption"] = caption

    if download_options.get("audio"):
        _extract_audio(
            reel_folder, reel_number, result, download_options, progress_callback
        )

    result["title"] = metadata.get("title", f"Reel {reel_number}")
    progress_callback(item.url, 100, "Completed")
    return result


def _extract_audio(
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """
    Extracts audio from the downloaded video file if enabled.

    Args:
        reel_folder: The folder where the reel is downloaded.
        reel_number: Sequential number for file naming.
        result: Dictionary to store download results.
        download_options: A dictionary of download preferences.
        progress_callback: A function to report progress updates.
    """
    if not download_options.get("audio", True):
        return

    # Ensure ffmpeg is available in frozen state
    if is_frozen() and not ensure_ffmpeg():
        progress_callback("", 60, "FFmpeg not available, skipping audio extraction...")
        return

    progress_callback("", 60, "Extracting audio...")
    video_path = result.get("video_path") or str(
        reel_folder / f"video{reel_number}.mp4"
    )
    if not os.path.exists(video_path):
        return
    audio_path = reel_folder / f"audio{reel_number}.mp3"
    video_clip = None
    audio_clip = None
    try:
        VideoFileClip = lazy_import_moviepy()
        video_clip = VideoFileClip(video_path)
        if video_clip.audio is not None:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(str(audio_path), verbose=False, logger=None)
            result["audio_path"] = str(audio_path)
    except Exception:
        # Log the error if a proper logging mechanism is in place
        pass
    finally:
        _cleanup_video_resources(audio_clip, video_clip)


def _cleanup_video_resources(audio_clip, video_clip):
    """
    Safely closes and cleans up moviepy video and audio clip resources.

    Args:
        audio_clip: The audio clip object to close.
        video_clip: The video clip object to close.
    """
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

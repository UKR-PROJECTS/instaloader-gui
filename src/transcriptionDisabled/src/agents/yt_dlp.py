"""
yt-dlp Agent: Handles all downloading operations using the yt-dlp executable.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

from src.utils.lazy_imports import lazy_import_requests, lazy_import_moviepy
from src.core.data_models import ReelItem


def download_reel(
    item: ReelItem,
    reel_number: int,
    session_folder: Path,
    download_options: Dict[str, bool],
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

    yt_dlp_path = Path("bin/yt-dlp.exe")
    if not yt_dlp_path.exists():
        raise FileNotFoundError("yt-dlp.exe not found in bin folder")

    progress_callback(item.url, 10, "Downloading with yt-dlp...")

    # Command to download video
    video_path = reel_folder / f"video{reel_number}.mp4"
    cmd = [
        str(yt_dlp_path),
        item.url,
        "-o",
        str(video_path),
        "--quiet",
        "--no-warnings",
    ]
    subprocess.run(cmd, check=True)
    result["video_path"] = str(video_path)

    # Get metadata
    info_cmd = [str(yt_dlp_path), item.url, "--dump-json", "--quiet"]
    process = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
    metadata = json.loads(process.stdout)

    # Save thumbnail
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

    # Save caption
    if download_options.get("caption"):
        caption = metadata.get("description", "No caption available")
        caption_path = reel_folder / f"caption{reel_number}.txt"
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption)
        result["caption_path"] = str(caption_path)
        result["caption"] = caption

    # Extract audio
    if download_options.get("audio"):
        _extract_audio(reel_folder, reel_number, result, download_options, progress_callback)

    result["title"] = metadata.get("title", f"Reel {reel_number}")
    progress_callback(item.url, 100, "Completed")
    return result


def _extract_audio(reel_folder: Path, reel_number: int, result: Dict, download_options: Dict, progress_callback: Any):
    """Extract audio from video if enabled."""
    if not download_options.get("audio", True):
        return
    progress_callback("", 60, "Extracting audio...")
    video_path = result.get("video_path") or str(reel_folder / f"video{reel_number}.mp4")
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
    except Exception as e:
        print(f"Audio extraction failed: {e}")
    finally:
        _cleanup_video_resources(audio_clip, video_clip)


def _cleanup_video_resources(audio_clip, video_clip):
    """Safely cleanup video and audio resources."""
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

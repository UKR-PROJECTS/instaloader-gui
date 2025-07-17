"""
Instaloader Agent: Handles all downloading operations using the Instaloader library.
"""

import os
from pathlib import Path
from typing import Dict, Any, Union

from src.utils.lazy_imports import (
    lazy_import_instaloader,
    lazy_import_requests,
    lazy_import_moviepy,
)
from src.core.data_models import ReelItem


def download_reel(
    item: ReelItem,
    reel_number: int,
    session_folder: Path,
    loader: Any,
    download_options: Dict[str, Union[bool, str]],
    progress_callback: Any,
) -> Dict[str, Any]:
    """
    Download individual reel and process it using Instaloader.

    Args:
        item: ReelItem to download.
        reel_number: Sequential number for file naming.
        session_folder: The root folder for the current download session.
        loader: An initialized Instaloader instance.
        download_options: A dictionary of download preferences.
        progress_callback: A function to report progress updates.

    Returns:
        A dictionary containing paths to downloaded files.
    """
    result = {}
    temp_video_path = None

    try:
        assert loader is not None, "Instaloader not initialized"
        assert session_folder is not None, "Session folder not created"

        shortcode = _extract_shortcode(item.url)
        if not shortcode:
            raise ValueError("Invalid Instagram URL")

        progress_callback(item.url, 10, "Fetching reel data...")

        instaloader_module = lazy_import_instaloader()
        post = instaloader_module.Post.from_shortcode(loader.context, shortcode)

        reel_folder = session_folder / f"reel{reel_number}"
        reel_folder.mkdir(exist_ok=True)
        result["folder_path"] = str(reel_folder)

        _download_video(
            post, reel_folder, reel_number, result, download_options, progress_callback
        )
        _download_thumbnail(
            post, reel_folder, reel_number, result, download_options, progress_callback
        )
        _extract_audio(
            reel_folder, reel_number, result, download_options, progress_callback
        )
        _save_caption(
            post, reel_folder, reel_number, result, download_options, progress_callback
        )

        result["title"] = f"Reel {reel_number}"
        progress_callback(item.url, 100, "Completed")

    except Exception as e:
        raise Exception(f"Instaloader download error: {str(e)}")

    finally:
        if temp_video_path and os.path.exists(str(temp_video_path)):
            _safe_file_removal(str(temp_video_path))

    return result


def _download_video(
    post,
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """Download video file if enabled."""
    need_video_for_audio = download_options.get("audio", False) or download_options.get(
        "transcribe", False
    )

    if download_options.get("video", True) or need_video_for_audio:
        progress_callback("", 20, "Downloading video...")
        video_path = reel_folder / f"video{reel_number}.mp4"
        try:
            requests_module = lazy_import_requests()
            response = requests_module.get(post.video_url, stream=True, timeout=30)
            response.raise_for_status()
            with open(video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            if download_options.get("video", True):
                result["video_path"] = str(video_path)
        except Exception as e:
            raise Exception(f"Video download failed: {str(e)}")


def _download_thumbnail(
    post,
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """Download thumbnail image if enabled."""
    if not download_options.get("thumbnail", True):
        return
    progress_callback("", 40, "Downloading thumbnail.")
    thumb_path = reel_folder / f"thumbnail{reel_number}.jpg"
    if hasattr(post, "thumbnail_url"):
        thumb_url = post.thumbnail_url
    elif hasattr(post, "url"):
        thumb_url = post.url
    else:
        raise AttributeError(
            f"Cannot find thumbnail URL on Post object; available attributes: {dir(post)}"
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


def _extract_audio(
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """Extract audio from video if enabled."""
    if not download_options.get("audio", True):
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
    except Exception as e:
        print(f"Audio extraction failed: {e}")
    finally:
        _cleanup_video_resources(audio_clip, video_clip)


def _save_caption(
    post,
    reel_folder: Path,
    reel_number: int,
    result: Dict,
    download_options: Dict,
    progress_callback: Any,
):
    """Save caption text if enabled."""
    if download_options.get("caption", True):
        progress_callback("", 80, "Getting caption...")
        caption_text = post.caption or "No caption available"
        result["caption"] = caption_text
        caption_path = reel_folder / f"caption{reel_number}.txt"
        try:
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(caption_text)
            result["caption_path"] = str(caption_path)
        except Exception as e:
            print(f"Caption save failed: {e}")


def _extract_shortcode(url: str):
    """Extract shortcode from Instagram URL."""
    try:
        if "/reel/" in url:
            return url.split("/reel/")[1].split("/")[0].split("?")[0]
        elif "/p/" in url:
            return url.split("/p/")[1].split("/")[0].split("?")[0]
        return None
    except Exception:
        return None


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


def _safe_file_removal(file_path: str):
    """Safely remove a file with error handling."""
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Could not remove file {file_path}: {e}")

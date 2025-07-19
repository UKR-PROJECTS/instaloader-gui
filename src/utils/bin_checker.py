import os
import sys
import urllib.request
import zipfile
import shutil
import logging
import json
import hashlib
import time

logger = logging.getLogger(__name__)


def is_frozen():
    """Check if the application is running as a frozen executable (EXE)"""
    return getattr(sys, "frozen", False)


def get_bin_dir():
    """Get the path to the bin directory based on execution context"""
    if is_frozen():
        # In frozen state, bin directory is next to the executable
        return os.path.join(os.path.dirname(sys.executable), "bin")
    else:
        # In development, use the src/bin directory
        return os.path.join(os.path.dirname(__file__), "..", "bin")


def download_yt_dlp(progress_callback=None):
    """Download yt-dlp.exe to the bin directory with progress reporting"""
    return download_file(
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        os.path.join(get_bin_dir(), "yt-dlp.exe"),
        "yt-dlp.exe",
        progress_callback,
    )


def download_ffmpeg(progress_callback=None):
    """Download and extract ffmpeg to the bin directory with progress reporting"""
    bin_dir = get_bin_dir()
    os.makedirs(bin_dir, exist_ok=True)
    temp_dir = os.path.join(bin_dir, "temp_ffmpeg")
    os.makedirs(temp_dir, exist_ok=True)

    # Download the latest FFmpeg build
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")

    try:
        if progress_callback:
            progress_callback("", 0, "Downloading FFmpeg...")
        logger.info("Downloading FFmpeg...")

        # Download with progress
        if not download_file(url, zip_path, "FFmpeg.zip", progress_callback):
            return False

        if progress_callback:
            progress_callback("", 50, "Extracting FFmpeg...")
        logger.info("Extracting FFmpeg...")

        # Extract FFmpeg executable
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Find ffmpeg.exe in the zip file
            for file in zip_ref.namelist():
                if file.endswith("ffmpeg.exe") and "bin" in file:
                    zip_ref.extract(file, temp_dir)
                    extracted_path = os.path.join(temp_dir, file)

                    # Move to bin directory
                    shutil.move(extracted_path, os.path.join(bin_dir, "ffmpeg.exe"))
                    break

        if progress_callback:
            progress_callback("", 100, "FFmpeg downloaded successfully")
        logger.info("FFmpeg downloaded and extracted successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download FFmpeg: {str(e)}")
        return False
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def download_whisper_model(progress_callback=None):
    """Download Whisper model (base.pt) and assets if missing in frozen state"""
    if not is_frozen():
        return True

    base_dir = os.path.dirname(get_bin_dir())
    whisper_dir = os.path.join(base_dir, "whisper")
    assets_dir = os.path.join(whisper_dir, "assets")

    # Create directories if needed
    os.makedirs(whisper_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # Define model and assets to download
    model_files = {
        "base.pt": "https://github.com/openai/whisper/raw/main/whisper/assets/base.pt",
        "assets/gpt2.tiktoken": "https://github.com/openai/whisper/raw/main/whisper/assets/gpt2.tiktoken",
        "assets/mel_filters.npz": "https://github.com/openai/whisper/raw/main/whisper/assets/mel_filters.npz",
        "assets/multilingual.tiktoken": "https://github.com/openai/whisper/raw/main/whisper/assets/multilingual.tiktoken",
    }

    try:
        if progress_callback:
            progress_callback("", 0, "Verifying Whisper model files...")
        logger.info("Verifying Whisper model files...")

        total_files = len(model_files)
        downloaded = 0

        for file, url in model_files.items():
            file_path = os.path.join(whisper_dir, file)

            # Skip if file exists
            if os.path.exists(file_path):
                downloaded += 1
                continue

            if progress_callback:
                progress_callback(
                    "",
                    int(downloaded / total_files * 100),
                    f"Starting download: {file}",
                )

            # Download with progress and retries
            if not download_file(
                url,
                file_path,
                file,
                progress_callback,
                lambda current, total, speed: (
                    progress_callback(
                        "",
                        int((downloaded + current / (total or 1)) / total_files * 100),
                        f"Downloading {file}: {format_size(current)}/{format_size(total)} ({speed} MB/s)",
                    )
                    if progress_callback
                    else None
                ),
            ):
                logger.error(f"Failed to download: {file}")
                return False

            downloaded += 1

        if progress_callback:
            progress_callback("", 100, "Whisper model download complete")

        logger.info("Whisper model download complete")
        return True
    except Exception as e:
        logger.error(f"Failed to download Whisper model: {str(e)}")
        return False


def download_file(
    url, dest, name, progress_callback=None, progress_lambda=None, max_retries=3
):
    """Download a file with progress reporting and retry logic"""
    # Prefer Qt-based downloader for better reliability
    if has_qt_available():
        return download_file_with_qt(url, dest, progress_lambda, max_retries)
    else:
        return download_file_with_urllib(
            url, dest, name, progress_callback, max_retries
        )


def has_qt_available():
    """Check if PyQt6 is available"""
    try:
        from PyQt6.QtCore import QCoreApplication

        app = QCoreApplication.instance() or QCoreApplication()
        return True
    except ImportError:
        return False
    except:
        return False


def download_file_with_qt(url, dest, progress_callback=None, max_retries=3):
    """Download a file using Qt network with progress reporting and retry logic"""
    try:
        from PyQt6.QtNetwork import (
            QNetworkAccessManager,
            QNetworkRequest,
            QNetworkReply,
        )
        from PyQt6.QtCore import QUrl, QFile, QIODevice, QTimer, QEventLoop
    except ImportError:
        return False

    manager = QNetworkAccessManager()
    file = QFile(dest)

    if not file.open(QIODevice.WriteOnly):
        logger.error(f"Failed to open file for writing: {dest}")
        return False

    retry_count = 0
    start_time = time.time()
    last_received = 0
    total_size = None

    while retry_count < max_retries:
        request = QNetworkRequest(QUrl(url))
        reply = manager.get(request)

        # Create a timer to track download speed
        timer = QTimer()
        timer.start(1000)  # Update every second

        def update_speed():
            nonlocal last_received
            if total_size is None:
                return

            current = file.size()
            elapsed = time.time() - start_time
            speed = (current - last_received) / (1024 * 1024)  # MB/s
            last_received = current

            if progress_callback:
                progress_callback(current, total_size, f"{speed:.2f}")

        timer.timeout.connect(update_speed)

        # Track download progress
        def on_download_progress(received, total):
            nonlocal total_size
            total_size = total
            file.write(reply.readAll())

            if progress_callback:
                progress_callback(received, total, "0.00")

        reply.downloadProgress.connect(on_download_progress)

        # Wait for download to finish
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec()

        if reply.error() == QNetworkReply.NoError:
            file.close()
            return True

        # Handle HTTP errors
        error = reply.errorString()
        logger.warning(f"Download failed (attempt {retry_count+1}): {error}")

        # Exponential backoff before retrying
        delay = 2**retry_count
        time.sleep(delay)
        retry_count += 1

    file.close()
    file.remove()
    return False


def download_file_with_urllib(url, dest, name, progress_callback=None, max_retries=3):
    """Download a file with urllib with progress reporting and retry logic"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            last_progress_time = time.time()
            last_bytes_received = 0

            def report_hook(count, block_size, total_size):
                nonlocal last_progress_time, last_bytes_received
                current_time = time.time()
                bytes_received = count * block_size

                # Calculate download speed
                time_diff = current_time - last_progress_time
                if time_diff > 0.5:  # Update every 0.5 seconds
                    speed = (bytes_received - last_bytes_received) / (
                        time_diff * 1024 * 1024
                    )  # MB/s
                    last_bytes_received = bytes_received
                    last_progress_time = current_time

                    if progress_callback:
                        if total_size > 0:
                            percent = min(100.0, bytes_received * 100.0 / total_size)
                            progress_callback(
                                "",
                                int(percent),
                                f"Downloading {name}: {format_size(bytes_received)}/{format_size(total_size)} ({speed:.2f} MB/s)",
                            )
                        else:
                            progress_callback(
                                "",
                                0,
                                f"Downloading {name}: {format_size(bytes_received)} (unknown size)",
                            )

            urllib.request.urlretrieve(url, dest, reporthook=report_hook)
            return True
        except Exception as e:
            logger.warning(f"Download failed (attempt {retry_count+1}): {str(e)}")
            if retry_count < max_retries - 1:
                delay = 2**retry_count
                time.sleep(delay)
                retry_count += 1
            else:
                return False
    return False


def format_size(bytes):
    """Convert bytes to human-readable format"""
    if bytes is None:
        return "Unknown"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} GB"


def ensure_whisper_model(progress_callback=None):
    """Ensure Whisper model exists, download if needed in frozen state"""
    if not is_frozen():
        return True

    base_dir = os.path.dirname(get_bin_dir())
    whisper_dir = os.path.join(base_dir, "whisper")
    model_path = os.path.join(whisper_dir, "base.pt")

    if not os.path.exists(model_path):
        return download_whisper_model(progress_callback)
    return True


def ensure_yt_dlp(progress_callback=None):
    """Ensure yt-dlp.exe exists in bin directory, download if needed and in frozen state"""
    bin_dir = get_bin_dir()
    yt_dlp_path = os.path.join(bin_dir, "yt-dlp.exe")

    if not os.path.exists(yt_dlp_path) and is_frozen():
        return download_yt_dlp(progress_callback)
    return True


def ensure_ffmpeg(progress_callback=None):
    """Ensure ffmpeg.exe exists in bin directory, download if needed and in frozen state"""
    bin_dir = get_bin_dir()
    ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")

    if not os.path.exists(ffmpeg_path) and is_frozen():
        return download_ffmpeg(progress_callback)
    return True

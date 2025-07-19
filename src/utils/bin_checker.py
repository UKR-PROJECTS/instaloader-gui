import os
import sys
import urllib.request
import zipfile
import shutil
import logging
import json
import hashlib

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
    """Download yt-dlp.exe to the bin directory"""
    bin_dir = get_bin_dir()
    os.makedirs(bin_dir, exist_ok=True)
    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    dest_path = os.path.join(bin_dir, "yt-dlp.exe")

    try:
        if progress_callback:
            progress_callback("", 0, "Downloading yt-dlp.exe...")

        logger.info("Downloading yt-dlp.exe...")
        urllib.request.urlretrieve(url, dest_path)

        if progress_callback:
            progress_callback("", 100, "yt-dlp.exe downloaded successfully")
        logger.info("yt-dlp.exe downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download yt-dlp.exe: {str(e)}")
        return False


def download_ffmpeg(progress_callback=None):
    """Download and extract ffmpeg to the bin directory"""
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
        urllib.request.urlretrieve(url, zip_path)

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

            # Use PySide6's network access for reliable downloads
            success = download_file_with_progress(
                url,
                file_path,
                lambda current, total, speed: (
                    progress_callback(
                        "",
                        int((downloaded + current / (total or 1)) / total_files * 100),
                        f"Downloading {file}: {format_size(current)}/{format_size(total)} ({speed} MB/s)",
                    )
                    if progress_callback
                    else None
                ),
            )

            if not success:
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


def format_size(bytes):
    """Convert bytes to human-readable format"""
    if bytes is None:
        return "Unknown"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} GB"


def download_file_with_progress(url, dest, progress_callback=None, max_retries=3):
    """Download a file with progress reporting and retry logic"""
    from PySide6.QtNetwork import QNetworkRequest, QNetworkAccessManager
    from PySide6.QtCore import QUrl, QFile, QIODevice, QTimer
    import time

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

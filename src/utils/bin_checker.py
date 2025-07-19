import os
import sys
import urllib.request
import zipfile
import shutil
import logging

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
            progress_callback(0, "Downloading yt-dlp.exe...")

        logger.info("Downloading yt-dlp.exe...")
        urllib.request.urlretrieve(url, dest_path)

        if progress_callback:
            progress_callback(100, "yt-dlp.exe downloaded successfully")
        logger.info("yt-dlp.exe downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download yt-dlp.exe: {str(e)}")
        if progress_callback:
            progress_callback(0, f"Failed to download yt-dlp.exe: {e}")
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
            progress_callback(0, "Downloading FFmpeg...")
        logger.info("Downloading FFmpeg...")
        urllib.request.urlretrieve(url, zip_path)

        if progress_callback:
            progress_callback(50, "Extracting FFmpeg...")
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
            progress_callback(100, "FFmpeg downloaded successfully")
        logger.info("FFmpeg downloaded and extracted successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to download FFmpeg: {str(e)}")
        if progress_callback:
            progress_callback(0, f"Failed to download FFmpeg: {e}")
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
        "base.pt": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
    }

    try:
        if progress_callback:
            progress_callback(0, "Verifying Whisper model files...")
        logger.info("Verifying Whisper model files...")

        for i, (file, url) in enumerate(model_files.items()):
            file_path = os.path.join(whisper_dir, file)

            if os.path.exists(file_path):
                continue

            if progress_callback:
                progress_callback(
                    int(i / len(model_files) * 100), f"Downloading {file}..."
                )

            urllib.request.urlretrieve(url, file_path)

        if progress_callback:
            progress_callback(100, "Whisper model download complete")
        logger.info("Whisper model download complete")
        return True
    except Exception as e:
        logger.error(f"Failed to download Whisper model: {str(e)}")
        if progress_callback:
            progress_callback(0, f"Failed to download Whisper model: {e}")
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

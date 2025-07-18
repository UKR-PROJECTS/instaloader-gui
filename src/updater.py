import subprocess
import requests
import os
from PyQt6.QtWidgets import QProgressDialog, QApplication, QMessageBox
from PyQt6.QtCore import Qt


def get_current_version() -> str | None:
    """
    Retrieves the current version of the yt-dlp executable.

    Executes `yt-dlp.exe --version` and parses the output.

    Returns:
        str | None: The current version string if successful, otherwise None.
    """
    try:
        result = subprocess.run(
            ["bin/yt-dlp.exe", "--version"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Log the error if a proper logging mechanism is in place
        return None


def get_latest_version() -> str | None:
    """
    Fetches the latest available version of yt-dlp from its GitHub releases.

    Returns:
        str | None: The latest version tag name if successful, otherwise None.
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest", timeout=10
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["tag_name"]
    except requests.exceptions.RequestException:
        # Log the error if a proper logging mechanism is in place
        return None
    except KeyError:
        # Log the error if 'tag_name' is not found in the JSON response
        return None


def download_latest_version():
    """
    Downloads the latest yt-dlp.exe to the 'bin' directory.

    Displays a QProgressDialog to show download progress.
    Handles potential network errors during download.
    """
    progress = QProgressDialog("Downloading update...", "Cancel", 0, 100)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setAutoClose(False)  # Keep dialog open until explicitly closed
    progress.setCancelButton(None)  # No cancel button for critical updates
    progress.show()

    try:
        response = requests.get(
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
            stream=True,
            timeout=300,  # 5 minutes timeout for large files
        )
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0

        # Ensure the bin directory exists
        os.makedirs("bin", exist_ok=True)
        yt_dlp_path = os.path.join("bin", "yt-dlp.exe")

        with open(yt_dlp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):  # Increased chunk size
                if (
                    progress.wasCanceled()
                ):  # Check if user cancelled (if button re-enabled)
                    break
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if total_size > 0:
                        progress.setValue(int(100 * bytes_downloaded / total_size))
                    QApplication.processEvents()  # Keep UI responsive

        progress.setValue(100)
        QMessageBox.information(
            None,
            "Update Complete",
            "yt-dlp has been updated to the latest version.",
        )
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(
            None, "Download Error", f"Failed to download yt-dlp update: {e}"
        )
    except Exception as e:
        QMessageBox.critical(
            None, "Error", f"An unexpected error occurred during update: {e}"
        )
    finally:
        progress.close()


def check_for_updates():
    """
    Checks for available yt-dlp updates and prompts the user to download if a new version is found.
    """
    current_version = get_current_version()
    latest_version = get_latest_version()

    if current_version and latest_version and current_version < latest_version:
        reply = QMessageBox.question(
            None,
            "Update Available",
            f"A new version of yt-dlp is available ({latest_version}). Do you want to update?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            download_latest_version()
    elif current_version and latest_version and current_version == latest_version:
        # Optionally, inform the user that they are already on the latest version
        # QMessageBox.information(None, "No Update", "You are already using the latest version of yt-dlp.")
        pass
    else:
        # Handle cases where versions couldn't be retrieved (e.g., network error, yt-dlp.exe missing)
        # This message might be too intrusive on every startup if there's a persistent issue.
        # Consider logging this instead or showing a less prominent message.
        # QMessageBox.warning(None, "Update Check Failed", "Could not check for yt-dlp updates.")
        pass

import subprocess
import requests
import os
from tkinter import messagebox
from PyQt6.QtWidgets import QProgressDialog, QApplication
from PyQt6.QtCore import Qt


def get_current_version():
    try:
        result = subprocess.run(
            ["bin/yt-dlp.exe", "--version"], capture_output=True, text=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return None


def get_latest_version():
    response = requests.get(
        "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
    )
    return response.json()["tag_name"]


def download_latest_version():
    progress = QProgressDialog("Downloading update...", "Cancel", 0, 100)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.show()

    response = requests.get(
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        stream=True,
    )
    total_size = int(response.headers.get("content-length", 0))
    bytes_downloaded = 0

    with open("bin/yt-dlp.exe", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                bytes_downloaded += len(chunk)
                progress.setValue(int(100 * bytes_downloaded / total_size))
                QApplication.processEvents()

    progress.setValue(100)


def check_for_updates():
    current_version = get_current_version()
    latest_version = get_latest_version()

    if current_version and current_version < latest_version:
        if messagebox.askyesno(
            "Update Available",
            f"A new version of yt-dlp is available ({latest_version}). Do you want to update?",
        ):
            download_latest_version()
            messagebox.showinfo(
                "Update Complete", "yt-dlp has been updated to the latest version."
            )

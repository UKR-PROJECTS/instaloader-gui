from PyQt6.QtCore import QThread, pyqtSignal
from src.utils.bin_checker import ensure_yt_dlp, ensure_ffmpeg, ensure_whisper_model


class DependencyDownloader(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(bool)

    def __init__(self, options):
        super().__init__()
        self.options = options

    def run(self):
        try:
            if self.options.get("downloader") == "yt-dlp":
                self.progress_updated.emit(0, "Checking for yt-dlp...")
                if not ensure_yt_dlp(self.update_progress):
                    self.finished.emit(False)
                    return
                self.progress_updated.emit(33, "Checking for ffmpeg...")
                if not ensure_ffmpeg(self.update_progress):
                    self.finished.emit(False)
                    return
            if self.options.get("transcribe"):
                self.progress_updated.emit(66, "Checking for Whisper model...")
                if not ensure_whisper_model(self.update_progress):
                    self.finished.emit(False)
                    return
            self.progress_updated.emit(100, "All dependencies are up to date.")
            self.finished.emit(True)
        except Exception as e:
            self.progress_updated.emit(0, f"An error occurred: {e}")
            self.finished.emit(False)

    def update_progress(self, value, text):
        self.progress_updated.emit(value, text)

from PyQt6.QtWidgets import QProgressDialog
from PyQt6.QtCore import Qt


class DownloadProgressDialog(QProgressDialog):
    def __init__(self, parent=None):
        super().__init__("Downloading...", "Cancel", 0, 100, parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setAutoClose(True)
        self.setMinimumDuration(0)

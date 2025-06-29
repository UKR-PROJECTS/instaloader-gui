from PyQt6.QtWidgets import QPushButton, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ModernButton(QPushButton):
    """Custom styled button with modern gradient design"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_button()

    def _setup_button(self):
        """Initialize button styling and properties"""
        self.setStyleSheet(self._get_button_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setFont(QFont("Arial", 9))

    def _get_button_style(self):
        """Return modern button stylesheet"""
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
            color: white;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
        }
        QPushButton:hover { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd8, stop:1 #6a4190);
        }
        QPushButton:pressed { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4e63c6, stop:1 #58377e);
        }
        QPushButton:disabled { 
            background: #bdc3c7; 
            color: #7f8c8d; 
        }
        """


class ModernProgressBar(QProgressBar):
    """Custom styled progress bar with modern design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_progress_bar()

    def _setup_progress_bar(self):
        """Initialize progress bar styling"""
        self.setMinimumHeight(20)
        self.setStyleSheet(self._get_progress_style())

    def _get_progress_style(self):
        """Return modern progress bar stylesheet"""
        return """
        QProgressBar {
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            text-align: center;
            background-color: #f8f9fa;
            font-size: 10px;
            color: #2c3e50;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            margin: 1px;
        }
        """
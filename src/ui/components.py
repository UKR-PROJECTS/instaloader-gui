"""
This module defines custom PyQt widgets with modern styling.

It includes:
- `ModernButton`: A custom QPushButton with a gradient background, rounded corners,
  and interactive hover/pressed/disabled states.
- `ModernProgressBar`: A custom QProgressBar with a modern design.
"""

from PyQt6.QtWidgets import QPushButton, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.styles import AppStyles


class ModernButton(QPushButton):
    """
    A custom styled QPushButton with a modern gradient design.

    This button provides a visually appealing and interactive element
    with custom styling defined in `AppStyles`.
    """

    def __init__(self, text: str = "", parent=None):
        """
        Initializes the ModernButton.

        Args:
            text (str): The text to display on the button. Defaults to an empty string.
            parent (QWidget, optional): The parent widget of the button. Defaults to None.
        """
        super().__init__(text, parent)
        self._setup_button()

    def _setup_button(self):
        """
        Applies initial styling and properties to the button.

        This includes setting the stylesheet, cursor shape, minimum height, and font.
        """
        self.setStyleSheet(AppStyles.get_button_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setFont(QFont("Arial", 9))


class ModernProgressBar(QProgressBar):
    """
    A custom styled QProgressBar with a modern design.

    This progress bar provides a visually consistent progress indicator
    with custom styling defined in `AppStyles`.
    """

    def __init__(self, parent=None):
        """
        Initializes the ModernProgressBar.

        Args:
            parent (QWidget, optional): The parent widget of the progress bar. Defaults to None.
        """
        super().__init__(parent)
        self._setup_progress_bar()

    def _setup_progress_bar(self):
        """
        Applies initial styling and properties to the progress bar.

        This includes setting the minimum height and the stylesheet.
        """
        self.setMinimumHeight(20)
        self.setStyleSheet(AppStyles.get_progress_style())

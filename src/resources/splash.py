"""
This module defines a custom SplashScreen class for a PyQt application.

The SplashScreen displays a visually appealing splash window with a gradient background,
application name, description, loading messages, and version information during application startup.
It is designed to enhance user experience by providing feedback while the main application loads.
"""

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QColor, QPainter, QBrush, QLinearGradient


class SplashScreen(QSplashScreen):
    """
    Custom splash screen for the application.

    This class creates a visually enhanced splash screen using a gradient background,
    displays the application name, description, loading status, and version information.
    It also provides a method to update the loading message dynamically during startup.
    """

    def __init__(self):
        """
        Initializes the SplashScreen.

        Calls `setup_splash` to configure the splash screen's appearance.
        """
        super().__init__()
        self.setup_splash()

    def setup_splash(self):
        """
        Configures the appearance of the splash screen.

        This method creates a QPixmap, draws a gradient background,
        and adds text elements for the application name, description,
        loading messages, and version information. It also sets the
        window flags for a frameless splash screen.
        """
        # Create splash screen pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#2c3e50"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw gradient background
        gradient = QLinearGradient(0, 0, 400, 300)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, 400, 300)

        # Draw app name
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        painter.drawText(50, 100, "Instagram Downloader")

        painter.setFont(QFont("Arial", 14))
        painter.drawText(50, 130, "Professional Media Downloader")

        # Draw loading text
        painter.setFont(QFont("Arial", 12))
        painter.drawText(50, 200, "Loading components...")
        painter.drawText(50, 220, "Please wait...")

        # Draw version
        painter.setFont(QFont("Arial", 10))
        painter.drawText(50, 270, "Version 3.0.0 - PyInstaller Optimized")

        painter.end()

        self.setPixmap(pixmap)
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
        )

    def show_message(self, message: str):
        """
        Updates the splash screen with a new loading message.

        This method displays the given message at the bottom center of the
        splash screen and forces the UI to update immediately.

        Args:
            message (str): The loading message to display.
        """
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("white"),
        )
        QApplication.processEvents()

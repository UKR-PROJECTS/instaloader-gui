"""
This module defines a custom SplashScreen class for a PyQt application.
The SplashScreen displays a visually appealing splash window with a gradient background,
application name, description, loading messages, and version information during application startup.
It is designed to enhance user experience by providing feedback while the main application loads.

Class SplashScreen: A subclass of QSplashScreen that customizes the splash screen's appearance

Custom splash screen for the application.
This class creates a visually enhanced splash screen using a gradient background,
displays the application name, description, loading status, and version information.
It also provides a method to update the loading message dynamically during startup.

Methods
-------
setup_splash():
    Configures the appearance of the splash screen, including background, text, and version.
show_message(message: str):
    Updates the splash screen with a new loading message and processes UI events.
"""

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QColor, QPainter, QBrush, QLinearGradient


class SplashScreen(QSplashScreen):
    """Custom splash screen with loading progress"""

    def __init__(self):
        super().__init__()
        self.setup_splash()

    def setup_splash(self):
        """Setup splash screen appearance"""
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
        painter.drawText(50, 100, "Instagram Media Downloader")

        painter.setFont(QFont("Arial", 14))
        painter.drawText(50, 130, "Instagram Downloader")

        # Draw loading text
        painter.setFont(QFont("Arial", 12))
        painter.drawText(50, 200, "Loading components...")
        painter.drawText(50, 220, "Please wait...")

        # Draw version
        painter.setFont(QFont("Arial", 10))
        painter.drawText(50, 270, "Version 3.0.0 ")

        painter.end()

        self.setPixmap(pixmap)
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
        )

    def show_message(self, message: str):
        """Show loading message on splash screen"""
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("white"),
        )
        QApplication.processEvents()

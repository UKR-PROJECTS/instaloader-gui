from PyQt6.QtGui import QColor, QBrush, QPainter, QPixmap


class AppStyles:
    """
    Centralized class for managing all application UI styles.

    This class provides static methods to retrieve stylesheets for various
    GUI components, promoting consistency and maintainability across the application's
    user interface. It also includes a method to programmatically create an application icon.
    """

    @staticmethod
    def get_main_style() -> str:
        """
        Returns the stylesheet for the main application window.

        This style applies a gradient background to the QMainWindow.
        """
        return """
        QMainWindow {
            background: #1a1a1a; /* Black background */
            color: #ecf0f1; /* Light text */
        }
        """

    @staticmethod
    def get_panel_style() -> str:
        """
        Returns the stylesheet for the left control panel.

        This style applies a modern design with a dark background,
        rounded borders, and a subtle shadow.
        """
        return """
        QFrame {
            background-color: #1a1a1a; /* Black panel background */
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            padding: 5px;
        }
        """

    @staticmethod
    def get_button_style() -> str:
        """
        Returns the stylesheet for a general-purpose button.

        This style provides a neutral gradient background with hover, pressed,
        and disabled states for visual feedback.
        """
        return """
        QPushButton {
            background-color: #333333; /* Black button background */
            border-radius: 5px;
            color: #ecf0f1; /* Light text */
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #444444; /* Slightly lighter on hover */
        }
        QPushButton:pressed {
            background-color: #222222; /* Darker on pressed */
        }
        QPushButton:disabled {
            background-color: #1a1a1a; /* Disabled background */
            color: #7f8c8d; /* Disabled text */
        }
        """

    @staticmethod
    def get_danger_button_style() -> str:
        """
        Returns the stylesheet for danger/delete action buttons.

        This style provides a red gradient background with hover, pressed,
        and disabled states for visual feedback.
        """
        return """
        QPushButton {
            background-color: #8b0000; /* Darker red for danger */
            border-radius: 5px;
            color: #ecf0f1; /* Light text */
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #a00000; /* Slightly lighter on hover */
        }
        QPushButton:pressed {
            background-color: #700000; /* Darker on pressed */
        }
        QPushButton:disabled {
            background-color: #1a1a1a; /* Disabled background */
            color: #7f8c8d; /* Disabled text */
        }
        """

    @staticmethod
    def get_success_button_style() -> str:
        """
        Returns the stylesheet for success/folder action buttons.

        This style provides a green gradient background with hover, pressed,
        and disabled states for visual feedback.
        """
        return """
        QPushButton {
            background-color: #006400; /* Darker green for success */
            border-radius: 5px;
            color: #ecf0f1; /* Light text */
            padding: 8px 16px;
            font-size: 11px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #008000; /* Slightly lighter on hover */
        }
        QPushButton:pressed {
            background-color: #004d00; /* Darker on pressed */
        }
        QPushButton:disabled {
            background-color: #1a1a1a; /* Disabled background */
            color: #7f8c8d; /* Disabled text */
        }
        """

    @staticmethod
    def get_group_style() -> str:
        """
        Returns the stylesheet for QGroupBox widgets.

        This style applies rounded borders, a bold title, and a white background.
        """
        return """
        QGroupBox {
            font-weight: bold;
            font-size: 15px;
            color: #ecf0f1; /* Light text for title */
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            background-color: #1a1a1a; /* Black background */
            margin-top: 5px;
            padding-top: 5px; 
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            background-color: #1a1a1a; /* Match groupbox background */
        }
        """

    @staticmethod
    def get_input_style() -> str:
        """
        Returns the stylesheet for QLineEdit (input) widgets.

        This style provides rounded borders, padding, and a distinct focus state.
        """
        return """
        QLineEdit {
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            padding: 8px 12px;
            font-size: 13px;
            background-color: #222222; /* Black input background */
            color: #ecf0f1; /* Light text */
            min-height: 20px;
        }
        QLineEdit:focus {
            border-color: #667eea; /* Accent color on focus */
            outline: none;
        }
        QLineEdit::placeholder {
            color: #95a5a6; /* Placeholder color */
        }
        """

    @staticmethod
    def get_checkbox_style() -> str:
        """
        Returns the stylesheet for QCheckBox widgets.

        This style customizes the appearance of the checkbox indicator
        for unchecked, checked, and hover states.
        """
        return """
        QCheckBox {
            font-size: 13px;
            color: #ecf0f1; /* Light text */
        }
        QCheckBox::indicator {
            width: 12px;
            height: 12px;
            border: 1px solid #333333; /* Darker border */
            border-radius: 3px;
            background-color: #222222; /* Black background */
        }
        QCheckBox::indicator:unchecked {
            background-color: #222222;
        }
        QCheckBox::indicator:checked {
            background-color: #667eea; /* Accent color when checked */
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMiAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDJMNC41IDhMMiA1LjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
        }
        QCheckBox::indicator:hover {
            border-color: #667eea; /* Accent color on hover */
        }
        """

    @staticmethod
    def get_tab_style() -> str:
        """
        Returns the stylesheet for QTabWidget components.

        This style applies rounded corners to the tab pane and customizes
        the appearance of individual tabs for selected and hover states.
        """
        return """
        QTabWidget::pane {
            border: 1px solid #333333;
            border-radius: 5px;
            background-color: #1a1a1a;
            padding: 15px;
            min-width: 300px; /* Reasonable minimum width */
        }
        QTabBar::tab {
            background: #222222;
            border: 1px solid #333333;
            padding: 8px 15px;
            font-size: 12px;
            font-weight: bold;
            color: #ecf0f1;
            text-align: center;
            white-space: nowrap;
        }
        QTabBar::tab:selected {
            background: #1a1a1a; /* Main background color when selected */
            border-bottom-color: #1a1a1a; /* Hide bottom border */
            color: #667eea; /* Accent color for selected tab */
        }
        QTabBar::tab:hover:!selected {
            background: #333333; /* Slightly lighter on hover */
        }
        """

    @staticmethod
    def get_list_style() -> str:
        """
        Returns the stylesheet for QListWidget components.

        This style provides rounded borders, padding, and distinct
        selected and hover states for list items.
        """
        return """
        QListWidget {
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            background-color: #1a1a1a; /* Black background */
            font-size: 13px;
            padding: 5px;
            color: #ecf0f1; /* Light text */
        }
        QListWidget::item {
            padding: 8px 5px;
            border-bottom: 1px solid #333333; /* Darker separator */
            border-radius: 3px;
            margin: 1px 0;
        }
        QListWidget::item:selected {
            background-color: #667eea; /* Accent color when selected */
            color: #ffffff;
            border: none;
        }
        QListWidget::item:hover {
            background-color: #222222; /* Slightly lighter on hover */
        }
        """

    @staticmethod
    def get_text_style() -> str:
        """
        Returns the stylesheet for QTextEdit widgets.

        This style applies rounded borders, padding, and a monospace font
        for displaying text content.
        """
        return """
        QTextEdit {
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            background-color: #222222; /* Black background */
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            padding: 10px;
            color: #ecf0f1; /* Light text */
            line-height: 1.4;
        }
        """

    @staticmethod
    def get_combo_box_style() -> str:
        """
        Returns the stylesheet for QComboBox widgets.

        This style provides rounded borders, padding, and customizes
        the dropdown arrow and item view appearance.
        """
        return """
        QComboBox {
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            padding: 8px 12px;
            font-size: 13px;
            background-color: #222222; /* Black background */
            color: #ecf0f1; /* Light text */
            min-height: 20px;
        }
        QComboBox:focus {
            border-color: #667eea; /* Accent color on focus */
            outline: none;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDYiIHN0cm9rZT0iI2VjZjBmMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+); /* Light arrow */
            width: 16px;
            height: 16px;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #333333; /* Darker border */
            border-radius: 5px;
            background-color: #222222; /* Black background */
            color: #ecf0f1; /* Light text */
            selection-background-color: #667eea; /* Accent color on selection */
        }
        """

    @staticmethod
    def create_app_icon_pixmap() -> QPixmap:
        """
        Programmatically creates a QPixmap representing the application icon.

        The icon is a stylized camera graphic with a gradient background.

        Returns:
            QPixmap: The generated application icon pixmap.
        """
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#667eea"))  # Background color

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw camera body
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QColor("white"))
        painter.drawRoundedRect(10, 20, 44, 30, 5, 5)

        # Draw camera lens
        painter.setBrush(QBrush(QColor("#667eea")))
        painter.drawEllipse(20, 28, 24, 24)

        # Draw camera lens center
        painter.setBrush(QBrush(QColor("white")))
        painter.drawEllipse(26, 34, 12, 12)

        painter.end()
        return pixmap

    @staticmethod
    def get_progress_style() -> str:
        """
        Returns the stylesheet for QProgressBar widgets.

        This style provides a modern, rounded progress bar with a gradient fill.
        """
        return """
        QProgressBar {
            border: 1px solid #333333; /* Darker border */
            border-radius: 8px;
            background-color: #222222; /* Black background */
            text-align: center;
            color: #ecf0f1; /* Light text */
            font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2); /* Accent gradient */
            border-radius: 7px;
        }
        """

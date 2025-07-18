from typing import Dict, Any

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QTabWidget,
    QFrame,
    QCheckBox,
    QGroupBox,
    QSplitter,
    QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.components import ModernButton, ModernProgressBar
from src.ui.styles import AppStyles


class PanelBuilder:
    """
    A utility class for building and configuring UI panels and their components.

    This class encapsulates the creation of the left control panel and the right
    tabbed panel, promoting modularity and reusability in the UI structure.
    It initializes and holds references to all major UI widgets.
    """

    def __init__(self, main_window_instance: Any):
        """
        Initializes the PanelBuilder with a reference to the main window instance.

        This allows connecting signals from UI components to slots in the main window.

        Args:
            main_window_instance (Any): A reference to the main application window
                                        (e.g., an instance of InstagramDownloaderGUI).
        """
        self.main_window = main_window_instance
        # Initialize all UI elements that will be built
        self.url_input = QLineEdit()
        self.add_button = ModernButton("➕ Add to Queue")
        self.downloader_combo = QComboBox()
        self.video_check = QCheckBox("📹 Download Video")
        self.thumbnail_check = QCheckBox("🖼️ Download Thumbnail")
        self.audio_check = QCheckBox("🎵 Extract Audio")
        self.caption_check = QCheckBox("📝 Get Caption")
        self.transcribe_check = QCheckBox("🎤 Transcribe Audio")
        self.download_button = ModernButton("🚀 Start Download")
        self.clear_button = ModernButton("🗑️ Clear Queue")
        self.folder_button = ModernButton("📁 Open Downloads")
        self.overall_progress = ModernProgressBar()
        self.progress_label = QLabel("Ready to start downloading...")
        self.queue_list = QListWidget()
        self.results_text = QTextEdit()
        self.tab_widget = QTabWidget()

    def create_main_layout(self, central_widget: QWidget):
        """
        Creates and sets up the main application layout within the central widget.

        This method arranges the left control panel and the right tabbed panel
        using a QSplitter to allow for resizable sections.

        Args:
            central_widget (QWidget): The central widget of the QMainWindow
                                      where the main layout will be applied.
        """
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])  # Initial sizes for the panels
        splitter.setStretchFactor(0, 0)  # Left panel not stretchable
        splitter.setStretchFactor(1, 1)  # Right panel stretches

        main_layout.addWidget(splitter)

    def _create_left_panel(self) -> QWidget:
        """
        Creates and configures the left control panel of the application.

        This panel contains input fields, download options, and control buttons.

        Returns:
            QWidget: The configured left panel widget.
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet(AppStyles.get_panel_style())
        panel.setMaximumWidth(500)

        layout = QVBoxLayout(panel)
        layout.setSpacing(20)

        top_layout = QVBoxLayout()
        self._add_title_section(top_layout)
        self._add_url_input_section(top_layout)
        self._add_downloader_selection_section(top_layout)
        self._add_download_options_section(top_layout)

        layout.addLayout(top_layout)
        layout.addStretch()

        self._add_control_buttons_section(layout)
        self._add_progress_section(layout)

        return panel

    def _add_title_section(self, layout: QVBoxLayout):
        """
        Adds the application title and subtitle to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the title and subtitle labels will be added.
        """
        title_label = QLabel("Instagram Reels\nDownloader")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Download, Extract & Transcribe")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(subtitle_label)

    def _add_url_input_section(self, layout: QVBoxLayout):
        """
        Adds the URL input field and "Add to Queue" button to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the URL input section will be added.
        """
        url_group = QGroupBox("📎 Add Reel URL")
        url_group.setStyleSheet(AppStyles.get_group_style())
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(10)

        self.url_input.setPlaceholderText("Paste Instagram Reel URL here...")
        self.url_input.setStyleSheet(AppStyles.get_input_style())
        # Connect returnPressed signal to main window's add_to_queue slot
        self.url_input.returnPressed.connect(self.main_window.add_to_queue)

        # Connect add_button clicked signal to main window's add_to_queue slot
        self.add_button.clicked.connect(self.main_window.add_to_queue)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_button)

        layout.addWidget(url_group)

    def _add_downloader_selection_section(self, layout: QVBoxLayout):
        """
        Adds the downloader selection combobox to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the downloader selection will be added.
        """
        downloader_group = QGroupBox("⬇️ Downloader")
        downloader_group.setStyleSheet(AppStyles.get_group_style())
        downloader_layout = QVBoxLayout(downloader_group)
        downloader_layout.setSpacing(10)

        self.downloader_combo.addItems(["Instaloader", "yt-dlp"])
        self.downloader_combo.setStyleSheet(AppStyles.get_combo_box_style())

        downloader_layout.addWidget(self.downloader_combo)
        downloader_group.setLayout(downloader_layout)
        layout.addWidget(downloader_group)

    def _add_download_options_section(self, layout: QVBoxLayout):
        """
        Adds the download options checkboxes to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the download options will be added.
        """
        options_group = QGroupBox("⚙️ Download Options")
        options_group.setStyleSheet(AppStyles.get_group_style())
        options_group.setMinimumHeight(110)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        # Set initial checked state for checkboxes
        self.video_check.setChecked(True)
        self.thumbnail_check.setChecked(True)
        self.audio_check.setChecked(True)
        self.caption_check.setChecked(True)
        self.transcribe_check.setChecked(False)

        checkboxes = [
            self.video_check,
            self.thumbnail_check,
            self.audio_check,
            self.caption_check,
            self.transcribe_check,
        ]

        for checkbox in checkboxes:
            checkbox.setStyleSheet(AppStyles.get_checkbox_style())
            checkbox.setMinimumHeight(25)
            options_layout.addWidget(checkbox)

        layout.addWidget(options_group)

    def _add_control_buttons_section(self, layout: QVBoxLayout):
        """
        Adds the control buttons (Start Download, Clear Queue, Open Downloads)
        to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the control buttons will be added.
        """
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)

        self.download_button.clicked.connect(self.main_window.start_download)
        self.clear_button.clicked.connect(self.main_window.clear_queue)
        self.clear_button.setStyleSheet(AppStyles.get_danger_button_style())
        self.folder_button.clicked.connect(self.main_window.open_downloads_folder)
        self.folder_button.setStyleSheet(AppStyles.get_success_button_style())

        controls_layout.addWidget(self.download_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.folder_button)

        layout.addLayout(controls_layout)

    def _add_progress_section(self, layout: QVBoxLayout):
        """
        Adds the overall progress bar and label to a given QVBoxLayout.

        Args:
            layout (QVBoxLayout): The layout to which the progress section will be added.
        """
        progress_group = QGroupBox("📊 Overall Progress")
        progress_group.setStyleSheet(AppStyles.get_group_style())
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)

        self.progress_label.setStyleSheet(
            """
            color: #2c3e50;
            font-size: 13px;
            font-weight: bold;
            padding: 2px;
        """
        )
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

    def _create_right_panel(self) -> QWidget:
        """
        Creates and configures the right panel with tabbed interface for queue and results.

        Returns:
            QWidget: The configured right panel widget.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget.setStyleSheet(AppStyles.get_tab_style())
        self.tab_widget.tabBar().setExpanding(True)

        queue_widget = self._create_queue_tab()
        results_widget = self._create_results_tab()

        self.tab_widget.addTab(queue_widget, "📋 Download Queue")
        self.tab_widget.addTab(results_widget, "✅ Results")

        layout.addWidget(self.tab_widget)

        return panel

    def _create_queue_tab(self) -> QWidget:
        """
        Creates the "Download Queue" tab content.

        This tab displays a list of URLs added to the download queue.

        Returns:
            QWidget: The widget containing the queue tab's content.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QLabel("Download Queue")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        self.queue_list.setStyleSheet(AppStyles.get_list_style())
        self.queue_list.setMinimumHeight(400)

        layout.addWidget(self.queue_list)

        return widget

    def _create_results_tab(self) -> QWidget:
        """
        Creates the "Results" tab content.

        This tab displays the detailed results and logs of completed downloads.

        Returns:
            QWidget: The widget containing the results tab's content.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QLabel("Download Results")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        self.results_text.setStyleSheet(AppStyles.get_text_style())
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(400)

        layout.addWidget(self.results_text)

        return widget

    def get_ui_elements(self) -> Dict[str, Any]:
        """
        Returns a dictionary of key UI elements initialized by the PanelBuilder.

        This allows the main window to easily access and interact with specific
        widgets created by the builder.

        Returns:
            Dict[str, Any]: A dictionary where keys are descriptive names
                            and values are the corresponding PyQt widgets.
        """
        return {
            "url_input": self.url_input,
            "add_button": self.add_button,
            "downloader_combo": self.downloader_combo,
            "video_check": self.video_check,
            "thumbnail_check": self.thumbnail_check,
            "audio_check": self.audio_check,
            "caption_check": self.caption_check,
            "transcribe_check": self.transcribe_check,
            "download_button": self.download_button,
            "clear_button": self.clear_button,
            "folder_button": self.folder_button,
            "overall_progress": self.overall_progress,
            "progress_label": self.progress_label,
            "queue_list": self.queue_list,
            "results_text": self.results_text,
            "tab_widget": self.tab_widget,
        }

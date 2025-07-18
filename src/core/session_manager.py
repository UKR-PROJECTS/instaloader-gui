from pathlib import Path
from datetime import datetime
from typing import Optional


class SessionManager:
    """
    Manages the creation and retrieval of session-specific download folders.

    This class ensures that all downloads for a given application session
    are organized into a unique, timestamped directory within a base download
    directory.
    """

    def __init__(self, base_download_dir: str = "downloads"):
        """
        Initializes the SessionManager.

        Args:
            base_download_dir: The base directory where session folders will be created.
                               Defaults to "downloads".
        """
        self.base_download_dir = Path(base_download_dir)
        self.session_folder: Optional[Path] = None

    def setup_session_folder(self) -> Path:
        """
        Creates a new timestamped session folder for the current download session.

        The folder name is generated using the current date and time to ensure uniqueness.
        Parent directories are created if they don't exist.

        Returns:
            The Path object representing the newly created session folder.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder = self.base_download_dir / f"session_{timestamp}"
        self.session_folder.mkdir(parents=True, exist_ok=True)
        return self.session_folder

    def get_session_folder(self) -> Optional[Path]:
        """
        Returns the path to the current session folder.

        Returns:
            A Path object if a session folder has been set up, otherwise None.
        """
        return self.session_folder

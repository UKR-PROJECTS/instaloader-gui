import sys
from pathlib import Path


def get_base_path() -> Path:
    """
    Determines the base path for loading application resources.

    This function intelligently identifies the root directory for resources,
    whether the application is running from source code or as a frozen
    executable (e.g., bundled by PyInstaller).

    Returns:
        Path: The base directory where resources are located.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as a bundled executable (one-file mode)
        # Resources are typically extracted to a temporary directory accessible via _MEIPASS
        return Path(sys._MEIPASS)
    else:
        # Running from source or as a non-bundled executable (one-folder mode)
        # The base path is two levels up from the current file (src/utils/resource_loader.py)
        return Path(__file__).resolve().parent.parent


def get_resource_path(relative_path: str) -> Path:
    """
    Constructs the absolute path to a specified resource.

    This function accounts for different deployment scenarios:
    1. When running from source: Resources are located relative to the 'src' directory.
    2. When running as a PyInstaller one-file executable: Resources are in `sys._MEIPASS`.
    3. When running as a PyInstaller one-folder executable: Resources are alongside the executable.

    Args:
        relative_path (str): The path to the resource relative to the base resource directory
                             (e.g., "bin/yt-dlp.exe", "favicon.ico", "whisper/base.pt").

    Returns:
        Path: The absolute Path object to the requested resource.
    """
    if getattr(sys, "frozen", False):
        # Application is running as a frozen executable (e.g., PyInstaller)
        if hasattr(sys, "_MEIPASS"):
            # One-file bundle: resources are in a temporary directory
            base_path = Path(sys._MEIPASS)
            # For some external binaries (like yt-dlp.exe), they might be placed
            # directly next to the executable, not inside _MEIPASS.
            # We check for this specific case.
            external_path = Path(sys.executable).parent / relative_path
            if external_path.exists():
                return external_path
        else:
            # One-folder bundle: resources are in the same directory as the executable
            base_path = Path(sys.executable).parent
    else:
        # Application is running from source code
        # Assumes this file is located at `src/utils/resource_loader.py`
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path

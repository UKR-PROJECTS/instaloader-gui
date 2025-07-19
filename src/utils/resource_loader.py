import sys
from pathlib import Path
from typing import cast, Any


def get_base_path() -> Path:
    """
    Determines the base path for loading application resources.

    This function intelligently identifies the root directory for resources,
    whether the application is running from source code or as a frozen
    executable (e.g., bundled by PyInstaller).

    Returns:
        Path: The base directory where resources are located.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller sets _MEIPASS for one-file bundles
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(cast(str, meipass))

        # For one-folder bundles, use executable directory
        return Path(sys.executable).parent
    else:
        # Running from source
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
    # Check if running as a frozen executable (e.g., PyInstaller)
    if getattr(sys, "frozen", False):
        # For one-file bundle, assets are next to the exe, not in _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            # The executable is in the parent directory of _MEIPASS
            executable_dir = Path(sys.executable).parent
            resource_path = executable_dir / relative_path
            if resource_path.exists():
                return resource_path
            # If not found next to exe, check inside _MEIPASS (for non-asset files)
            return Path(cast(str, meipass)) / relative_path
        else:  # One-folder bundle
            return Path(sys.executable).parent / relative_path
    else:
        # Application is running from source code
        base_path = Path(__file__).resolve().parent.parent
        return base_path / relative_path

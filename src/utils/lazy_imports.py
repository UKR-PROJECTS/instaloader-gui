"""
This module provides utility functions for lazy importing of optional dependencies.

Each function attempts to import a specific package only when it is first needed,
and caches the imported module or class in a global variable for future use.
If the required package is not installed, an ImportError with a descriptive message is raised,
guiding the user on which dependency is missing.

This approach optimizes application startup time and memory usage by avoiding
loading heavy or non-essential libraries until they are explicitly required.
"""

# Global variables to cache lazy-loaded modules
_instaloader = None
_moviepy = None
_whisper = None
_requests = None
_PIL = None


def lazy_import_requests():
    """
    Lazily imports the 'requests' library.

    Raises:
        ImportError: If the 'requests' package is not installed.

    Returns:
        module: The imported 'requests' module.
    """
    global _requests
    if _requests is None:
        try:
            import requests

            _requests = requests
        except ImportError as e:
            raise ImportError(
                "The 'requests' package is required for this functionality. "
                "Please install it using: pip install requests"
            ) from e
    return _requests


def lazy_import_instaloader():
    """
    Lazily imports the 'instaloader' library.

    Raises:
        ImportError: If the 'instaloader' package is not installed.

    Returns:
        module: The imported 'instaloader' module.
    """
    global _instaloader
    if _instaloader is None:
        try:
            import instaloader

            _instaloader = instaloader
        except ImportError as e:
            raise ImportError(
                "The 'instaloader' package is required for this functionality. "
                "Please install it using: pip install instaloader"
            ) from e
    return _instaloader


def lazy_import_moviepy():
    """
    Lazily imports 'VideoFileClip' from the 'moviepy.editor' module.

    Raises:
        ImportError: If the 'moviepy' package is not installed.

    Returns:
        class: The 'VideoFileClip' class.
    """
    global _moviepy
    if _moviepy is None:
        try:
            from moviepy.editor import VideoFileClip

            _moviepy = VideoFileClip
        except ImportError as e:
            raise ImportError(
                "The 'moviepy' package is required for audio extraction. "
                "Please install it using: pip install moviepy"
            ) from e
    return _moviepy


def lazy_import_whisper():
    """
    Lazily imports the whisper module and returns its load_model function.

    Raises:
        ImportError: If the 'openai-whisper' package is not installed.

    Returns:
        function: The whisper.load_model function.
    """
    global _whisper
    if _whisper is None:
        try:
            import whisper

            _whisper = whisper.load_model
        except ImportError as e:
            raise ImportError(
                "The 'openai-whisper' package is required for transcription. "
                "Please install it using: pip install openai-whisper"
            ) from e
    return _whisper


def lazy_import_pil():
    """
    Lazily imports the 'Image' class from the 'PIL' (Pillow) library.

    Raises:
        ImportError: If the 'Pillow' package is not installed.

    Returns:
        class: The 'PIL.Image' class.
    """
    global _PIL
    if _PIL is None:
        try:
            from PIL import Image

            _PIL = Image
        except ImportError as e:
            raise ImportError(
                "The 'Pillow' package is required for image processing. "
                "Please install it using: pip install Pillow"
            ) from e
    return _PIL

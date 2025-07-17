"""
This module provides utility functions for lazy importing of optional dependencies.
Each function attempts to import a specific package only when it is first needed,
and caches the imported module or class in a global variable for future use.
If the required package is not installed, an ImportError with a descriptive message is raised.

Lazy imports implemented for:
- instaloader
- moviepy.editor.VideoFileClip
- whisper
- requests
- PIL.Image
"""

# Global variables for lazy-loaded modules
_instaloader = None
_moviepy = None
_whisper = None
_requests = None
_PIL = None


def lazy_import_requests():
    """Lazy import requests when needed"""
    global _requests
    if _requests is None:
        try:
            import requests

            _requests = requests
        except ImportError as e:
            raise ImportError(f"Missing requests package: {e}")
    return _requests


def lazy_import_instaloader():
    """Lazy import instaloader when needed"""
    global _instaloader
    if _instaloader is None:
        try:
            import instaloader

            _instaloader = instaloader
        except ImportError as e:
            raise ImportError(f"Missing instaloader package: {e}")
    return _instaloader


def lazy_import_moviepy():
    """Lazy import moviepy when needed"""
    global _moviepy
    if _moviepy is None:
        try:
            from moviepy.editor import VideoFileClip

            _moviepy = VideoFileClip
        except ImportError as e:
            raise ImportError(f"Missing moviepy package: {e}")
    return _moviepy


def lazy_import_whisper():
    """Lazy import whisper when needed"""
    global _whisper
    if _whisper is None:
        try:
            import whisper

            _whisper = whisper
        except ImportError as e:
            raise ImportError(f"Missing whisper package: {e}")
    return _whisper


def lazy_import_pil():
    """Lazy import PIL when needed"""
    global _PIL
    if _PIL is None:
        try:
            from PIL import Image

            _PIL = Image
        except ImportError as e:
            raise ImportError(f"Missing PIL package: {e}")
    return _PIL

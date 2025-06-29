"""
This module provides utility functions for lazy importing of commonly used packages.
Each function imports its respective package only when needed, and caches the imported
module or class in a global variable for subsequent use. This approach helps to reduce
initial load time and memory usage, especially when some dependencies are optional or
not always required.

Lazy imports provided:
- instaloader
- moviepy.editor.VideoFileClip
- requests
- PIL.Image
"""

# Global variables for lazy-loaded modules
_instaloader = None
_moviepy = None
_requests = None
_PIL = None


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

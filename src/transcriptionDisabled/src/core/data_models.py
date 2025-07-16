"""
This module defines data models used in the application.

Currently, it provides the ReelItem dataclass, which encapsulates all relevant
information for an Instagram reel download task, including URLs, file paths,
status, progress, captions, transcripts, and error messages.
"""

from dataclasses import dataclass


@dataclass
class ReelItem:
    """
    Data class for reel download items

    Attributes:
        url: Instagram reel URL
        title: Display title for the reel
        status: Current download status
        progress: Download progress percentage
        thumbnail_path: Path to saved thumbnail
        video_path: Path to saved video file
        audio_path: Path to extracted audio
        caption: Reel caption text
        error_message: Error details if download fails
        folder_path: Path to reel's download folder
    """

    url: str
    title: str = ""
    status: str = "Pending"
    progress: int = 0
    thumbnail_path: str = ""
    video_path: str = ""
    audio_path: str = ""
    caption: str = ""
    transcript: str = ""
    error_message: str = ""
    folder_path: str = ""

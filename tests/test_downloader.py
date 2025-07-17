import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.core.downloader import ReelDownloader
from src.core.data_models import ReelItem
from src.agents import instaloader as instaloader_agent
from src.agents import yt_dlp as yt_dlp_agent


class TestReelDownloader(unittest.TestCase):
    """Tests for the ReelDownloader class."""

    def setUp(self):
        """Set up the test environment."""
        self.reel_items = [ReelItem(url="https://www.instagram.com/reel/Cxyz123/")]
        self.download_options: dict[str, bool | str] = {
            "video": True,
            "audio": True,
            "thumbnail": True,
            "caption": True,
            "transcribe": False,
            "downloader": "Instaloader",
        }
        self.downloader = ReelDownloader(self.reel_items, self.download_options)
        # Mock the session folder to avoid creating it
        self.downloader.session_folder = Path("test_downloads/session_123")

    def test_extract_shortcode_reel(self):
        """Test extracting a shortcode from a standard /reel/ URL."""
        url = "https://www.instagram.com/reel/Cxyz123/?utm_source=ig_web_copy_link"
        shortcode = instaloader_agent._extract_shortcode(url)
        self.assertEqual(shortcode, "Cxyz123")

    def test_extract_shortcode_post(self):
        """Test extracting a shortcode from a /p/ URL."""
        url = "https://www.instagram.com/p/Cabc456/"
        shortcode = instaloader_agent._extract_shortcode(url)
        self.assertEqual(shortcode, "Cabc456")

    def test_extract_shortcode_invalid(self):
        """Test that an invalid URL returns None."""
        url = "https://www.instagram.com/"
        shortcode = instaloader_agent._extract_shortcode(url)
        self.assertIsNone(shortcode)

    @patch("src.core.downloader.ReelDownloader._download_with_yt_dlp")
    @patch("src.core.downloader.ReelDownloader._download_with_instaloader")
    def test_download_process_calls_instaloader(
        self, mock_instaloader_download, mock_yt_dlp_download
    ):
        """Test that the main download process calls the instaloader agent."""
        self.downloader.download_options["downloader"] = "Instaloader"
        mock_instaloader_download.return_value = {"status": "success"}
        self.downloader._process_downloads()
        mock_instaloader_download.assert_called_once()
        mock_yt_dlp_download.assert_not_called()

    @patch("src.core.downloader.ReelDownloader._download_with_yt_dlp")
    @patch("src.core.downloader.ReelDownloader._download_with_instaloader")
    def test_download_process_calls_yt_dlp(
        self, mock_instaloader_download, mock_yt_dlp_download
    ):
        """Test that the main download process calls the yt-dlp agent."""
        self.downloader.download_options["downloader"] = "yt-dlp"
        mock_yt_dlp_download.return_value = {"status": "success"}
        self.downloader._process_downloads()
        mock_yt_dlp_download.assert_called_once()
        mock_instaloader_download.assert_not_called()

    @patch("src.core.downloader.ReelDownloader._download_with_yt_dlp")
    @patch("src.core.downloader.ReelDownloader._download_with_instaloader")
    def test_download_process_calls_with_transcription(
        self, mock_instaloader_download, mock_yt_dlp_download
    ):
        """Test that the main download process calls the transcription method when enabled."""
        self.downloader.download_options["transcribe"] = True
        mock_instaloader_download.return_value = {
            "status": "success",
            "folder_path": "test_folder",
        }

        # Create a mock for _handle_transcription
        with patch.object(
            self.downloader, "_handle_transcription"
        ) as mock_transcription:
            self.downloader._process_downloads()
            mock_instaloader_download.assert_called_once()
            mock_yt_dlp_download.assert_not_called()
            mock_transcription.assert_called_once_with(
                {"status": "success", "folder_path": "test_folder"}, 1
            )

    @patch(
        "src.core.downloader.ReelDownloader._download_with_instaloader",
        side_effect=Exception("Instaloader failed"),
    )
    @patch("src.core.downloader.ReelDownloader._download_with_yt_dlp")
    def test_fallback_mechanism(self, mock_yt_dlp_download, mock_instaloader_download):
        """Test that the downloader falls back to the secondary agent on failure."""
        self.downloader._process_downloads()
        mock_instaloader_download.assert_called_once()
        mock_yt_dlp_download.assert_called_once()


if __name__ == "__main__":
    unittest.main()

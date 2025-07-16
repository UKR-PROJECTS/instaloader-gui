import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add the correct parent directory to the Python path to allow for 'from src...' imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Determine which of the two 'src' parent directories to use
# Add transcriptionEnabled src to path
src_enabled_path = os.path.join(project_root, "src", "transcriptionEnabled")
sys.path.insert(0, src_enabled_path)
from src.core.downloader import ReelDownloader as ReelDownloaderEnabled
from src.core.data_models import ReelItem

# Add transcriptionDisabled src to path
src_disabled_path = os.path.join(project_root, "src", "transcriptionDisabled")
sys.path.insert(0, src_disabled_path)
from src.core.downloader import ReelDownloader as ReelDownloaderDisabled


class TestReelDownloader(unittest.TestCase):
    """Tests for the ReelDownloader class."""

    def setUp(self):
        """Set up the test environment."""
        self.reel_items = [ReelItem(url="https://www.instagram.com/reel/Cxyz123/")]
        self.download_options_disabled = {
            "video": True,
            "audio": True,
            "thumbnail": True,
            "caption": True,
        }
        self.download_options_enabled = {
            "video": True,
            "audio": True,
            "thumbnail": True,
            "caption": True,
            "transcribe": True,
        }
        self.downloader_disabled = ReelDownloaderDisabled(
            self.reel_items, self.download_options_disabled
        )
        self.downloader_enabled = ReelDownloaderEnabled(
            self.reel_items, self.download_options_enabled
        )

    def test_extract_shortcode_reel(self):
        """Test extracting a shortcode from a standard /reel/ URL."""
        url = "https://www.instagram.com/reel/Cxyz123/?utm_source=ig_web_copy_link"
        shortcode = self.downloader_disabled._extract_shortcode(url)
        self.assertEqual(shortcode, "Cxyz123")

    def test_extract_shortcode_post(self):
        """Test extracting a shortcode from a /p/ URL."""
        url = "https://www.instagram.com/p/Cabc456/"
        shortcode = self.downloader_disabled._extract_shortcode(url)
        self.assertEqual(shortcode, "Cabc456")

    def test_extract_shortcode_invalid(self):
        """Test that an invalid URL returns None."""
        url = "https://www.instagram.com/"
        shortcode = self.downloader_disabled._extract_shortcode(url)
        self.assertIsNone(shortcode)

    @patch("src.core.downloader.lazy_import_instaloader")
    @patch("src.core.downloader.lazy_import_requests")
    @patch("src.core.downloader.lazy_import_moviepy")
    @patch("src.core.downloader.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_process_calls_disabled(
        self, mock_open_file, mock_mkdir, mock_moviepy, mock_requests, mock_instaloader
    ):
        """Test that the main download process calls the correct helper methods for the disabled version."""
        # Mock the external libraries and their return values
        mock_instaloader.return_value.Instaloader.return_value.context = MagicMock()
        mock_post = MagicMock()
        mock_post.video_url = "http://fake.url/video.mp4"
        mock_post.thumbnail_url = "http://fake.url/thumb.jpg"
        mock_post.caption = "Fake caption"
        mock_instaloader.return_value.Post.from_shortcode.return_value = mock_post

        mock_requests.return_value.get.return_value.iter_content.return_value = [
            b"fakedata"
        ]

        # Mock moviepy to avoid actual processing
        mock_video_clip = MagicMock()
        mock_audio_clip = MagicMock()
        mock_video_clip.audio = mock_audio_clip
        mock_moviepy.return_value.return_value = mock_video_clip

        # Mock the downloader's own methods to check if they are called
        self.downloader_disabled._download_video = MagicMock()
        self.downloader_disabled._download_thumbnail = MagicMock()
        self.downloader_disabled._extract_audio = MagicMock()
        self.downloader_disabled._save_caption = MagicMock()

        # Run the main thread logic
        self.downloader_disabled.run()

        # Assert that the setup methods were called
        self.assertTrue(mock_mkdir.called)

        # Assert that the download helper methods were called
        self.downloader_disabled._download_video.assert_called_once()
        self.downloader_disabled._download_thumbnail.assert_called_once()
        self.downloader_disabled._extract_audio.assert_called_once()
        self.downloader_disabled._save_caption.assert_called_once()

    @patch("src.core.downloader.lazy_import_instaloader")
    @patch("src.core.downloader.lazy_import_requests")
    @patch("src.core.downloader.lazy_import_moviepy")
    @patch("src.core.downloader.lazy_import_whisper")
    @patch("src.core.downloader.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_process_calls_enabled(
        self,
        mock_open_file,
        mock_mkdir,
        mock_whisper,
        mock_moviepy,
        mock_requests,
        mock_instaloader,
    ):
        """Test that the main download process calls the correct helper methods for the enabled version."""
        # Mock the external libraries and their return values
        mock_instaloader.return_value.Instaloader.return_value.context = MagicMock()
        mock_post = MagicMock()
        mock_post.video_url = "http://fake.url/video.mp4"
        mock_post.thumbnail_url = "http://fake.url/thumb.jpg"
        mock_post.caption = "Fake caption"
        mock_instaloader.return_value.Post.from_shortcode.return_value = mock_post

        mock_requests.return_value.get.return_value.iter_content.return_value = [
            b"fakedata"
        ]

        # Mock moviepy to avoid actual processing
        mock_video_clip = MagicMock()
        mock_audio_clip = MagicMock()
        mock_video_clip.audio = mock_audio_clip
        mock_moviepy.return_value.return_value = mock_video_clip

        # Mock whisper
        mock_whisper.return_value.load_model.return_value.transcribe.return_value = {
            "text": "fake transcript"
        }

        # Mock the downloader's own methods to check if they are called
        self.downloader_enabled._download_video = MagicMock()
        self.downloader_enabled._download_thumbnail = MagicMock()
        self.downloader_enabled._extract_audio = MagicMock()
        self.downloader_enabled._save_caption = MagicMock()
        self.downloader_enabled._transcribe_audio = MagicMock()

        # Run the main thread logic
        self.downloader_enabled.run()

        # Assert that the setup methods were called
        self.assertTrue(mock_mkdir.called)

        # Assert that the download helper methods were called
        self.downloader_enabled._download_video.assert_called_once()
        self.downloader_enabled._download_thumbnail.assert_called_once()
        self.downloader_enabled._extract_audio.assert_called_once()
        self.downloader_enabled._save_caption.assert_called_once()
        self.downloader_enabled._transcribe_audio.assert_called_once()


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
from src.core.session_manager import SessionManager


class TestSessionManager(unittest.TestCase):
    """Tests for the SessionManager class."""

    def setUp(self):
        self.base_dir = "test_downloads"
        self.session_manager = SessionManager(self.base_dir)

    def test_setup_session_folder(self):
        """Test creating a new session folder."""
        with patch("src.core.session_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250101_123000"
            session_folder = self.session_manager.setup_session_folder()

            expected_path = Path(self.base_dir) / "session_20250101_123000"
            self.assertEqual(session_folder, expected_path)
            self.assertTrue(expected_path.exists())

            # Cleanup
            os.rmdir(expected_path)

    def test_get_session_folder_before_setup(self):
        """Test getting session folder before setup returns None."""
        self.assertIsNone(self.session_manager.get_session_folder())

    def test_get_session_folder_after_setup(self):
        """Test getting session folder after setup returns correct path."""
        session_folder = self.session_manager.setup_session_folder()
        self.assertEqual(self.session_manager.get_session_folder(), session_folder)

        # Cleanup
        os.rmdir(session_folder)


if __name__ == "__main__":
    unittest.main()

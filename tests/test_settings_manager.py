import unittest
from unittest.mock import patch, mock_open
import json
from pathlib import Path
from src.core.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    """Tests for the SettingsManager class."""

    def setUp(self):
        self.settings_file = "test_settings.json"
        self.manager = SettingsManager(self.settings_file)

    @patch("pathlib.Path.exists", return_value=True)
    def test_load_settings_existing_file(self, mock_exists):
        """Test loading settings from an existing file."""
        test_data = {"theme": "dark", "language": "en"}

        with patch(
            "builtins.open", mock_open(read_data=json.dumps(test_data))
        ) as mock_file:
            self.manager.load_settings()
            self.assertEqual(self.manager.settings, test_data)

    def test_load_settings_missing_file(self):
        """Test loading settings when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            self.manager.load_settings()
            self.assertEqual(self.manager.settings, {})

    def test_save_settings(self):
        """Test saving settings updates the file."""
        test_data = {"new_setting": "value"}

        with patch("builtins.open", mock_open()) as mock_file:
            self.manager.save_settings(test_data)
            mock_file.assert_called_with(
                Path(self.settings_file), "w", encoding="utf-8"
            )
            # Verify JSON was written correctly
            handle = mock_file()
            written_data = "".join(call[0][0] for call in handle.write.call_args_list)
            self.assertEqual(json.loads(written_data), test_data)

    def test_get_setting(self):
        """Test retrieving a setting value."""
        self.manager.settings = {"key": "value"}
        self.assertEqual(self.manager.get_setting("key"), "value")
        self.assertEqual(self.manager.get_setting("missing", "default"), "default")

    def test_set_setting(self):
        """Test updating a setting and saving automatically."""
        with patch.object(self.manager, "save_settings") as mock_save:
            self.manager.set_setting("theme", "light")
            self.assertEqual(self.manager.settings["theme"], "light")
            mock_save.assert_called_once_with(self.manager.settings)

    def test_error_handling_during_load(self):
        """Test error handling during settings load."""
        with patch("builtins.open", side_effect=Exception("Test error")):
            self.manager.load_settings()
            self.assertEqual(self.manager.settings, {})

    def test_error_handling_during_save(self):
        """Test error handling during settings save."""
        with patch("builtins.open", side_effect=Exception("Test error")):
            # Should not raise exception
            self.manager.save_settings({"key": "value"})


if __name__ == "__main__":
    unittest.main()

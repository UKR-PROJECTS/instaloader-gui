import json
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    """
    Manages application settings, including loading from and saving to a JSON file.

    This class provides methods to load settings from a specified JSON file,
    save current settings to the file, and retrieve or set individual settings.
    It handles file I/O errors gracefully.
    """

    def __init__(self, settings_file: str = "settings.json"):
        """
        Initializes the SettingsManager.

        Args:
            settings_file: The name of the JSON file where settings will be stored.
                           Defaults to "settings.json".
        """
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = {}
        self.load_settings()

    def load_settings(self):
        """
        Loads application settings from the JSON file.

        If the settings file does not exist or an error occurs during loading,
        the settings dictionary will be initialized as empty.
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
        except Exception:
            # Log the error if a proper logging mechanism is in place
            self.settings = {}  # Ensure settings is a dict even on error

    def save_settings(self, current_settings: Dict[str, Any]):
        """
        Saves application settings to the JSON file.

        Updates the internal settings dictionary with the provided `current_settings`
        and then writes the complete settings to the file.

        Args:
            current_settings: A dictionary containing the settings to be saved.
                              These will be merged with existing settings.
        """
        try:
            self.settings.update(current_settings)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            # Log the error if a proper logging mechanism is in place
            pass

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a specific setting by its key.

        Args:
            key: The key of the setting to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value if the key is not found.
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """
        Sets a specific setting by its key and immediately saves all settings to the file.

        Args:
            key: The key of the setting to set.
            value: The value to assign to the setting.
        """
        self.settings[key] = value
        self.save_settings(self.settings)

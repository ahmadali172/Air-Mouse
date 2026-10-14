"""
Configuration manager: loads and saves application settings as JSON.
"""

import copy
import json
import os


class ConfigManager:
    """Manages application configuration with save/load support."""

    DEFAULT_CONFIG = {
        "camera": {
            "index": 0,
            "resolution_width": 640,
            "resolution_height": 480
        },
        "tracking": {
            "max_hands": 1,
            "detection_confidence": 0.5,
            "tracking_confidence": 0.5
        },
        "cursor": {
            "speed": 1.5,
            "smoothing": 0.3,
            "margin": 5
        },
        "gestures": {
            "pinch_threshold": 0.12,
            "click_cooldown": 0.5
        },
        "ui": {
            "show_preview": True,
            "window_width": 300,
            "window_height": 400
        }
    }

    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self):
        """Create the config directory if it doesn't exist."""
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def load(self):
        """Load configuration from file, or keep defaults if there is no file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                self._merge_config(self.config, loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")

    def save(self):
        """Save the current configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_config(self, default, loaded):
        """Recursively merge loaded values into the default config."""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value

    def get(self, *keys):
        """
        Get a value by walking through nested keys.
        Example: config.get('cursor', 'speed')
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def set(self, *keys, value):
        """
        Set a value by walking through nested keys.
        Example: config.set('cursor', 'speed', value=2.0)
        """
        if len(keys) < 1:
            return False

        current = self.config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
        return True

    def reset_to_defaults(self):
        """Reset all settings to their default values and save them."""
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.save()
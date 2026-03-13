"""Settings management — reads and writes StreamController JSON settings files."""

import json
import os
from typing import Any, Optional


def load_json(path: str) -> dict:
    """Load a JSON file, returning {} if missing or corrupt."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_json(path: str, data: dict):
    """Save a dictionary to a JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


class SettingsManager:
    """Manages app-level and deck-level settings."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.settings_dir = os.path.join(data_path, "settings")
        self.app_settings_path = os.path.join(self.settings_dir, "settings.json")
        self.page_settings_path = os.path.join(self.settings_dir, "pages.json")

    # --- App settings ---

    def get_app_settings(self) -> dict:
        return load_json(self.app_settings_path)

    def save_app_settings(self, settings: dict):
        save_json(self.app_settings_path, settings)

    def get_app_setting(self, *keys: str, default: Any = None) -> Any:
        """Get a nested app setting by key path."""
        settings = self.get_app_settings()
        for key in keys:
            if not isinstance(settings, dict):
                return default
            settings = settings.get(key, default)
        return settings

    def set_app_setting(self, value: Any, *keys: str):
        """Set a nested app setting by key path."""
        settings = self.get_app_settings()
        current = settings
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        self.save_app_settings(settings)

    # --- Deck settings ---

    def get_deck_settings_path(self, serial: str) -> str:
        return os.path.join(self.settings_dir, "decks", f"{serial}.json")

    def get_deck_settings(self, serial: str) -> dict:
        return load_json(self.get_deck_settings_path(serial))

    def save_deck_settings(self, serial: str, settings: dict):
        save_json(self.get_deck_settings_path(serial), settings)

    def get_deck_brightness(self, serial: str) -> int:
        settings = self.get_deck_settings(serial)
        return settings.get("brightness", {}).get("value", 75)

    def set_deck_brightness(self, serial: str, value: int):
        settings = self.get_deck_settings(serial)
        settings.setdefault("brightness", {})["value"] = max(0, min(100, value))
        self.save_deck_settings(serial, settings)

    def get_deck_screensaver(self, serial: str) -> dict:
        settings = self.get_deck_settings(serial)
        return settings.get("screensaver", {})

    def set_deck_screensaver(self, serial: str, **kwargs):
        """Update screensaver settings. Only provided kwargs are updated."""
        settings = self.get_deck_settings(serial)
        ss = settings.setdefault("screensaver", {})
        for k, v in kwargs.items():
            if v is not None:
                ss[k] = v
        self.save_deck_settings(serial, settings)

    # --- Page assignment settings ---

    def get_page_settings(self) -> dict:
        return load_json(self.page_settings_path)

    def save_page_settings(self, settings: dict):
        save_json(self.page_settings_path, settings)

    def get_default_page(self, serial: str) -> Optional[str]:
        settings = self.get_page_settings()
        return settings.get("default-pages", {}).get(serial)

    def set_default_page(self, serial: str, page_path: str):
        settings = self.get_page_settings()
        settings.setdefault("default-pages", {})[serial] = page_path
        self.save_page_settings(settings)

    def list_deck_serials_with_defaults(self) -> dict:
        """Return {serial: page_path} for all decks with default page assignments."""
        settings = self.get_page_settings()
        return dict(settings.get("default-pages", {}))

    # --- Known deck serials (from settings/decks/) ---

    def list_known_serials(self) -> list:
        """List all serials that have settings files."""
        decks_dir = os.path.join(self.settings_dir, "decks")
        if not os.path.isdir(decks_dir):
            return []
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(decks_dir)
            if f.endswith(".json")
        ]

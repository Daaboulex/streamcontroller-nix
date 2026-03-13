"""Configuration and data path management for StreamController CLI."""

import os
import json


DEFAULT_DATA_PATH = os.path.expanduser(
    "~/.var/app/com.core447.StreamController/data"
)
STATIC_SETTINGS_PATH = os.path.expanduser(
    "~/.var/app/com.core447.StreamController/static/settings.json"
)

# Known Stream Deck models and their key layouts (cols x rows)
DECK_MODELS = {
    "Stream Deck Mini": {"cols": 3, "rows": 2, "keys": 6},
    "Stream Deck Mini MK.2": {"cols": 3, "rows": 2, "keys": 6},
    "Stream Deck": {"cols": 5, "rows": 3, "keys": 15},
    "Stream Deck MK.2": {"cols": 5, "rows": 3, "keys": 15},
    "Stream Deck XL": {"cols": 8, "rows": 4, "keys": 32},
    "Stream Deck XL V2": {"cols": 8, "rows": 4, "keys": 32},
    "Stream Deck +": {"cols": 4, "rows": 2, "keys": 8, "dials": 4, "touchscreen": True},
    "Stream Deck Pedal": {"cols": 3, "rows": 1, "keys": 3},
    "Stream Deck Neo": {"cols": 4, "rows": 2, "keys": 8},
}


def resolve_data_path(override: str = None) -> str:
    """Resolve the StreamController data path.

    Priority:
    1. Explicit override from --data-path CLI argument
    2. Static settings file
    3. Default path
    """
    if override:
        return os.path.expanduser(override)

    if os.path.exists(STATIC_SETTINGS_PATH):
        try:
            with open(STATIC_SETTINGS_PATH) as f:
                settings = json.load(f)
                if "data-path" in settings:
                    return settings["data-path"]
        except (json.JSONDecodeError, IOError):
            pass

    return DEFAULT_DATA_PATH


def ensure_data_dirs(data_path: str):
    """Create required data directories if they don't exist."""
    dirs = [
        data_path,
        os.path.join(data_path, "pages"),
        os.path.join(data_path, "pages", "backups"),
        os.path.join(data_path, "settings"),
        os.path.join(data_path, "settings", "decks"),
        os.path.join(data_path, "plugins"),
        os.path.join(data_path, "cache"),
        os.path.join(data_path, "logs"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

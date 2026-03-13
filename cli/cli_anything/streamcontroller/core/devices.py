"""Device management — list known devices and their configurations."""

import os
from typing import Optional

from cli_anything.streamcontroller.core.settings import SettingsManager, load_json
from cli_anything.streamcontroller.core.config import DECK_MODELS


class DeviceManager:
    """Manages Stream Deck device information (from settings, not live USB)."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.settings = SettingsManager(data_path)

    def list_known_devices(self) -> list:
        """List all devices that have settings files (previously connected)."""
        devices = []
        serials = self.settings.list_known_serials()
        defaults = self.settings.list_deck_serials_with_defaults()

        for serial in serials:
            deck_settings = self.settings.get_deck_settings(serial)
            brightness = deck_settings.get("brightness", {}).get("value", 75)
            screensaver = deck_settings.get("screensaver", {})
            default_page = defaults.get(serial)

            devices.append({
                "serial": serial,
                "brightness": brightness,
                "default_page": default_page,
                "screensaver_enabled": screensaver.get("enable", False),
                "screensaver_delay": screensaver.get("time-delay", 5),
            })

        # Also include serials that have default pages but no settings file
        for serial in defaults:
            if serial not in serials:
                devices.append({
                    "serial": serial,
                    "brightness": 75,
                    "default_page": defaults[serial],
                    "screensaver_enabled": False,
                    "screensaver_delay": 5,
                })

        return devices

    def get_device_info(self, serial: str) -> Optional[dict]:
        """Get detailed information about a known device."""
        deck_settings = self.settings.get_deck_settings(serial)
        if not deck_settings and serial not in self.settings.list_known_serials():
            return None

        defaults = self.settings.list_deck_serials_with_defaults()
        default_page = defaults.get(serial)

        return {
            "serial": serial,
            "brightness": deck_settings.get("brightness", {}).get("value", 75),
            "default_page": default_page,
            "screensaver": deck_settings.get("screensaver", {}),
            "settings": deck_settings,
        }

    @staticmethod
    def list_supported_models() -> list:
        """List all supported Stream Deck models."""
        return [
            {"model": name, **info}
            for name, info in DECK_MODELS.items()
        ]

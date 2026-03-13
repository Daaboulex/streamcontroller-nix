"""Plugin management — list, inspect, and manage installed plugins."""

import json
import os
from typing import Optional

from cli_anything.streamcontroller.core.settings import load_json


class PluginManager:
    """Manages StreamController plugins (read-only inspection of installed plugins)."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.plugin_dir = os.environ.get(
            "PLUGIN_DIR",
            os.path.join(data_path, "plugins")
        )

    def list_plugins(self) -> list:
        """List all installed plugins with basic info."""
        if not os.path.isdir(self.plugin_dir):
            return []

        plugins = []
        for folder in sorted(os.listdir(self.plugin_dir)):
            folder_path = os.path.join(self.plugin_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            manifest = self._load_manifest(folder_path)
            plugins.append({
                "id": manifest.get("id", folder),
                "name": manifest.get("name", folder),
                "version": manifest.get("version", "unknown"),
                "author": manifest.get("author", "unknown"),
                "folder": folder,
                "path": folder_path,
            })

        return plugins

    def get_plugin_info(self, plugin_id: str) -> Optional[dict]:
        """Get detailed information about a plugin."""
        if not os.path.isdir(self.plugin_dir):
            return None

        for folder in os.listdir(self.plugin_dir):
            folder_path = os.path.join(self.plugin_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            manifest = self._load_manifest(folder_path)
            pid = manifest.get("id", folder)

            if pid == plugin_id or folder == plugin_id:
                actions = self._get_plugin_actions(folder_path, manifest)
                return {
                    "id": pid,
                    "name": manifest.get("name", folder),
                    "version": manifest.get("version", "unknown"),
                    "author": manifest.get("author", "unknown"),
                    "description": manifest.get("description", ""),
                    "url": manifest.get("url", ""),
                    "folder": folder,
                    "path": folder_path,
                    "actions": actions,
                    "app_version": manifest.get("app-version", ""),
                    "minimum_app_version": manifest.get("minimum-app-version", ""),
                }

        return None

    def search_plugins(self, query: str) -> list:
        """Search installed plugins by name or ID."""
        query_lower = query.lower()
        results = []
        for plugin in self.list_plugins():
            if (query_lower in plugin["name"].lower() or
                    query_lower in plugin["id"].lower()):
                results.append(plugin)
        return results

    def _load_manifest(self, plugin_path: str) -> dict:
        """Load plugin manifest.json."""
        manifest_path = os.path.join(plugin_path, "manifest.json")
        return load_json(manifest_path)

    def _get_plugin_actions(self, plugin_path: str, manifest: dict) -> list:
        """Extract action information from a plugin."""
        actions = []
        for action_id, action_data in manifest.get("actions", {}).items():
            actions.append({
                "id": action_id,
                "name": action_data.get("name", action_id),
                "description": action_data.get("description", ""),
            })
        return actions

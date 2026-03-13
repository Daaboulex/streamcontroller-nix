"""Page management — create, list, delete, rename, import/export pages."""

import json
import os
import shutil
import zipfile
import datetime
from typing import Optional

from cli_anything.streamcontroller.core.settings import load_json, save_json


class PageManager:
    """Manages StreamController page files."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.pages_dir = os.path.join(data_path, "pages")
        self.backups_dir = os.path.join(self.pages_dir, "backups")
        self.page_settings_path = os.path.join(data_path, "settings", "pages.json")

    # --- List / Get ---

    def list_pages(self) -> list:
        """Return list of page info dicts sorted by name."""
        os.makedirs(self.pages_dir, exist_ok=True)
        pages = []
        for f in sorted(os.listdir(self.pages_dir)):
            if not f.endswith(".json"):
                continue
            path = os.path.join(self.pages_dir, f)
            name = os.path.splitext(f)[0]
            data = load_json(path)
            n_keys = len(data.get("keys", {}))
            n_dials = len(data.get("dials", {}))
            n_touchscreens = len(data.get("touchscreens", {}))
            pages.append({
                "name": name,
                "path": path,
                "keys": n_keys,
                "dials": n_dials,
                "touchscreens": n_touchscreens,
            })
        return pages

    def get_page_path(self, name: str) -> Optional[str]:
        """Resolve a page name to its file path. Returns None if not found."""
        if os.path.isfile(name):
            return name
        path = os.path.join(self.pages_dir, f"{name}.json")
        if os.path.isfile(path):
            return path
        # Case-insensitive fallback
        target = name.lower()
        for f in os.listdir(self.pages_dir):
            if not f.endswith(".json"):
                continue
            if os.path.splitext(f)[0].lower() == target:
                return os.path.join(self.pages_dir, f)
        return None

    def get_page_data(self, name: str) -> dict:
        """Load page data by name."""
        path = self.get_page_path(name)
        if not path:
            return {}
        return load_json(path)

    def get_page_name(self, path: str) -> str:
        """Extract page name from path."""
        return os.path.splitext(os.path.basename(path))[0]

    # --- Create / Delete / Rename ---

    def create_page(self, name: str, data: dict = None) -> str:
        """Create a new page. Returns the path."""
        os.makedirs(self.pages_dir, exist_ok=True)
        path = os.path.join(self.pages_dir, f"{name}.json")
        if os.path.exists(path):
            raise FileExistsError(f"Page '{name}' already exists")
        save_json(path, data or {})
        return path

    def delete_page(self, name: str) -> str:
        """Delete a page. Returns the deleted path."""
        path = self.get_page_path(name)
        if not path:
            raise FileNotFoundError(f"Page '{name}' not found")
        # Remove from default-pages settings
        settings = load_json(self.page_settings_path)
        defaults = settings.get("default-pages", {})
        to_remove = [s for s, p in defaults.items() if p == path]
        for serial in to_remove:
            del defaults[serial]
        if to_remove:
            settings["default-pages"] = defaults
            save_json(self.page_settings_path, settings)
        os.remove(path)
        return path

    def rename_page(self, old_name: str, new_name: str) -> str:
        """Rename a page. Returns the new path."""
        old_path = self.get_page_path(old_name)
        if not old_path:
            raise FileNotFoundError(f"Page '{old_name}' not found")
        new_path = os.path.join(self.pages_dir, f"{new_name}.json")
        if os.path.exists(new_path):
            raise FileExistsError(f"Page '{new_name}' already exists")
        shutil.copy2(old_path, new_path)
        # Update default-pages settings
        settings = load_json(self.page_settings_path)
        defaults = settings.get("default-pages", {})
        for serial, page_path in defaults.items():
            if page_path == old_path:
                defaults[serial] = new_path
        settings["default-pages"] = defaults
        save_json(self.page_settings_path, settings)
        os.remove(old_path)
        return new_path

    def duplicate_page(self, name: str, new_name: str = None) -> str:
        """Duplicate a page. Returns the new path."""
        src_path = self.get_page_path(name)
        if not src_path:
            raise FileNotFoundError(f"Page '{name}' not found")
        if not new_name:
            new_name = f"{self.get_page_name(src_path)}_copy"
        new_path = os.path.join(self.pages_dir, f"{new_name}.json")
        if os.path.exists(new_path):
            raise FileExistsError(f"Page '{new_name}' already exists")
        shutil.copy2(src_path, new_path)
        return new_path

    # --- Import / Export ---

    def export_page(self, name: str, output_path: str) -> str:
        """Export a page to a JSON file. Returns the output path."""
        page_path = self.get_page_path(name)
        if not page_path:
            raise FileNotFoundError(f"Page '{name}' not found")
        output_path = os.path.expanduser(output_path)
        if os.path.isdir(output_path):
            page_name = self.get_page_name(page_path)
            output_path = os.path.join(output_path, f"{page_name}.json")
        shutil.copy2(page_path, output_path)
        return output_path

    def import_page(self, input_path: str, name: str = None) -> str:
        """Import a page from a JSON file. Returns the new path."""
        input_path = os.path.expanduser(input_path)
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"File '{input_path}' not found")
        # Validate it's valid JSON
        data = load_json(input_path)
        if not isinstance(data, dict):
            raise ValueError(f"File '{input_path}' is not valid page JSON")
        if not name:
            name = os.path.splitext(os.path.basename(input_path))[0]
        os.makedirs(self.pages_dir, exist_ok=True)
        dest_path = os.path.join(self.pages_dir, f"{name}.json")
        if os.path.exists(dest_path):
            raise FileExistsError(f"Page '{name}' already exists")
        shutil.copy2(input_path, dest_path)
        return dest_path

    # --- Page inspection ---

    def inspect_page(self, name: str) -> dict:
        """Get detailed information about a page."""
        path = self.get_page_path(name)
        if not path:
            raise FileNotFoundError(f"Page '{name}' not found")
        data = load_json(path)
        page_name = self.get_page_name(path)

        keys_info = []
        for coord, key_data in data.get("keys", {}).items():
            states = key_data.get("states", {})
            state_details = []
            for state_id, state_data in states.items():
                labels = state_data.get("labels", {})
                media = state_data.get("media", {})
                actions = state_data.get("actions", [])
                label_texts = {}
                for pos in ["top", "center", "bottom"]:
                    text = labels.get(pos, {}).get("text", "")
                    if text:
                        label_texts[pos] = text
                state_details.append({
                    "state": int(state_id),
                    "image": media.get("path"),
                    "labels": label_texts,
                    "actions": [a.get("id", "unknown") for a in actions] if isinstance(actions, list) else [],
                })
            keys_info.append({
                "coordinate": coord,
                "states": state_details,
            })

        settings = data.get("settings", {})
        return {
            "name": page_name,
            "path": path,
            "keys": keys_info,
            "n_keys": len(data.get("keys", {})),
            "n_dials": len(data.get("dials", {})),
            "n_touchscreens": len(data.get("touchscreens", {})),
            "settings": {
                "brightness": settings.get("brightness", {}),
                "screensaver": settings.get("screensaver", {}),
                "background": settings.get("background", {}),
                "auto_change": settings.get("auto-change", {}),
            },
        }

    # --- Backup ---

    def create_backup(self) -> str:
        """Create a ZIP backup of all pages. Returns the backup path."""
        os.makedirs(self.backups_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        backup_path = os.path.join(self.backups_dir, f"backup_{timestamp}.zip")
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in os.listdir(self.pages_dir):
                if not f.endswith(".json"):
                    continue
                zf.write(os.path.join(self.pages_dir, f), arcname=f)
        return backup_path

    def list_backups(self) -> list:
        """List available backups."""
        if not os.path.isdir(self.backups_dir):
            return []
        backups = []
        for f in sorted(os.listdir(self.backups_dir), reverse=True):
            if not f.endswith(".zip"):
                continue
            path = os.path.join(self.backups_dir, f)
            size = os.path.getsize(path)
            # Extract timestamp from filename
            ts = f.replace("backup_", "").replace(".zip", "")
            backups.append({
                "filename": f,
                "path": path,
                "timestamp": ts,
                "size_bytes": size,
            })
        return backups

    def restore_backup(self, backup_name: str) -> int:
        """Restore pages from a backup. Returns number of pages restored."""
        backup_path = os.path.join(self.backups_dir, backup_name)
        if not os.path.isfile(backup_path):
            # Try with .zip extension
            backup_path = os.path.join(self.backups_dir, f"{backup_name}.zip")
        if not os.path.isfile(backup_path):
            raise FileNotFoundError(f"Backup '{backup_name}' not found")
        count = 0
        with zipfile.ZipFile(backup_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".json"):
                    zf.extract(name, self.pages_dir)
                    count += 1
        return count

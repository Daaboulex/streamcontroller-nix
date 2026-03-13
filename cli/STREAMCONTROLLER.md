# StreamController CLI Harness — Standard Operating Procedure

## Software Overview

StreamController is a Python GTK4 application for controlling Elgato Stream Deck devices on Linux.
It manages pages, buttons (keys/dials/touchscreens), plugins, and device settings through a
file-based JSON configuration model with optional D-Bus IPC for live control.

## Architecture

### Data Model
- **Data directory**: `~/.var/app/com.core447.StreamController/data/` (configurable)
- **Pages**: JSON files in `{DATA_PATH}/pages/` — each page defines keys, dials, touchscreens with states
- **Settings**: `{DATA_PATH}/settings/settings.json` — app-level settings
- **Deck settings**: `{DATA_PATH}/settings/decks/{serial}.json` — per-device brightness, screensaver, etc.
- **Page settings**: `{DATA_PATH}/settings/pages.json` — default page assignments per device
- **Plugins**: `{DATA_PATH}/plugins/` — installed plugin directories
- **Backups**: `{DATA_PATH}/pages/backups/` — timestamped ZIP backups

### Page JSON Structure
```json
{
  "keys": {
    "0x0": {
      "states": {
        "0": {
          "media": {"path": "/path/to/image.png", ...},
          "labels": {"top": {...}, "center": {...}, "bottom": {...}},
          "actions": [{"id": "plugin_id::ActionName", "settings": {...}}]
        }
      }
    }
  },
  "dials": {...},
  "touchscreens": {...},
  "settings": {
    "brightness": {"overwrite": false, "value": 75},
    "screensaver": {"enable": false, "time-delay": 5, ...},
    "background": {"show": false, "media-path": "", ...},
    "auto-change": {"enable": false, "wm-class": "", ...}
  }
}
```

### Key Coordinate System
- Keys use `{col}x{row}` format (e.g., "0x0" = top-left)
- Stream Deck Mini: 2x3, Original: 5x3, XL: 8x4, MK2: 5x3, Plus: 4x2 + 4 dials + touchscreen

## CLI Design Principles

1. **Offline-first**: All operations work directly on JSON files — no running StreamController needed
2. **JSON output**: Every command supports `--json` for machine-readable output
3. **REPL mode**: Interactive shell for multi-step workflows
4. **Non-destructive**: Backup pages before modifications
5. **Device-aware**: Commands that target devices use serial numbers

## Command Groups

| Group | Domain |
|-------|--------|
| `device` | List/inspect connected devices |
| `page` | Create/list/delete/rename/import/export pages |
| `button` | Set images, labels, actions on keys |
| `plugin` | List/inspect installed plugins |
| `settings` | View/modify app and deck settings |
| `backup` | Create/restore/list page backups |

## Error Handling

- Missing data directory: create with defaults
- Corrupt JSON: report error, suggest backup restore
- Missing device: list available devices
- Invalid coordinates: show valid range for device type

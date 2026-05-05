# streamcontroller-nix

<!-- BEGIN generated:badges -->
[![NixOS unstable](https://img.shields.io/badge/NixOS-unstable-78C0E8?logo=nixos&logoColor=white)](https://nixos.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
<!-- END generated:badges -->

Nix flake for [StreamController](https://github.com/StreamController/StreamController) — Elgato Stream Deck control application for Linux with plugin ecosystem.

<!-- BEGIN generated:upstream -->
## Upstream

| | |
|---|---|
| **Project** | [StreamController/StreamController](https://github.com/StreamController/StreamController) |
| **License** | GPL-3.0 |
| **Tracked** | GitHub releases |
<!-- END generated:upstream -->

## Components

| Component | Type | Description |
|---|---|---|
| `streamcontroller` | package | StreamController app (de-Flatpaked native Linux build via `patches/native-linux.patch`) |
| `streamcontroller-cli` | package | Offline CLI (Click + Python) for page/button/device/plugin management |
| `nixosModules.default` | NixOS module | `programs.streamcontroller` — package install + udev rules + optional XDG autostart |
| `homeManagerModules.default` | HM module | Declarative `programs.streamcontroller.pages.*` config — emits page JSON, deploys assets, maps device serials to default pages |
| `export-config.sh` | shell script | Reads existing page JSONs and emits a ready-to-paste `programs.streamcontroller` Nix attrset |

## What it does

Packages StreamController (de-Flatpaked for native Linux) with a NixOS module for system-level setup and a Home Manager module for declarative page/button configuration. Includes a CLI tool for offline management and an export script for capturing existing settings as Nix.

The NixOS module handles package installation, udev rules for USB device access, and optional XDG autostart. The Home Manager module generates page JSON files from Nix attrsets, deploys custom assets, and maps devices to default pages.

### Supported devices

All Elgato Stream Deck models are supported:

| Model | Keys | Layout |
|---|---|---|
| Stream Deck Mini | 6 | 3x2 |
| Stream Deck Mini MK.2 | 6 | 3x2 |
| Stream Deck (Original) | 15 | 5x3 |
| Stream Deck MK.2 | 15 | 5x3 |
| Stream Deck XL | 32 | 8x4 |
| Stream Deck XL V2 | 32 | 8x4 |
| Stream Deck + (Plus) | 8 keys + 4 dials + touchscreen | 4x2 |
| Stream Deck Pedal | 3 | 3x1 |
| Stream Deck Neo | 8 + 2 touch buttons | 4x2 |

### Key coordinate system

Buttons are addressed as `COLxROW` (zero-indexed, top-left origin). For a 5x3 Stream Deck:

```
0x0  1x0  2x0  3x0  4x0
0x1  1x1  2x1  3x1  4x1
0x2  1x2  2x2  3x2  4x2
```

<!-- BEGIN generated:installation -->
## Installation

Add as a flake input:

```nix
{
  inputs.streamcontroller = {
    url = "github:Daaboulex/streamcontroller-nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

Then add the overlay:

```nix
nixpkgs.overlays = [ inputs.streamcontroller.overlays.default ];
```

Import the NixOS module:

```nix
imports = [ inputs.streamcontroller.nixosModules.default ];
```

Import the Home Manager module:

```nix
home-manager.sharedModules = [ inputs.streamcontroller.homeManagerModules.default ];
```
<!-- END generated:installation -->

## Usage

Add as a flake input:

```nix
inputs.streamcontroller.url = "github:Daaboulex/streamcontroller-nix";
```

### NixOS module

```nix
imports = [ inputs.streamcontroller.nixosModules.default ];

programs.streamcontroller = {
  enable = true;
  autostart = true;  # XDG autostart entry
};
```

### Home Manager module

Import in your Home Manager config:

```nix
# In your flake, add to Home Manager sharedModules:
home-manager.sharedModules = [
  inputs.streamcontroller.homeManagerModules.default
];
```

### Example configuration

```nix
programs.streamcontroller = {
  enable = true;

  # Flatpak data directory (omit for native package default)
  # dataPath = "${config.home.homeDirectory}/.var/app/com.core447.StreamController/data";

  # Deploy custom icons to <dataPath>/assets/
  assets = {
    "goxlr-utility.png" = ./assets/goxlr-utility.png;
    "crt-icon.png" = ./assets/crt-icon.png;
  };

  # Map device serial to default page
  defaultPages."AL22K2C74512" = "Default";

  pages = {
    Default = {
      brightness.value = 100;

      keys = {
        # Battery status (mouse)
        "0x0".states."0".actions = [{
          id = "com_core447_Battery::BatteryPercentage";
          settings.device = "G502 LIGHTSPEED Wireless Gaming Mouse";
        }];

        # Run a shell command with custom icon
        "1x1".states."0" = {
          actions = [{
            id = "com_core447_OSPlugin::RunCommand";
            settings.command = "goxlr-toggle";
          }];
          media = {
            path = "${config.programs.streamcontroller.dataPath}/assets/goxlr-utility.png";
            size = 0.7;
          };
        };

        # Media controls
        "0x2".states."0".actions = [{
          id = "com_core447_MediaPlugin::Previous";
          settings = { show_label = true; show_thumbnail = true; };
        }];
        "1x2".states."0".actions = [{
          id = "com_core447_MediaPlugin::PlayPause";
          settings = { show_label = true; show_thumbnail = true; };
        }];
        "2x2".states."0".actions = [{
          id = "com_core447_MediaPlugin::Next";
          settings = { show_label = true; show_thumbnail = true; };
        }];
      };
    };

    # Second page with auto-change (activates when a window matches)
    controls = {
      brightness.value = 75;
      extraConfig.auto-change = {
        enable = true;
        wm_class = "";
        title = "";
        stay_on_page = true;
        decks = [ "AL22K2C74512" ];
      };

      keys = {
        # Labeled button with keyboard shortcut
        "0x0".states."0" = {
          label.center.text = "Toggle";
          actions = [{
            id = "com_core447_OSPlugin::Hotkey";
            settings.keys = [ [ 119 1 ] [ 119 0 ] ];  # F8 press/release
          }];
        };

        # Labeled button pair (increment/decrement)
        "0x1".states."0" = {
          label = { top.text = "Volume"; center.text = "+"; };
          actions = [{
            id = "com_core447_OSPlugin::RunCommand";
            settings.command = "volume-up";
          }];
        };
        "1x1".states."0" = {
          label = { top.text = "Volume"; center.text = "-"; };
          actions = [{
            id = "com_core447_OSPlugin::RunCommand";
            settings.command = "volume-down";
          }];
        };

        # Navigate back to Default page
        "4x0".states."0".actions = [{
          id = "com_core447_DeckPlugin::ChangePage";
          settings = {
            selected_page = "${config.programs.streamcontroller.dataPath}/pages/Default.json";
            deck_number = "AL22K2C74512";
          };
        }];
      };
    };
  };
};
```

### Action plugins

Actions are plugin-specific attrsets with an `id` field and a `settings` attrset. Common built-in plugins:

| Action ID | Description | Key settings |
|---|---|---|
| `com_core447_OSPlugin::RunCommand` | Run a shell command | `command`, `display_output`, `detached` |
| `com_core447_OSPlugin::Hotkey` | Send keyboard shortcut | `keys` (list of [keycode, state] pairs) |
| `com_core447_MediaPlugin::PlayPause` | Media play/pause | `show_label`, `show_thumbnail` |
| `com_core447_MediaPlugin::Previous` | Media previous track | `show_label`, `show_thumbnail` |
| `com_core447_MediaPlugin::Next` | Media next track | `show_label`, `show_thumbnail` |
| `com_core447_Battery::BatteryPercentage` | Show device battery | `device` (device name string) |
| `com_core447_DeckPlugin::ChangePage` | Switch Stream Deck page | `selected_page` (JSON path), `deck_number` (serial) |

Additional plugins can be installed through StreamController's plugin system. Action IDs follow the pattern `<plugin_id>::<action_name>`.

## CLI usage

The `streamcontroller-cli` tool manages Stream Deck configuration offline (reads/writes JSON files directly, no daemon required):

```bash
# Page management
streamcontroller-cli page list
streamcontroller-cli page create "My Page"
streamcontroller-cli page inspect Default
streamcontroller-cli page rename "Old Name" "New Name"
streamcontroller-cli page duplicate Default --new-name "Default Copy"
streamcontroller-cli page export Default backup.json
streamcontroller-cli page import backup.json --name "Imported"
streamcontroller-cli page delete "Old Page" --yes

# Button editing
streamcontroller-cli button list Default
streamcontroller-cli button set-label Default 0x0 --position center --text "Hello" --size 14
streamcontroller-cli button set-image Default 1x1 --path /path/to/icon.png
streamcontroller-cli button set-action Default 0x0 '{"id": "com_core447_OSPlugin::RunCommand", "settings": {"command": "echo hi"}}'
streamcontroller-cli button add-action Default 0x0 '{"id": "...", "settings": {...}}'
streamcontroller-cli button clear-label Default 0x0 --position center
streamcontroller-cli button clear-image Default 0x0
streamcontroller-cli button clear-actions Default 0x0

# Device info
streamcontroller-cli device list
streamcontroller-cli device info AL22K2C74512
streamcontroller-cli device models

# Plugin inspection
streamcontroller-cli plugin list
streamcontroller-cli plugin info com_core447_OSPlugin
streamcontroller-cli plugin search "media"

# Settings
streamcontroller-cli settings show
streamcontroller-cli settings set key.path value
streamcontroller-cli settings get key.path
streamcontroller-cli settings deck-brightness AL22K2C74512 75
streamcontroller-cli settings default-page AL22K2C74512 Default

# Backups
streamcontroller-cli backup create --comment "before changes"
streamcontroller-cli backup list
streamcontroller-cli backup restore 2024-01-15_143000

# JSON output mode (for scripting)
streamcontroller-cli --json page list
streamcontroller-cli --json device list
```

## Options reference

### NixOS module

| Option | Type | Default | Description |
|---|---|---|---|
| `programs.streamcontroller.enable` | bool | `false` | Install StreamController and udev rules |
| `programs.streamcontroller.package` | package | `streamcontroller` | Package to use |
| `programs.streamcontroller.autostart` | bool | `false` | Create XDG autostart entry |

### Home Manager module

#### Top-level options

| Option | Type | Default | Description |
|---|---|---|---|
| `enable` | bool | `false` | Enable declarative page management |
| `package` | package | `streamcontroller` | Package to use |
| `dataPath` | string | `$XDG_DATA_HOME/StreamController` | Data directory |
| `pages` | lazyAttrsOf submodule | `{}` | Page definitions |
| `defaultPages` | attrsOf string | `{}` | Device serial to default page mapping |
| `assets` | attrsOf path | `{}` | Asset files copied to `<dataPath>/assets/` |
| `extraCommands` | listOf string | `[]` | Extra shell commands to run after config |

#### Page submodule

| Option | Type | Default | Description |
|---|---|---|---|
| `keys` | lazyAttrsOf keySubmodule | `{}` | Key definitions (`COLxROW` coordinates) |
| `brightness.value` | nullOr int | `null` | Page brightness (0-100) |
| `brightness.overwrite` | bool | `false` | Whether to overwrite device brightness |
| `screensaver` | nullOr attrs | `null` | Screensaver settings |
| `extraConfig` | attrs | `{}` | Additional top-level page JSON attributes |

#### State submodule (per key state)

| Option | Type | Default | Description |
|---|---|---|---|
| `label.{top,center,bottom}.text` | nullOr str | `null` | Label text |
| `label.{top,center,bottom}.size` | nullOr int | `null` | Label font size |
| `label.{top,center,bottom}.color` | nullOr str | `null` | Label colour (RRGGBBAA hex) |
| `label.{top,center,bottom}.font-family` | nullOr str | `null` | Label font family |
| `label.{top,center,bottom}.font-weight` | nullOr int | `null` | Label font weight |
| `label.{top,center,bottom}.outline_width` | nullOr int | `null` | Label outline width (px) |
| `media.path` | nullOr str | `null` | Path to media file |
| `media.size` | nullOr (either int float) | `null` | Media size (px or scale factor) |
| `media.valign` | nullOr str | `null` | Vertical alignment |
| `background` | nullOr str | `null` | Background colour (hex RRGGBBAA) |
| `actions` | listOf attrs | `[]` | Plugin-specific action definitions |
| `image-control-action` | nullOr int | `0` | Image control action |
| `label-control-actions` | listOf int | `[0 0 0]` | Label control actions (top, center, bottom) |
| `background-control-action` | nullOr int | `0` | Background control action |

All options under `programs.streamcontroller` are prefixed accordingly (e.g., `programs.streamcontroller.pages.main.keys."0x0".states."0".label.center.text`).

### Assets

Custom icons and images can be managed via the `assets` option. Files are copied to `<dataPath>/assets/` during activation, making them accessible from both native and Flatpak environments.

```nix
programs.streamcontroller = {
  assets = {
    "my-icon.png" = ./icons/my-icon.png;
  };
  pages.main.keys."0x0".states."0".media = {
    path = "${config.programs.streamcontroller.dataPath}/assets/my-icon.png";
    size = 0.7;
  };
};
```

### JSON output structure

Pages are written to `<dataPath>/pages/<name>.json`. Default pages are written to `<dataPath>/settings/pages.json`.

```json
{
  "brightness": { "value": 100, "overwrite": false },
  "screensaver": { "enable": true, "timeout": 300 },
  "auto-change": { "enable": false },
  "keys": {
    "0x0": {
      "states": {
        "0": {
          "labels": {
            "center": { "text": "Hello", "font-size": 14, "color": "FFFFFFFF" }
          },
          "media": { "path": "/nix/store/.../icon.png", "size": 0.7 },
          "actions": [],
          "image-control-action": 0,
          "label-control-actions": [0, 0, 0],
          "background-control-action": 0
        }
      }
    }
  }
}
```

Only non-null label fields, media fields, and background are included. Entire label positions and media blocks are omitted when all fields are null.

## Exporting current settings

To generate Nix config from your current StreamController pages:

```bash
bash export-config.sh > my-streamcontroller-config.nix
# Or specify data directory:
bash export-config.sh --data-dir ~/.var/app/com.core447.StreamController/data
```

This reads all page JSONs and default page settings, then outputs valid Nix ready to paste into your `programs.streamcontroller` block. Requires `jq`.

## Repository structure

```
streamcontroller-nix/
├── flake.nix                  # Flake definition (packages, overlay, modules)
├── package.nix                # StreamController application package
├── module.nix                 # NixOS module (udev, autostart, systemPackages)
├── hm-module.nix              # Home Manager module (declarative page config)
├── export-config.sh           # Export current pages as Nix attrset
├── patches/
│   └── native-linux.patch     # De-Flatpak patch for native Linux
├── cli/
│   ├── package.nix            # CLI package definition
│   ├── setup.py               # Python setuptools config
│   └── cli_anything/
│       └── streamcontroller/
│           ├── streamcontroller_cli.py  # Click CLI entry point
│           ├── core/                    # Business logic modules
│           │   ├── config.py            # Data paths, deck models
│           │   ├── pages.py             # Page file management
│           │   ├── buttons.py           # Button editing
│           │   ├── plugins.py           # Plugin inspection
│           │   ├── devices.py           # Device info
│           │   └── settings.py          # JSON settings CRUD
│           ├── utils/
│           │   └── output.py            # JSON/human output formatting
│           └── tests/                   # 92 tests (unit + E2E)
├── README.md
└── LICENSE
```

## Development

```bash
git clone https://github.com/Daaboulex/streamcontroller-nix
cd streamcontroller-nix
nix develop                          # enter dev shell, installs pre-commit hooks
nix fmt                              # format flake + module + hm-module
nix flake check --no-build           # eval check
nix build .#streamcontroller         # build the desktop app
nix build .#streamcontroller-cli     # build the offline CLI
./result/bin/streamcontroller --help # binary verify (or run `streamcontroller-cli`)
```

CI runs the same chain daily via `.github/workflows/update.yml`; manual updates rarely needed.

<!-- BEGIN generated:options -->
<!-- END generated:options -->

## License

This packaging flake is [GPL-3.0-only](./LICENSE) licensed (matches upstream). Upstream StreamController is [GPL-3.0-only](https://github.com/StreamController/StreamController/blob/main/LICENSE).

<!-- BEGIN generated:footer -->
---

*Maintained as part of the [Daaboulex](https://github.com/Daaboulex) NixOS ecosystem.*
<!-- END generated:footer -->

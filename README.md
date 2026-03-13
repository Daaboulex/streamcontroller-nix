# streamcontroller-nix

Nix flake for [StreamController](https://github.com/StreamController/StreamController) — Elgato Stream Deck control application for Linux with plugin ecosystem.

## Features

- **Nix package** — StreamController de-Flatpaked for native Linux (GTK4/libadwaita, Pyro5 RPC, USB HID)
- **CLI tool** — offline management of pages, buttons, plugins, devices, settings, and backups
- **NixOS module** — system-level install with udev rules and optional autostart
- **Home Manager module** — declarative page definitions, button configs, and device defaults
- **Overlay** — drop-in for nixpkgs integration

## Quick start

### Flake input

```nix
{
  inputs.streamcontroller.url = "github:Daaboulex/streamcontroller-nix";
}
```

### NixOS module

```nix
{ inputs, ... }: {
  imports = [ inputs.streamcontroller.nixosModules.default ];

  programs.streamcontroller = {
    enable = true;
    autostart = true;  # XDG autostart entry
  };
}
```

### Home Manager module

```nix
{ inputs, ... }: {
  imports = [ inputs.streamcontroller.homeManagerModules.default ];

  programs.streamcontroller = {
    enable = true;

    pages.main = {
      brightness = { value = 100; overwrite = false; };
      screensaver = { enable = true; timeout = 300; };
      extraConfig.auto-change = { enable = false; };

      keys."0x0".states."0" = {
        label.center = { text = "Hello"; size = 14; color = "FFFFFFFF"; };
        media = { path = "/path/to/icon.png"; size = 0.7; };
        actions = [{ /* plugin-specific attrs */ }];
      };

      keys."1x0".states."0" = {
        label.top = { text = "Sharpen"; };
        label.center = { text = "+"; outline_width = 2; };
        background = "FF0000FF";
        image-control-action = 0;
        label-control-actions = [ 0 0 0 ];
        background-control-action = 0;
      };
    };

    defaultPages."AL12H34567" = "main";
  };
}
```

### CLI usage

```bash
# List pages
streamcontroller-cli page list

# Inspect a page
streamcontroller-cli page inspect main

# Create a backup
streamcontroller-cli backup create

# Set button label
streamcontroller-cli button set-label main 0x0 --position center --text "Hi"

# JSON output
streamcontroller-cli --json device list
```

## Packages

| Package | Description |
|---|---|
| `streamcontroller` | StreamController application (default) |
| `streamcontroller-cli` | Offline CLI for managing Stream Deck configurations |

## Outputs

| Output | Description |
|---|---|
| `packages.x86_64-linux.streamcontroller` | Main application |
| `packages.x86_64-linux.streamcontroller-cli` | CLI tool |
| `nixosModules.default` | NixOS module (`programs.streamcontroller`) |
| `homeManagerModules.default` | Home Manager module |
| `overlays.default` | Nixpkgs overlay |

## NixOS module options

| Option | Type | Default | Description |
|---|---|---|---|
| `programs.streamcontroller.enable` | bool | `false` | Install StreamController and udev rules |
| `programs.streamcontroller.package` | package | `streamcontroller` | Package to use |
| `programs.streamcontroller.autostart` | bool | `false` | Create XDG autostart entry |

## Home Manager module options

### Top-level options

| Option | Type | Default | Description |
|---|---|---|---|
| `programs.streamcontroller.enable` | bool | `false` | Enable declarative page management |
| `programs.streamcontroller.package` | package | `streamcontroller` | Package to use |
| `programs.streamcontroller.dataPath` | string | `$XDG_DATA_HOME/StreamController` | Data directory |
| `programs.streamcontroller.pages` | lazyAttrsOf submodule | `{}` | Page definitions |
| `programs.streamcontroller.defaultPages` | attrsOf string | `{}` | Device serial to default page mapping |
| `programs.streamcontroller.extraCommands` | listOf string | `[]` | Extra shell commands to run after config |

### Page submodule options

| Option | Type | Default | Description |
|---|---|---|---|
| `keys` | lazyAttrsOf keySubmodule | `{}` | Key definitions (`COLxROW` coordinates) |
| `brightness.value` | nullOr int | `null` | Page brightness (0-100) |
| `brightness.overwrite` | bool | `false` | Whether to overwrite device brightness |
| `screensaver` | nullOr attrs | `null` | Screensaver settings |
| `extraConfig` | attrs | `{}` | Additional top-level page JSON attributes |

### State submodule options (per key state)

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

## License

GPL-3.0-only

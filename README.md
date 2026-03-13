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
      keys."0x0".states."0" = {
        label.center = { text = "Hello"; size = 14; color = "FFFFFFFF"; };
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

| Option | Type | Default | Description |
|---|---|---|---|
| `programs.streamcontroller.enable` | bool | `false` | Enable declarative page management |
| `programs.streamcontroller.package` | package | `streamcontroller` | Package to use |
| `programs.streamcontroller.dataPath` | string | `$XDG_DATA_HOME/StreamController` | Data directory |
| `programs.streamcontroller.pages` | attrsOf submodule | `{}` | Page definitions |
| `programs.streamcontroller.defaultPages` | attrsOf string | `{}` | Device serial to default page mapping |
| `programs.streamcontroller.extraCommands` | listOf string | `[]` | Extra CLI commands to run after config |

## License

GPL-3.0-only

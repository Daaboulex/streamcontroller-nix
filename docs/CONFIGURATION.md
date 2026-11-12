# Configuration

How the Home Manager module is used: the coordinates, a full example, the
actions, assets, what the module writes and how to export what you have. The
options themselves, with types and defaults, are declared in
[hm-module.nix](../hm-module.nix) and, for the NixOS module, in
[module.nix](../module.nix).

## Key coordinates

Buttons are addressed as `COLxROW` (zero-indexed, top-left origin). For a 5x3
Stream Deck:

```text
0x0  1x0  2x0  3x0  4x0
0x1  1x1  2x1  3x1  4x1
0x2  1x2  2x2  3x2  4x2
```

The models the command-line tool knows, with the key layout of each, are
`DECK_MODELS` in
[core/config.py](../cli/cli_anything/streamcontroller/core/config.py), and
`streamcontroller-cli device models` prints them.

## Data directory

`dataPath` is where the module writes. Its default is
`$XDG_DATA_HOME/StreamController`, the directory the packaged application is
started with, so it is left out for the native package. For a StreamController
that runs as a Flatpak, point it at the Flatpak data directory:

```nix
programs.streamcontroller.dataPath =
  "${config.home.homeDirectory}/.var/app/com.core447.StreamController/data";
```

## Example configuration

Two pages for one deck. The deck's serial number is mapped to the page it
opens with, and two icons are deployed to `<dataPath>/assets/`.

The `Default` page shows the battery of a mouse on `0x0`, runs a shell command
with a custom icon on `1x1`, and has media controls on the bottom row.

```nix
programs.streamcontroller = {
  enable = true;

  assets = {
    "goxlr-utility.png" = ./assets/goxlr-utility.png;
    "crt-icon.png" = ./assets/crt-icon.png;
  };

  defaultPages."AL22K2C74512" = "Default";

  pages = {
    Default = {
      brightness.value = 100;

      keys = {
        "0x0".states."0".actions = [{
          id = "com_core447_Battery::BatteryPercentage";
          settings.device = "G502 LIGHTSPEED Wireless Gaming Mouse";
        }];

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
  };
};
```

The second page, `controls`, goes into the same `pages` set. It uses
auto-change, which activates the page when a window matches. Its `0x0` is a
labeled button with a keyboard shortcut: the two key pairs are F8 pressed and
F8 released. `0x1` and `1x1` are a labeled pair that increments and
decrements, and `4x0` navigates back to the `Default` page.

```nix
programs.streamcontroller.pages.controls = {
  brightness.value = 75;
  extraConfig.auto-change = {
    enable = true;
    wm_class = "";
    title = "";
    stay_on_page = true;
    decks = [ "AL22K2C74512" ];
  };

  keys = {
    "0x0".states."0" = {
      label.center.text = "Toggle";
      actions = [{
        id = "com_core447_OSPlugin::Hotkey";
        settings.keys = [ [ 119 1 ] [ 119 0 ] ];
      }];
    };

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

    "4x0".states."0".actions = [{
      id = "com_core447_DeckPlugin::ChangePage";
      settings = {
        selected_page = "${config.programs.streamcontroller.dataPath}/pages/Default.json";
        deck_number = "AL22K2C74512";
      };
    }];
  };
};
```

## Action plugins

Actions are plugin-specific attrsets with an `id` field and a `settings`
attrset. Common built-in plugins:

| Action ID | Description | Key settings |
|---|---|---|
| `com_core447_OSPlugin::RunCommand` | Run a shell command | `command`, `display_output`, `detached` |
| `com_core447_OSPlugin::Hotkey` | Send keyboard shortcut | `keys` (list of [keycode, state] pairs) |
| `com_core447_MediaPlugin::PlayPause` | Media play/pause | `show_label`, `show_thumbnail` |
| `com_core447_MediaPlugin::Previous` | Media previous track | `show_label`, `show_thumbnail` |
| `com_core447_MediaPlugin::Next` | Media next track | `show_label`, `show_thumbnail` |
| `com_core447_Battery::BatteryPercentage` | Show device battery | `device` (device name string) |
| `com_core447_DeckPlugin::ChangePage` | Switch Stream Deck page | `selected_page` (JSON path), `deck_number` (serial) |

Additional plugins can be installed through StreamController's plugin system.
Action IDs follow the pattern `<plugin_id>::<action_name>`.

The plugins are upstream's, not part of this repository, so nothing here
checks the setting names in the table.

## Assets

Custom icons and images can be managed via the `assets` option. Files are
copied to `<dataPath>/assets/` during activation, making them accessible from
both native and Flatpak environments.

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

## Page files from the application

A page the application itself saved can be handed over as it is:

```nix
programs.streamcontroller.pageFiles.Default = ./pages/Default.json;
```

It lands as `pages/Default.json` next to the declarative pages, and the same
install rule applies: the file is copied again whenever it differs from what
is deployed.

## What the module writes

Pages are written to `<dataPath>/pages/<name>.json`. Default pages are written
to `<dataPath>/settings/pages.json`.

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

Only non-null label fields, media fields, and background are included. Entire
label positions and media blocks are omitted when all fields are null.

## Exporting current settings

To generate Nix config from your current StreamController pages, run
[export-config.sh](../export-config.sh):

```bash
bash export-config.sh > my-streamcontroller-config.nix
```

This reads all page JSONs and default page settings, then outputs valid Nix
ready to paste into your `programs.streamcontroller` block. Requires `jq`.

Without an argument the script looks for pages in the Flatpak data directory
first and in `$XDG_DATA_HOME/StreamController` second. `--data-dir` names the
directory instead:

```bash
bash export-config.sh --data-dir ~/.var/app/com.core447.StreamController/data
```

`--module` wraps the output as a module that can be imported as a file.

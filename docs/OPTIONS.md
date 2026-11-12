# Options

Every option the modules of this flake declare. This file is generated from the module sources: change a description there, then run `nix run .#std-write-option-reference`.

## Home Manager module

Declared in [hm-module.nix](../hm-module.nix).

### `programs.streamcontroller.enable`

Whether to enable declarative StreamController page and device configuration.

- Type: boolean
- Default: `false`

### `programs.streamcontroller.package`

The StreamController package to use.

- Type: package
- Default: `pkgs.streamcontroller`

### `programs.streamcontroller.assets`

Asset files to copy into the StreamController data directory. Keys are filenames, values are source paths. Files are placed at <dataPath>/assets/<key>.

- Type: attribute set of absolute path
- Default: `{ }`
- Example:

  ```nix
  {
    "my-icon.png" = ./icons/my-icon.png;
  }

  ```

### `programs.streamcontroller.dataPath`

StreamController data directory path.

- Type: string
- Default: `"${config.xdg.dataHome}/StreamController"`

### `programs.streamcontroller.defaultPages`

Map of device serial numbers to their default page name.

- Type: attribute set of string
- Default: `{ }`
- Example:

  ```nix
  {
    CL12345678 = "Main";
  }
  ```

### `programs.streamcontroller.extraCommands`

Additional commands to run after applying StreamController configuration.

- Type: list of string
- Default: `[ ]`

### `programs.streamcontroller.pageFiles`

Page files in StreamController's own JSON, installed as pages/<name>.json beside the declarative pages. Keys are page names.

- Type: attribute set of absolute path
- Default: `{ }`

### `programs.streamcontroller.pages`

Declarative page definitions. Keys are page names.

- Type: lazy attribute set of (submodule)
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.brightness`

Page brightness settings

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.brightness.overwrite`

Whether to overwrite device brightness

- Type: boolean
- Default: `false`

### `programs.streamcontroller.pages.<name>.brightness.value`

Brightness value (0-100)

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.extraConfig`

Additional page JSON attributes merged at the top level (e.g., auto-change)

- Type: attribute set
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys`

Key definitions. Keys are coordinates as 'COLxROW' (e.g., '0x0', '1x2').

- Type: lazy attribute set of (submodule)
- Default: `{ }`
- Example:

  ```nix
  {
    "0x0" = {
      states = {
        "0" = {
          label = {
            center = {
              text = "Play";
            };
          };
          media = {
            path = "/path/to/play.png";
          };
        };
      };
    };
  }
  ```

### `programs.streamcontroller.pages.<name>.keys.<name>.states`

Button states (keys are state IDs as strings: "0", "1", etc.)

- Type: lazy attribute set of (submodule)
- Default:

  ```nix
  {
    "0" = { };
  }
  ```

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.actions`

List of action definitions (plugin-specific attrs)

- Type: list of (attribute set)
- Default: `[ ]`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.background`

Background colour as hex RRGGBBAA

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.background-control-action`

Background control action (0 = default)

- Type: null or signed integer
- Default: `0`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.image-control-action`

Image control action (0 = default)

- Type: null or signed integer
- Default: `0`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label`

Label configuration for each position (top, center, bottom)

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom`

Bottom label configuration

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.color`

Label colour as RRGGBBAA hex string

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.font-family`

Label font family

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.font-weight`

Label font weight

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.outline_width`

Label outline width in pixels

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.size`

Label font size

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.bottom.text`

Label text

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center`

Center label configuration

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.color`

Label colour as RRGGBBAA hex string

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.font-family`

Label font family

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.font-weight`

Label font weight

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.outline_width`

Label outline width in pixels

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.size`

Label font size

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.center.text`

Label text

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top`

Top label configuration

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.color`

Label colour as RRGGBBAA hex string

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.font-family`

Label font family

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.font-weight`

Label font weight

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.outline_width`

Label outline width in pixels

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.size`

Label font size

- Type: null or signed integer
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label.top.text`

Label text

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.label-control-actions`

Label control actions for top, center, bottom

- Type: list of signed integer
- Default:

  ```nix
  [
    0
    0
    0
  ]
  ```

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.media`

Media (image/icon) configuration

- Type: submodule
- Default: `{ }`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.media.path`

Path to media file (image/icon)

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.media.size`

Media size (integer pixels or float scale factor)

- Type: null or signed integer or floating point number
- Default: `null`

### `programs.streamcontroller.pages.<name>.keys.<name>.states.<name>.media.valign`

Vertical alignment of media

- Type: null or string
- Default: `null`

### `programs.streamcontroller.pages.<name>.screensaver`

Screensaver settings

- Type: null or (attribute set)
- Default: `null`

## NixOS module

Declared in [module.nix](../module.nix).

### `programs.streamcontroller.enable`

Whether to enable StreamController — Elgato Stream Deck control application.

- Type: boolean
- Default: `false`

### `programs.streamcontroller.package`

The StreamController package to use.

- Type: package
- Default: `pkgs.streamcontroller`

### `programs.streamcontroller.autostart`

Whether to autostart StreamController at login.

- Type: boolean
- Default: `false`

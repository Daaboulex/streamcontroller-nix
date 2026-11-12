# The command-line tool

The `streamcontroller-cli` tool manages Stream Deck configuration offline: it
reads and writes the JSON files directly, no daemon required.

## Pages

```bash
streamcontroller-cli page list
streamcontroller-cli page create "My Page"
streamcontroller-cli page inspect Default
streamcontroller-cli page rename "Old Name" "New Name"
streamcontroller-cli page duplicate Default --new-name "Default Copy"
streamcontroller-cli page export Default backup.json
streamcontroller-cli page import backup.json --name "Imported"
streamcontroller-cli page delete "Old Page" --yes
```

## Buttons

```bash
streamcontroller-cli button list Default
streamcontroller-cli button inspect Default 0x0
streamcontroller-cli button set-label Default 0x0 "Hello" --position center --size 14
streamcontroller-cli button set-image Default 1x1 /path/to/icon.png
streamcontroller-cli button set-action Default 0x0 com_core447_OSPlugin::RunCommand --settings '{"command": "echo hi"}'
streamcontroller-cli button add-action Default 0x0 com_core447_OSPlugin::RunCommand --settings '{"command": "echo again"}'
streamcontroller-cli button clear-label Default 0x0 --position center
streamcontroller-cli button clear-image Default 0x0
streamcontroller-cli button clear-actions Default 0x0
```

`set-action` replaces the actions of a button and `add-action` appends one.
A label goes to `top`, `center` or `bottom`, and to `bottom` when no
`--position` is given.

## Devices

```bash
streamcontroller-cli device list
streamcontroller-cli device info AL22K2C74512
streamcontroller-cli device models
```

## Plugins

```bash
streamcontroller-cli plugin list
streamcontroller-cli plugin info com_core447_OSPlugin
streamcontroller-cli plugin search "media"
```

These inspect the plugins that are installed. They do not install any.

## Settings

```bash
streamcontroller-cli settings show
streamcontroller-cli settings set key.path value
streamcontroller-cli settings get key.path
streamcontroller-cli settings brightness AL22K2C74512 75
streamcontroller-cli settings default-page AL22K2C74512 Default
```

A key path is separated by dots. Brightness is a number from 0 to 100.

## Backups

```bash
streamcontroller-cli backup create
streamcontroller-cli backup list
streamcontroller-cli backup restore backup_20240115T143000
```

A backup is a ZIP file of all pages, kept under `pages/backups/` in the data
directory.

## JSON output

`--json` before the command prints JSON, for scripting:

```bash
streamcontroller-cli --json page list
streamcontroller-cli --json device list
```

## Which data directory it works on

`--data-path` before the command names the directory. Without it the tool
takes the `data-path` from
`~/.var/app/com.core447.StreamController/static/settings.json` when that file
exists. Otherwise it uses `$XDG_DATA_HOME/StreamController`, or the Flatpak
data directory when it runs inside a Flatpak.

## Interactive session

`streamcontroller-cli repl` starts a prompt that takes the same commands
without the program name. `quit` leaves it.

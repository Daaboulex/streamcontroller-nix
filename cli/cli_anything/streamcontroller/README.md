# StreamController CLI

A command-line interface for managing Elgato Stream Deck configurations offline, without needing the StreamController GUI running.

## Installation

```bash
cd agent-harness
pip install -e .
```

After installation, the CLI is available as `cli-anything-streamcontroller`.

## Usage

```bash
# Show help
cli-anything-streamcontroller --help

# Use JSON output mode (for scripting/agents)
cli-anything-streamcontroller --json page list

# Override data directory
cli-anything-streamcontroller --data-path ~/my-streamcontroller-data page list
```

## Command Groups

### Pages

```bash
# List all pages
cli-anything-streamcontroller page list

# Create a new page
cli-anything-streamcontroller page create MyPage

# Inspect a page (show all keys, settings)
cli-anything-streamcontroller page inspect MyPage

# Delete a page
cli-anything-streamcontroller page delete MyPage

# Rename a page
cli-anything-streamcontroller page rename OldName NewName

# Duplicate a page
cli-anything-streamcontroller page duplicate MyPage --new-name MyPageCopy

# Export a page to a file
cli-anything-streamcontroller page export MyPage /tmp/mypage.json

# Import a page from a file
cli-anything-streamcontroller page import /tmp/mypage.json --name ImportedPage
```

### Buttons

```bash
# List all configured buttons on a page
cli-anything-streamcontroller button list MyPage

# Inspect a specific button
cli-anything-streamcontroller button inspect MyPage 0x0

# Set a text label
cli-anything-streamcontroller button set-label MyPage 0x0 "Hello" --position bottom --font "Arial" --size 14

# Clear a label
cli-anything-streamcontroller button clear-label MyPage 0x0 --position bottom

# Set an image
cli-anything-streamcontroller button set-image MyPage 0x0 /path/to/icon.png

# Clear an image
cli-anything-streamcontroller button clear-image MyPage 0x0

# Set an action (replaces existing)
cli-anything-streamcontroller button set-action MyPage 0x0 "dev_core447_MediaPlugin::Pause"

# Add an action (appends)
cli-anything-streamcontroller button add-action MyPage 0x0 "dev_core447_OBSPlugin::SwitchScene" --settings '{"scene": "Main"}'

# Clear all actions
cli-anything-streamcontroller button clear-actions MyPage 0x0
```

### Plugins

```bash
# List installed plugins
cli-anything-streamcontroller plugin list

# Get plugin details
cli-anything-streamcontroller plugin info dev_core447_MediaPlugin

# Search plugins
cli-anything-streamcontroller plugin search media
```

### Devices

```bash
# List known devices
cli-anything-streamcontroller device list

# Get device details
cli-anything-streamcontroller device info CL123456789

# List supported models
cli-anything-streamcontroller device models
```

### Settings

```bash
# Show all app settings
cli-anything-streamcontroller settings show

# Get a specific setting
cli-anything-streamcontroller settings get store.auto-update

# Set a setting
cli-anything-streamcontroller settings set store.auto-update false

# Set device brightness
cli-anything-streamcontroller settings brightness CL123456789 75

# Set default page for a device
cli-anything-streamcontroller settings default-page CL123456789 MyPage
```

### Backups

```bash
# Create a backup of all pages
cli-anything-streamcontroller backup create

# List backups
cli-anything-streamcontroller backup list

# Restore from a backup
cli-anything-streamcontroller backup restore backup_20240101T120000.zip
```

### REPL Mode

```bash
# Start interactive session
cli-anything-streamcontroller repl

streamcontroller> page list
streamcontroller> button set-label MyPage 0x0 "Test"
streamcontroller> quit
```

## JSON Output

All commands support `--json` for machine-readable output:

```bash
cli-anything-streamcontroller --json page list
cli-anything-streamcontroller --json button inspect MyPage 0x0
cli-anything-streamcontroller --json settings show
```

## Data Path Resolution

The CLI resolves the data directory in this order:
1. `--data-path` CLI argument
2. Static settings file (`~/.var/app/com.core447.StreamController/static/settings.json`)
3. Default: `~/.var/app/com.core447.StreamController/data/`

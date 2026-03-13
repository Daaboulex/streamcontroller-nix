"""StreamController CLI — manage Stream Deck pages, buttons, plugins, and settings."""

import json
import os
import sys

import click

from cli_anything.streamcontroller.core.config import resolve_data_path, ensure_data_dirs
from cli_anything.streamcontroller.core.pages import PageManager
from cli_anything.streamcontroller.core.buttons import ButtonManager
from cli_anything.streamcontroller.core.plugins import PluginManager
from cli_anything.streamcontroller.core.devices import DeviceManager
from cli_anything.streamcontroller.core.settings import SettingsManager
from cli_anything.streamcontroller.utils.output import OutputFormatter


# ---------- Context ----------

class CLIContext:
    def __init__(self, data_path: str, json_mode: bool):
        self.data_path = data_path
        self.json_mode = json_mode
        self.out = OutputFormatter(json_mode)
        ensure_data_dirs(data_path)
        self.pages = PageManager(data_path)
        self.buttons = ButtonManager(data_path)
        self.plugins = PluginManager(data_path)
        self.devices = DeviceManager(data_path)
        self.settings = SettingsManager(data_path)


pass_ctx = click.make_pass_decorator(CLIContext)


# ---------- Root group ----------

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format.")
@click.option("--data-path", default=None, help="Override StreamController data directory.")
@click.pass_context
def cli(ctx, json_mode, data_path):
    """StreamController CLI — manage Stream Deck configurations offline."""
    data_path = resolve_data_path(data_path)
    ctx.ensure_object(dict)
    ctx.obj = CLIContext(data_path, json_mode)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ============================================================
# PAGE commands
# ============================================================

@cli.group()
def page():
    """Manage Stream Deck pages."""
    pass


@page.command("list")
@pass_ctx
def page_list(ctx):
    """List all pages."""
    pages = ctx.pages.list_pages()
    if ctx.json_mode:
        ctx.out.print_result(pages)
    else:
        if not pages:
            click.echo("No pages found.")
            return
        headers = ["Name", "Keys", "Dials", "Touchscreens"]
        rows = [[p["name"], p["keys"], p["dials"], p["touchscreens"]] for p in pages]
        ctx.out.print_table(headers, rows)


@page.command("inspect")
@click.argument("name")
@pass_ctx
def page_inspect(ctx, name):
    """Show detailed information about a page."""
    try:
        info = ctx.pages.inspect_page(name)
        ctx.out.print_result(info)
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("create")
@click.argument("name")
@pass_ctx
def page_create(ctx, name):
    """Create a new empty page."""
    try:
        path = ctx.pages.create_page(name)
        ctx.out.print_success(f"Created page '{name}' at {path}", {"path": path})
    except FileExistsError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("delete")
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@pass_ctx
def page_delete(ctx, name, yes):
    """Delete a page."""
    if not yes and not ctx.json_mode:
        click.confirm(f"Delete page '{name}'?", abort=True)
    try:
        path = ctx.pages.delete_page(name)
        ctx.out.print_success(f"Deleted page '{name}'", {"path": path})
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("rename")
@click.argument("old_name")
@click.argument("new_name")
@pass_ctx
def page_rename(ctx, old_name, new_name):
    """Rename a page."""
    try:
        path = ctx.pages.rename_page(old_name, new_name)
        ctx.out.print_success(f"Renamed '{old_name}' to '{new_name}'", {"path": path})
    except (FileNotFoundError, FileExistsError) as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("duplicate")
@click.argument("name")
@click.option("--new-name", default=None, help="Name for the copy.")
@pass_ctx
def page_duplicate(ctx, name, new_name):
    """Duplicate a page."""
    try:
        path = ctx.pages.duplicate_page(name, new_name)
        ctx.out.print_success(f"Duplicated page '{name}'", {"path": path})
    except (FileNotFoundError, FileExistsError) as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("export")
@click.argument("name")
@click.argument("output_path")
@pass_ctx
def page_export(ctx, name, output_path):
    """Export a page to a file."""
    try:
        path = ctx.pages.export_page(name, output_path)
        ctx.out.print_success(f"Exported page '{name}' to {path}", {"path": path})
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@page.command("import")
@click.argument("input_path")
@click.option("--name", default=None, help="Name for the imported page.")
@pass_ctx
def page_import(ctx, input_path, name):
    """Import a page from a file."""
    try:
        path = ctx.pages.import_page(input_path, name)
        ctx.out.print_success(f"Imported page to {path}", {"path": path})
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


# ============================================================
# BUTTON commands
# ============================================================

@cli.group()
def button():
    """Manage buttons/keys on pages."""
    pass


@button.command("list")
@click.argument("page_name")
@pass_ctx
def button_list(ctx, page_name):
    """List all configured buttons on a page."""
    try:
        keys = ctx.buttons.list_keys(page_name)
        if ctx.json_mode:
            ctx.out.print_result(keys)
        else:
            if not keys:
                click.echo("No configured buttons.")
                return
            headers = ["Type", "Coord", "States", "Label", "Actions"]
            rows = []
            for k in keys:
                action_str = ", ".join(k["actions"][:2])
                if len(k["actions"]) > 2:
                    action_str += f" (+{len(k['actions']) - 2})"
                rows.append([k["type"], k["coordinate"], k["states"],
                             k["label"][:30], action_str[:40]])
            ctx.out.print_table(headers, rows)
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("inspect")
@click.argument("page_name")
@click.argument("coord")
@click.option("--state", "-s", default=0, type=int, help="State number (default: 0).")
@pass_ctx
def button_inspect(ctx, page_name, coord, state):
    """Inspect a specific button."""
    try:
        state_data = ctx.buttons.get_key_state(page_name, coord, state)
        if not state_data:
            ctx.out.print_error(f"No data at {coord} state {state}")
            sys.exit(1)
        ctx.out.print_result({
            "coordinate": coord,
            "state": state,
            "data": state_data,
        })
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("set-label")
@click.argument("page_name")
@click.argument("coord")
@click.argument("text")
@click.option("--position", "-p", default="bottom", type=click.Choice(["top", "center", "bottom"]))
@click.option("--state", "-s", default=0, type=int)
@click.option("--font", default=None, help="Font family name.")
@click.option("--size", default=None, type=int, help="Font size.")
@click.option("--color", default=None, help="Color as R,G,B,A (e.g. 255,255,255,255).")
@pass_ctx
def button_set_label(ctx, page_name, coord, text, position, state, font, size, color):
    """Set a text label on a button."""
    color_list = None
    if color:
        try:
            color_list = [int(c.strip()) for c in color.split(",")]
        except ValueError:
            ctx.out.print_error("Invalid color format. Use R,G,B,A (e.g. 255,255,255,255)")
            sys.exit(1)
    try:
        ctx.buttons.set_label(page_name, coord, position, text, state, font, size, color_list)
        ctx.out.print_success(f"Set {position} label on {coord} to '{text}'")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("clear-label")
@click.argument("page_name")
@click.argument("coord")
@click.option("--position", "-p", default="bottom", type=click.Choice(["top", "center", "bottom"]))
@click.option("--state", "-s", default=0, type=int)
@pass_ctx
def button_clear_label(ctx, page_name, coord, position, state):
    """Clear a label from a button."""
    try:
        ctx.buttons.clear_label(page_name, coord, position, state)
        ctx.out.print_success(f"Cleared {position} label on {coord}")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("set-image")
@click.argument("page_name")
@click.argument("coord")
@click.argument("image_path")
@click.option("--state", "-s", default=0, type=int)
@pass_ctx
def button_set_image(ctx, page_name, coord, image_path, state):
    """Set the image on a button."""
    try:
        ctx.buttons.set_image(page_name, coord, image_path, state)
        ctx.out.print_success(f"Set image on {coord} to '{image_path}'")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("clear-image")
@click.argument("page_name")
@click.argument("coord")
@click.option("--state", "-s", default=0, type=int)
@pass_ctx
def button_clear_image(ctx, page_name, coord, state):
    """Clear the image from a button."""
    try:
        ctx.buttons.clear_image(page_name, coord, state)
        ctx.out.print_success(f"Cleared image on {coord}")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("set-action")
@click.argument("page_name")
@click.argument("coord")
@click.argument("action_id")
@click.option("--state", "-s", default=0, type=int)
@click.option("--settings", default=None, help="JSON string of action settings.")
@pass_ctx
def button_set_action(ctx, page_name, coord, action_id, state, settings):
    """Set the action on a button (replaces existing)."""
    action_settings = None
    if settings:
        try:
            action_settings = json.loads(settings)
        except json.JSONDecodeError:
            ctx.out.print_error("Invalid JSON for --settings")
            sys.exit(1)
    try:
        ctx.buttons.set_action(page_name, coord, action_id, state, action_settings)
        ctx.out.print_success(f"Set action '{action_id}' on {coord}")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("add-action")
@click.argument("page_name")
@click.argument("coord")
@click.argument("action_id")
@click.option("--state", "-s", default=0, type=int)
@click.option("--settings", default=None, help="JSON string of action settings.")
@pass_ctx
def button_add_action(ctx, page_name, coord, action_id, state, settings):
    """Add an action to a button (appends to existing)."""
    action_settings = None
    if settings:
        try:
            action_settings = json.loads(settings)
        except json.JSONDecodeError:
            ctx.out.print_error("Invalid JSON for --settings")
            sys.exit(1)
    try:
        ctx.buttons.add_action(page_name, coord, action_id, state, action_settings)
        ctx.out.print_success(f"Added action '{action_id}' on {coord}")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


@button.command("clear-actions")
@click.argument("page_name")
@click.argument("coord")
@click.option("--state", "-s", default=0, type=int)
@pass_ctx
def button_clear_actions(ctx, page_name, coord, state):
    """Remove all actions from a button."""
    try:
        ctx.buttons.clear_actions(page_name, coord, state)
        ctx.out.print_success(f"Cleared actions on {coord}")
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


# ============================================================
# PLUGIN commands
# ============================================================

@cli.group()
def plugin():
    """Manage installed plugins."""
    pass


@plugin.command("list")
@pass_ctx
def plugin_list(ctx):
    """List all installed plugins."""
    plugins = ctx.plugins.list_plugins()
    if ctx.json_mode:
        ctx.out.print_result(plugins)
    else:
        if not plugins:
            click.echo("No plugins installed.")
            return
        headers = ["ID", "Name", "Version", "Author"]
        rows = [[p["id"], p["name"], p["version"], p["author"]] for p in plugins]
        ctx.out.print_table(headers, rows)


@plugin.command("info")
@click.argument("plugin_id")
@pass_ctx
def plugin_info(ctx, plugin_id):
    """Show detailed information about a plugin."""
    info = ctx.plugins.get_plugin_info(plugin_id)
    if not info:
        ctx.out.print_error(f"Plugin '{plugin_id}' not found")
        sys.exit(1)
    ctx.out.print_result(info)


@plugin.command("search")
@click.argument("query")
@pass_ctx
def plugin_search(ctx, query):
    """Search installed plugins by name or ID."""
    results = ctx.plugins.search_plugins(query)
    if ctx.json_mode:
        ctx.out.print_result(results)
    else:
        if not results:
            click.echo(f"No plugins matching '{query}'.")
            return
        headers = ["ID", "Name", "Version", "Author"]
        rows = [[p["id"], p["name"], p["version"], p["author"]] for p in results]
        ctx.out.print_table(headers, rows)


# ============================================================
# DEVICE commands
# ============================================================

@cli.group()
def device():
    """Manage Stream Deck devices."""
    pass


@device.command("list")
@pass_ctx
def device_list(ctx):
    """List all known devices (from settings)."""
    devices = ctx.devices.list_known_devices()
    if ctx.json_mode:
        ctx.out.print_result(devices)
    else:
        if not devices:
            click.echo("No known devices. Connect a Stream Deck and run StreamController first.")
            return
        headers = ["Serial", "Brightness", "Default Page", "Screensaver"]
        rows = []
        for d in devices:
            dp = os.path.basename(d["default_page"]) if d["default_page"] else "-"
            ss = "on" if d["screensaver_enabled"] else "off"
            rows.append([d["serial"], d["brightness"], dp, ss])
        ctx.out.print_table(headers, rows)


@device.command("info")
@click.argument("serial")
@pass_ctx
def device_info(ctx, serial):
    """Show detailed information about a device."""
    info = ctx.devices.get_device_info(serial)
    if not info:
        ctx.out.print_error(f"Device '{serial}' not found in settings")
        sys.exit(1)
    ctx.out.print_result(info)


@device.command("models")
@pass_ctx
def device_models(ctx):
    """List all supported Stream Deck models."""
    models = DeviceManager.list_supported_models()
    if ctx.json_mode:
        ctx.out.print_result(models)
    else:
        headers = ["Model", "Cols", "Rows", "Keys", "Dials", "Touch"]
        rows = []
        for m in models:
            rows.append([
                m["model"], m["cols"], m["rows"], m["keys"],
                m.get("dials", 0), "Yes" if m.get("touchscreen") else "No"
            ])
        ctx.out.print_table(headers, rows)


# ============================================================
# SETTINGS commands
# ============================================================

@cli.group()
def settings():
    """View and modify settings."""
    pass


@settings.command("show")
@pass_ctx
def settings_show(ctx):
    """Show current app settings."""
    app_settings = ctx.settings.get_app_settings()
    ctx.out.print_result(app_settings)


@settings.command("get")
@click.argument("key_path")
@pass_ctx
def settings_get(ctx, key_path):
    """Get a setting value by dot-separated key path (e.g. 'store.auto-update')."""
    keys = key_path.split(".")
    value = ctx.settings.get_app_setting(*keys)
    ctx.out.print_result({"key": key_path, "value": value})


@settings.command("set")
@click.argument("key_path")
@click.argument("value")
@pass_ctx
def settings_set(ctx, key_path, value):
    """Set a setting value by dot-separated key path."""
    # Try to parse value as JSON for booleans, numbers, etc.
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    keys = key_path.split(".")
    ctx.settings.set_app_setting(parsed, *keys)
    ctx.out.print_success(f"Set {key_path} = {parsed}")


@settings.command("brightness")
@click.argument("serial")
@click.argument("value", type=int)
@pass_ctx
def settings_brightness(ctx, serial, value):
    """Set brightness for a device (0-100)."""
    if value < 0 or value > 100:
        ctx.out.print_error("Brightness must be between 0 and 100")
        sys.exit(1)
    ctx.settings.set_deck_brightness(serial, value)
    ctx.out.print_success(f"Set brightness for {serial} to {value}")


@settings.command("default-page")
@click.argument("serial")
@click.argument("page_name")
@pass_ctx
def settings_default_page(ctx, serial, page_name):
    """Set the default page for a device."""
    page_path = ctx.pages.get_page_path(page_name)
    if not page_path:
        ctx.out.print_error(f"Page '{page_name}' not found")
        sys.exit(1)
    ctx.settings.set_default_page(serial, page_path)
    ctx.out.print_success(f"Set default page for {serial} to '{page_name}'")


# ============================================================
# BACKUP commands
# ============================================================

@cli.group()
def backup():
    """Manage page backups."""
    pass


@backup.command("create")
@pass_ctx
def backup_create(ctx):
    """Create a backup of all pages."""
    path = ctx.pages.create_backup()
    ctx.out.print_success(f"Backup created at {path}", {"path": path})


@backup.command("list")
@pass_ctx
def backup_list(ctx):
    """List available backups."""
    backups = ctx.pages.list_backups()
    if ctx.json_mode:
        ctx.out.print_result(backups)
    else:
        if not backups:
            click.echo("No backups found.")
            return
        headers = ["Filename", "Timestamp", "Size"]
        rows = []
        for b in backups:
            size_kb = b["size_bytes"] / 1024
            rows.append([b["filename"], b["timestamp"], f"{size_kb:.1f} KB"])
        ctx.out.print_table(headers, rows)


@backup.command("restore")
@click.argument("backup_name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation.")
@pass_ctx
def backup_restore(ctx, backup_name, yes):
    """Restore pages from a backup."""
    if not yes and not ctx.json_mode:
        click.confirm(f"Restore from backup '{backup_name}'? This may overwrite existing pages.", abort=True)
    try:
        count = ctx.pages.restore_backup(backup_name)
        ctx.out.print_success(f"Restored {count} pages from backup", {"count": count})
    except FileNotFoundError as e:
        ctx.out.print_error(str(e))
        sys.exit(1)


# ============================================================
# REPL mode
# ============================================================

@cli.command("repl")
@click.pass_context
def repl_cmd(click_ctx):
    """Start an interactive REPL session."""
    ctx = click_ctx.obj
    click.echo("StreamController CLI REPL. Type 'help' for commands, 'quit' to exit.")
    click.echo(f"Data path: {ctx.data_path}")
    click.echo()

    while True:
        try:
            line = input("streamcontroller> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            click.echo("Bye!")
            break
        if line == "help":
            click.echo(click_ctx.parent.get_help() if click_ctx.parent else click_ctx.get_help())
            continue

        # Parse and execute the command
        args = line.split()
        try:
            cli.main(args=args, standalone_mode=False, obj=ctx)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"Error: {e}")
        except Exception as e:
            click.echo(f"Error: {e}")


# ============================================================
# Entry point
# ============================================================

def main():
    cli()


if __name__ == "__main__":
    main()

"""End-to-end tests for StreamController CLI — tests the actual Click CLI interface."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from click.testing import CliRunner

from cli_anything.streamcontroller.streamcontroller_cli import cli


class TestCLIBase(unittest.TestCase):
    """Base class with shared setUp/tearDown for CLI tests."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.runner = CliRunner()
        self.base_args = ["--data-path", self.tmpdir]

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def invoke(self, args, **kwargs):
        return self.runner.invoke(cli, self.base_args + args, catch_exceptions=False, **kwargs)

    def invoke_json(self, args, **kwargs):
        return self.runner.invoke(cli, ["--json"] + self.base_args + args,
                                 catch_exceptions=False, **kwargs)


class TestPageCLI(TestCLIBase):
    def test_page_list_empty(self):
        result = self.invoke(["page", "list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No pages found", result.output)

    def test_page_create_and_list(self):
        result = self.invoke(["page", "create", "Main"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Created page", result.output)

        result = self.invoke(["page", "list"])
        self.assertIn("Main", result.output)

    def test_page_create_json(self):
        result = self.invoke_json(["page", "create", "Main"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data["status"], "ok")

    def test_page_list_json(self):
        self.invoke(["page", "create", "Page1"])
        self.invoke(["page", "create", "Page2"])
        result = self.invoke_json(["page", "list"])
        data = json.loads(result.output)
        self.assertEqual(len(data), 2)

    def test_page_inspect(self):
        self.invoke(["page", "create", "Detailed"])
        result = self.invoke_json(["page", "inspect", "Detailed"])
        data = json.loads(result.output)
        self.assertEqual(data["name"], "Detailed")
        self.assertEqual(data["n_keys"], 0)

    def test_page_delete(self):
        self.invoke(["page", "create", "ToDelete"])
        result = self.invoke(["page", "delete", "ToDelete", "-y"])
        self.assertEqual(result.exit_code, 0)
        result = self.invoke(["page", "list"])
        self.assertIn("No pages found", result.output)

    def test_page_rename(self):
        self.invoke(["page", "create", "Old"])
        result = self.invoke(["page", "rename", "Old", "New"])
        self.assertEqual(result.exit_code, 0)
        result = self.invoke_json(["page", "list"])
        names = [p["name"] for p in json.loads(result.output)]
        self.assertIn("New", names)
        self.assertNotIn("Old", names)

    def test_page_duplicate(self):
        self.invoke(["page", "create", "Original"])
        result = self.invoke(["page", "duplicate", "Original", "--new-name", "Copy"])
        self.assertEqual(result.exit_code, 0)
        result = self.invoke_json(["page", "list"])
        names = [p["name"] for p in json.loads(result.output)]
        self.assertIn("Original", names)
        self.assertIn("Copy", names)

    def test_page_export_import(self):
        self.invoke(["page", "create", "ForExport"])
        export_dir = tempfile.mkdtemp()
        try:
            result = self.invoke(["page", "export", "ForExport", export_dir])
            self.assertEqual(result.exit_code, 0)

            export_file = os.path.join(export_dir, "ForExport.json")
            self.assertTrue(os.path.isfile(export_file))

            self.invoke(["page", "delete", "ForExport", "-y"])
            result = self.invoke(["page", "import", export_file, "--name", "Imported"])
            self.assertEqual(result.exit_code, 0)

            result = self.invoke_json(["page", "list"])
            names = [p["name"] for p in json.loads(result.output)]
            self.assertIn("Imported", names)
        finally:
            shutil.rmtree(export_dir)

    def test_page_delete_nonexistent(self):
        result = self.invoke(["page", "delete", "Ghost", "-y"])
        self.assertNotEqual(result.exit_code, 0)


class TestButtonCLI(TestCLIBase):
    def setUp(self):
        super().setUp()
        self.invoke(["page", "create", "TestPage"])

    def test_button_list_empty(self):
        result = self.invoke(["button", "list", "TestPage"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No configured buttons", result.output)

    def test_button_set_label(self):
        result = self.invoke(["button", "set-label", "TestPage", "0x0", "Hello"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Set bottom label", result.output)

    def test_button_set_label_json(self):
        result = self.invoke_json(["button", "set-label", "TestPage", "0x0", "Hello"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertEqual(data["status"], "ok")

    def test_button_set_label_positions(self):
        self.invoke(["button", "set-label", "TestPage", "0x0", "Top", "-p", "top"])
        self.invoke(["button", "set-label", "TestPage", "0x0", "Center", "-p", "center"])
        self.invoke(["button", "set-label", "TestPage", "0x0", "Bottom", "-p", "bottom"])

        result = self.invoke_json(["button", "inspect", "TestPage", "0x0"])
        data = json.loads(result.output)
        labels = data["data"]["labels"]
        self.assertEqual(labels["top"]["text"], "Top")
        self.assertEqual(labels["center"]["text"], "Center")
        self.assertEqual(labels["bottom"]["text"], "Bottom")

    def test_button_clear_label(self):
        self.invoke(["button", "set-label", "TestPage", "0x0", "Test"])
        result = self.invoke(["button", "clear-label", "TestPage", "0x0"])
        self.assertEqual(result.exit_code, 0)

    def test_button_set_image(self):
        img_path = os.path.join(self.tmpdir, "icon.png")
        with open(img_path, "w") as f:
            f.write("fake")
        result = self.invoke(["button", "set-image", "TestPage", "0x0", img_path])
        self.assertEqual(result.exit_code, 0)

    def test_button_clear_image(self):
        img_path = os.path.join(self.tmpdir, "icon.png")
        with open(img_path, "w") as f:
            f.write("fake")
        self.invoke(["button", "set-image", "TestPage", "0x0", img_path])
        result = self.invoke(["button", "clear-image", "TestPage", "0x0"])
        self.assertEqual(result.exit_code, 0)

    def test_button_set_action(self):
        result = self.invoke(["button", "set-action", "TestPage", "0x0",
                              "test::Action", "--settings", '{"key": "val"}'])
        self.assertEqual(result.exit_code, 0)

    def test_button_add_action(self):
        self.invoke(["button", "set-action", "TestPage", "0x0", "test::Action1"])
        self.invoke(["button", "add-action", "TestPage", "0x0", "test::Action2"])

        result = self.invoke_json(["button", "inspect", "TestPage", "0x0"])
        data = json.loads(result.output)
        actions = data["data"]["actions"]
        self.assertEqual(len(actions), 2)

    def test_button_clear_actions(self):
        self.invoke(["button", "set-action", "TestPage", "0x0", "test::Action"])
        result = self.invoke(["button", "clear-actions", "TestPage", "0x0"])
        self.assertEqual(result.exit_code, 0)

    def test_button_list_after_config(self):
        self.invoke(["button", "set-label", "TestPage", "0x0", "Key1"])
        self.invoke(["button", "set-label", "TestPage", "1x0", "Key2"])
        result = self.invoke_json(["button", "list", "TestPage"])
        data = json.loads(result.output)
        self.assertEqual(len(data), 2)


class TestPluginCLI(TestCLIBase):
    def setUp(self):
        super().setUp()
        # Create a fake plugin
        plugin_dir = os.path.join(self.tmpdir, "plugins", "dev_test_Plugin")
        os.makedirs(plugin_dir)
        manifest = {
            "id": "dev_test_Plugin",
            "name": "Test Plugin",
            "version": "2.0.0",
            "author": "TestDev",
            "actions": {
                "dev_test_Plugin::Run": {"name": "Run", "description": "Runs stuff"},
            },
        }
        with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)

    def test_plugin_list(self):
        result = self.invoke(["plugin", "list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Test Plugin", result.output)

    def test_plugin_list_json(self):
        result = self.invoke_json(["plugin", "list"])
        data = json.loads(result.output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "dev_test_Plugin")

    def test_plugin_info(self):
        result = self.invoke_json(["plugin", "info", "dev_test_Plugin"])
        data = json.loads(result.output)
        self.assertEqual(data["name"], "Test Plugin")
        self.assertEqual(len(data["actions"]), 1)

    def test_plugin_info_missing(self):
        result = self.invoke(["plugin", "info", "nonexistent"])
        self.assertNotEqual(result.exit_code, 0)

    def test_plugin_search(self):
        result = self.invoke_json(["plugin", "search", "test"])
        data = json.loads(result.output)
        self.assertEqual(len(data), 1)


class TestDeviceCLI(TestCLIBase):
    def test_device_list_empty(self):
        result = self.invoke(["device", "list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No known devices", result.output)

    def test_device_models(self):
        result = self.invoke(["device", "models"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Stream Deck MK.2", result.output)

    def test_device_models_json(self):
        result = self.invoke_json(["device", "models"])
        data = json.loads(result.output)
        model_names = [m["model"] for m in data]
        self.assertIn("Stream Deck +", model_names)


class TestSettingsCLI(TestCLIBase):
    def test_settings_show_empty(self):
        result = self.invoke_json(["settings", "show"])
        data = json.loads(result.output)
        self.assertEqual(data, {})

    def test_settings_set_and_get(self):
        self.invoke(["settings", "set", "store.auto-update", "false"])
        result = self.invoke_json(["settings", "get", "store.auto-update"])
        data = json.loads(result.output)
        self.assertFalse(data["value"])

    def test_settings_brightness(self):
        # Create a deck settings file first
        result = self.invoke(["settings", "brightness", "TEST001", "60"])
        self.assertEqual(result.exit_code, 0)


class TestBackupCLI(TestCLIBase):
    def test_backup_create_and_list(self):
        self.invoke(["page", "create", "ForBackup"])
        result = self.invoke(["backup", "create"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created", result.output)

        result = self.invoke_json(["backup", "list"])
        data = json.loads(result.output)
        self.assertEqual(len(data), 1)

    def test_backup_restore(self):
        self.invoke(["page", "create", "BackupMe"])
        self.invoke(["backup", "create"])
        self.invoke(["page", "delete", "BackupMe", "-y"])

        result = self.invoke_json(["backup", "list"])
        backup_name = json.loads(result.output)[0]["filename"]

        result = self.invoke(["backup", "restore", backup_name, "-y"])
        self.assertEqual(result.exit_code, 0)

        result = self.invoke_json(["page", "list"])
        names = [p["name"] for p in json.loads(result.output)]
        self.assertIn("BackupMe", names)


class TestWorkflow(TestCLIBase):
    """Tests realistic multi-step workflows."""

    def test_full_page_setup_workflow(self):
        """Create a page, configure buttons, export, then import on fresh setup."""
        # Create page
        self.invoke(["page", "create", "Streaming"])

        # Set up buttons
        img = os.path.join(self.tmpdir, "mic.png")
        with open(img, "w") as f:
            f.write("fake")

        self.invoke(["button", "set-label", "Streaming", "0x0", "Mute", "-p", "bottom"])
        self.invoke(["button", "set-image", "Streaming", "0x0", img])
        self.invoke(["button", "set-action", "Streaming", "0x0", "audio::ToggleMute"])

        self.invoke(["button", "set-label", "Streaming", "1x0", "Scene 1", "-p", "bottom"])
        self.invoke(["button", "set-action", "Streaming", "1x0", "obs::SwitchScene",
                      "--settings", '{"scene": "Main"}'])

        # Verify setup
        result = self.invoke_json(["button", "list", "Streaming"])
        buttons = json.loads(result.output)
        self.assertEqual(len(buttons), 2)

        # Export
        export_dir = tempfile.mkdtemp()
        try:
            self.invoke(["page", "export", "Streaming", export_dir])

            # Create fresh data dir and import
            fresh_dir = tempfile.mkdtemp()
            try:
                export_file = os.path.join(export_dir, "Streaming.json")
                fresh_result = self.runner.invoke(
                    cli,
                    ["--data-path", fresh_dir, "page", "import", export_file],
                    catch_exceptions=False,
                )
                self.assertEqual(fresh_result.exit_code, 0)

                # Verify import
                list_result = self.runner.invoke(
                    cli,
                    ["--json", "--data-path", fresh_dir, "button", "list", "Streaming"],
                    catch_exceptions=False,
                )
                imported_buttons = json.loads(list_result.output)
                self.assertEqual(len(imported_buttons), 2)
            finally:
                shutil.rmtree(fresh_dir)
        finally:
            shutil.rmtree(export_dir)

    def test_device_settings_workflow(self):
        """Configure device brightness and default page."""
        self.invoke(["page", "create", "Default"])
        self.invoke(["settings", "brightness", "CL001", "50"])
        self.invoke(["settings", "default-page", "CL001", "Default"])

        result = self.invoke_json(["device", "list"])
        devices = json.loads(result.output)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["serial"], "CL001")
        self.assertEqual(devices[0]["brightness"], 50)

    def test_backup_restore_workflow(self):
        """Full backup/restore cycle with verification."""
        # Create multiple pages
        self.invoke(["page", "create", "Page1"])
        self.invoke(["page", "create", "Page2"])
        self.invoke(["button", "set-label", "Page1", "0x0", "Button1"])

        # Backup
        self.invoke(["backup", "create"])

        # Delete everything
        self.invoke(["page", "delete", "Page1", "-y"])
        self.invoke(["page", "delete", "Page2", "-y"])

        # Verify empty
        result = self.invoke_json(["page", "list"])
        self.assertEqual(json.loads(result.output), [])

        # Restore
        result = self.invoke_json(["backup", "list"])
        backup_name = json.loads(result.output)[0]["filename"]
        self.invoke(["backup", "restore", backup_name, "-y"])

        # Verify restored
        result = self.invoke_json(["page", "list"])
        names = [p["name"] for p in json.loads(result.output)]
        self.assertIn("Page1", names)
        self.assertIn("Page2", names)

        # Verify button data survived
        result = self.invoke_json(["button", "inspect", "Page1", "0x0"])
        data = json.loads(result.output)
        self.assertEqual(data["data"]["labels"]["bottom"]["text"], "Button1")


class TestCLISubprocess(unittest.TestCase):
    """Tests the installed CLI command via subprocess."""

    @staticmethod
    def _resolve_cli(name):
        """Resolve CLI binary path — prefer PATH, fall back to python -m."""
        import shutil as sh
        path = sh.which(name)
        if path:
            return [path]
        # Check if forced to use installed
        if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
            raise RuntimeError(f"CLI_ANYTHING_FORCE_INSTALLED is set but '{name}' not found in PATH")
        # Fall back to python -m
        return [sys.executable, "-m", "cli_anything.streamcontroller.streamcontroller_cli"]

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cli_cmd = self._resolve_cli("cli-anything-streamcontroller")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def run_cli(self, args):
        result = subprocess.run(
            self.cli_cmd + ["--data-path", self.tmpdir] + args,
            capture_output=True, text=True, timeout=30,
        )
        return result

    def test_help(self):
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("StreamController CLI", result.stdout)

    def test_page_create_and_list(self):
        result = self.run_cli(["page", "create", "SubTest"])
        self.assertEqual(result.returncode, 0)

        result = self.run_cli(["--json", "page", "list"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "SubTest")

    def test_device_models(self):
        result = self.run_cli(["--json", "device", "models"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(len(data) > 0)

    def test_settings_roundtrip(self):
        self.run_cli(["settings", "set", "test.key", '"hello"'])
        result = self.run_cli(["--json", "settings", "get", "test.key"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["value"], "hello")


if __name__ == "__main__":
    unittest.main()

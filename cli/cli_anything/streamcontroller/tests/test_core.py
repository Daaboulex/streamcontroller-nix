"""Unit tests for StreamController CLI core modules — synthetic data, no external deps."""

import json
import os
import shutil
import tempfile
import unittest

from cli_anything.streamcontroller.core.config import resolve_data_path, ensure_data_dirs, DECK_MODELS
from cli_anything.streamcontroller.core.settings import SettingsManager, load_json, save_json
from cli_anything.streamcontroller.core.pages import PageManager
from cli_anything.streamcontroller.core.buttons import ButtonManager
from cli_anything.streamcontroller.core.plugins import PluginManager
from cli_anything.streamcontroller.core.devices import DeviceManager
from cli_anything.streamcontroller.utils.output import OutputFormatter


class TestLoadSaveJson(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_load_missing_file(self):
        self.assertEqual(load_json(os.path.join(self.tmpdir, "missing.json")), {})

    def test_save_and_load(self):
        path = os.path.join(self.tmpdir, "test.json")
        data = {"key": "value", "number": 42}
        save_json(path, data)
        loaded = load_json(path)
        self.assertEqual(loaded, data)

    def test_load_corrupt_json(self):
        path = os.path.join(self.tmpdir, "corrupt.json")
        with open(path, "w") as f:
            f.write("{bad json")
        self.assertEqual(load_json(path), {})

    def test_save_creates_dirs(self):
        path = os.path.join(self.tmpdir, "sub", "dir", "file.json")
        save_json(path, {"hello": "world"})
        self.assertTrue(os.path.isfile(path))


class TestConfig(unittest.TestCase):
    def test_resolve_data_path_override(self):
        result = resolve_data_path("/custom/path")
        self.assertEqual(result, "/custom/path")

    def test_resolve_data_path_tilde(self):
        result = resolve_data_path("~/test")
        self.assertTrue(result.startswith("/"))

    def test_ensure_data_dirs(self):
        tmpdir = tempfile.mkdtemp()
        try:
            data_path = os.path.join(tmpdir, "data")
            ensure_data_dirs(data_path)
            self.assertTrue(os.path.isdir(os.path.join(data_path, "pages")))
            self.assertTrue(os.path.isdir(os.path.join(data_path, "plugins")))
            self.assertTrue(os.path.isdir(os.path.join(data_path, "settings", "decks")))
        finally:
            shutil.rmtree(tmpdir)

    def test_deck_models(self):
        self.assertIn("Stream Deck MK.2", DECK_MODELS)
        mk2 = DECK_MODELS["Stream Deck MK.2"]
        self.assertEqual(mk2["keys"], 15)
        self.assertEqual(mk2["cols"], 5)
        self.assertEqual(mk2["rows"], 3)


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        ensure_data_dirs(self.tmpdir)
        self.settings = SettingsManager(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_app_settings_empty(self):
        self.assertEqual(self.settings.get_app_settings(), {})

    def test_app_settings_roundtrip(self):
        data = {"store": {"auto-update": False}, "system": {"autostart": True}}
        self.settings.save_app_settings(data)
        loaded = self.settings.get_app_settings()
        self.assertEqual(loaded, data)

    def test_get_set_app_setting(self):
        self.settings.set_app_setting(False, "store", "auto-update")
        val = self.settings.get_app_setting("store", "auto-update")
        self.assertFalse(val)

    def test_deck_brightness(self):
        self.settings.set_deck_brightness("ABC123", 50)
        self.assertEqual(self.settings.get_deck_brightness("ABC123"), 50)

    def test_deck_brightness_clamped(self):
        self.settings.set_deck_brightness("ABC123", 150)
        self.assertEqual(self.settings.get_deck_brightness("ABC123"), 100)
        self.settings.set_deck_brightness("ABC123", -10)
        self.assertEqual(self.settings.get_deck_brightness("ABC123"), 0)

    def test_default_page(self):
        self.settings.set_default_page("ABC123", "/path/to/page.json")
        self.assertEqual(self.settings.get_default_page("ABC123"), "/path/to/page.json")

    def test_list_known_serials(self):
        self.settings.set_deck_brightness("DEV001", 75)
        self.settings.set_deck_brightness("DEV002", 80)
        serials = self.settings.list_known_serials()
        self.assertIn("DEV001", serials)
        self.assertIn("DEV002", serials)

    def test_screensaver(self):
        self.settings.set_deck_screensaver("ABC123", enable=True, time_delay=10)
        ss = self.settings.get_deck_screensaver("ABC123")
        self.assertTrue(ss.get("enable"))
        self.assertEqual(ss.get("time_delay"), 10)


class TestPageManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        ensure_data_dirs(self.tmpdir)
        self.pm = PageManager(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_list_empty(self):
        self.assertEqual(self.pm.list_pages(), [])

    def test_create_and_list(self):
        self.pm.create_page("TestPage")
        pages = self.pm.list_pages()
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]["name"], "TestPage")

    def test_create_duplicate_raises(self):
        self.pm.create_page("TestPage")
        with self.assertRaises(FileExistsError):
            self.pm.create_page("TestPage")

    def test_delete(self):
        self.pm.create_page("ToDelete")
        self.pm.delete_page("ToDelete")
        self.assertEqual(self.pm.list_pages(), [])

    def test_delete_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.pm.delete_page("Nonexistent")

    def test_rename(self):
        self.pm.create_page("OldName")
        self.pm.rename_page("OldName", "NewName")
        pages = self.pm.list_pages()
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]["name"], "NewName")

    def test_duplicate(self):
        self.pm.create_page("Original")
        self.pm.duplicate_page("Original", "Copy")
        names = [p["name"] for p in self.pm.list_pages()]
        self.assertIn("Original", names)
        self.assertIn("Copy", names)

    def test_export_import(self):
        self.pm.create_page("ForExport", {"keys": {"0x0": {"states": {"0": {}}}}})
        export_dir = tempfile.mkdtemp()
        try:
            export_path = self.pm.export_page("ForExport", export_dir)
            self.assertTrue(os.path.isfile(export_path))

            self.pm.delete_page("ForExport")
            import_path = self.pm.import_page(export_path, "Imported")
            pages = self.pm.list_pages()
            self.assertEqual(len(pages), 1)
            self.assertEqual(pages[0]["name"], "Imported")
        finally:
            shutil.rmtree(export_dir)

    def test_inspect(self):
        page_data = {
            "keys": {
                "0x0": {
                    "states": {
                        "0": {
                            "labels": {"bottom": {"text": "Hello"}},
                            "media": {"path": "/img.png"},
                            "actions": [{"id": "test::Action"}],
                        }
                    }
                }
            },
            "settings": {
                "brightness": {"overwrite": True, "value": 50},
            },
        }
        self.pm.create_page("Detailed", page_data)
        info = self.pm.inspect_page("Detailed")
        self.assertEqual(info["name"], "Detailed")
        self.assertEqual(info["n_keys"], 1)
        self.assertEqual(len(info["keys"]), 1)
        key = info["keys"][0]
        self.assertEqual(key["coordinate"], "0x0")
        self.assertEqual(key["states"][0]["labels"]["bottom"], "Hello")

    def test_backup_and_restore(self):
        self.pm.create_page("BackupTest", {"test": True})
        backup_path = self.pm.create_backup()
        self.assertTrue(os.path.isfile(backup_path))

        backups = self.pm.list_backups()
        self.assertEqual(len(backups), 1)

        self.pm.delete_page("BackupTest")
        count = self.pm.restore_backup(os.path.basename(backup_path))
        self.assertEqual(count, 1)
        pages = self.pm.list_pages()
        self.assertEqual(len(pages), 1)

    def test_case_insensitive_lookup(self):
        self.pm.create_page("MyPage")
        path = self.pm.get_page_path("mypage")
        self.assertIsNotNone(path)


class TestButtonManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        ensure_data_dirs(self.tmpdir)
        self.pm = PageManager(self.tmpdir)
        self.bm = ButtonManager(self.tmpdir)
        self.pm.create_page("TestPage")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_set_label(self):
        self.bm.set_label("TestPage", "0x0", "bottom", "Hello")
        labels = self.bm.get_labels("TestPage", "0x0")
        self.assertEqual(labels["bottom"]["text"], "Hello")

    def test_set_label_with_font(self):
        self.bm.set_label("TestPage", "1x0", "center", "World",
                          font_family="Arial", font_size=16, color=[255, 0, 0, 255])
        labels = self.bm.get_labels("TestPage", "1x0")
        self.assertEqual(labels["center"]["text"], "World")
        self.assertEqual(labels["center"]["font-family"], "Arial")
        self.assertEqual(labels["center"]["font-size"], 16)

    def test_clear_label(self):
        self.bm.set_label("TestPage", "0x0", "bottom", "Test")
        self.bm.clear_label("TestPage", "0x0", "bottom")
        labels = self.bm.get_labels("TestPage", "0x0")
        self.assertNotIn("bottom", labels)

    def test_set_image(self):
        img_path = os.path.join(self.tmpdir, "test.png")
        with open(img_path, "w") as f:
            f.write("fake png")
        self.bm.set_image("TestPage", "0x0", img_path)
        result = self.bm.get_image("TestPage", "0x0")
        self.assertEqual(result, os.path.abspath(img_path))

    def test_set_image_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.bm.set_image("TestPage", "0x0", "/nonexistent/image.png")

    def test_clear_image(self):
        img_path = os.path.join(self.tmpdir, "test.png")
        with open(img_path, "w") as f:
            f.write("fake png")
        self.bm.set_image("TestPage", "0x0", img_path)
        self.bm.clear_image("TestPage", "0x0")
        result = self.bm.get_image("TestPage", "0x0")
        self.assertIsNone(result)

    def test_set_action(self):
        self.bm.set_action("TestPage", "0x0", "test::Action", settings={"key": "val"})
        actions = self.bm.get_actions("TestPage", "0x0")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["id"], "test::Action")
        self.assertEqual(actions[0]["settings"]["key"], "val")

    def test_add_action(self):
        self.bm.set_action("TestPage", "0x0", "test::Action1")
        self.bm.add_action("TestPage", "0x0", "test::Action2")
        actions = self.bm.get_actions("TestPage", "0x0")
        self.assertEqual(len(actions), 2)

    def test_clear_actions(self):
        self.bm.set_action("TestPage", "0x0", "test::Action")
        self.bm.clear_actions("TestPage", "0x0")
        actions = self.bm.get_actions("TestPage", "0x0")
        self.assertEqual(len(actions), 0)

    def test_list_keys(self):
        self.bm.set_label("TestPage", "0x0", "bottom", "Key1")
        self.bm.set_label("TestPage", "1x0", "center", "Key2")
        keys = self.bm.list_keys("TestPage")
        self.assertEqual(len(keys), 2)

    def test_coord_formats(self):
        """Test that comma and parenthesized coords are normalized."""
        self.bm.set_label("TestPage", "0,0", "bottom", "Test1")
        self.bm.set_label("TestPage", "(1,0)", "bottom", "Test2")
        labels1 = self.bm.get_labels("TestPage", "0x0")
        labels2 = self.bm.get_labels("TestPage", "1x0")
        self.assertEqual(labels1["bottom"]["text"], "Test1")
        self.assertEqual(labels2["bottom"]["text"], "Test2")

    def test_multiple_states(self):
        self.bm.set_label("TestPage", "0x0", "bottom", "State0", state=0)
        self.bm.set_label("TestPage", "0x0", "bottom", "State1", state=1)
        s0 = self.bm.get_key_state("TestPage", "0x0", 0)
        s1 = self.bm.get_key_state("TestPage", "0x0", 1)
        self.assertEqual(s0["labels"]["bottom"]["text"], "State0")
        self.assertEqual(s1["labels"]["bottom"]["text"], "State1")

    def test_missing_page_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.bm.set_label("NoSuchPage", "0x0", "bottom", "Test")


class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        ensure_data_dirs(self.tmpdir)
        self.plm = PluginManager(self.tmpdir)
        # Create a fake plugin
        plugin_dir = os.path.join(self.tmpdir, "plugins", "dev_test_Plugin")
        os.makedirs(plugin_dir)
        manifest = {
            "id": "dev_test_Plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "author": "TestAuthor",
            "description": "A test plugin",
            "actions": {
                "dev_test_Plugin::DoThing": {
                    "name": "Do Thing",
                    "description": "Does a thing",
                }
            },
        }
        with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_list_plugins(self):
        plugins = self.plm.list_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["id"], "dev_test_Plugin")
        self.assertEqual(plugins[0]["version"], "1.0.0")

    def test_get_plugin_info(self):
        info = self.plm.get_plugin_info("dev_test_Plugin")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "Test Plugin")
        self.assertEqual(len(info["actions"]), 1)
        self.assertEqual(info["actions"][0]["id"], "dev_test_Plugin::DoThing")

    def test_get_missing_plugin(self):
        info = self.plm.get_plugin_info("nonexistent")
        self.assertIsNone(info)

    def test_search(self):
        results = self.plm.search_plugins("test")
        self.assertEqual(len(results), 1)
        results = self.plm.search_plugins("nonexistent")
        self.assertEqual(len(results), 0)


class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        ensure_data_dirs(self.tmpdir)
        self.dm = DeviceManager(self.tmpdir)
        self.settings = SettingsManager(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_list_no_devices(self):
        devices = self.dm.list_known_devices()
        self.assertEqual(len(devices), 0)

    def test_list_with_settings(self):
        self.settings.set_deck_brightness("DEV001", 60)
        self.settings.set_default_page("DEV001", "/path/to/page.json")
        devices = self.dm.list_known_devices()
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["serial"], "DEV001")
        self.assertEqual(devices[0]["brightness"], 60)

    def test_get_device_info(self):
        self.settings.set_deck_brightness("DEV001", 80)
        info = self.dm.get_device_info("DEV001")
        self.assertIsNotNone(info)
        self.assertEqual(info["brightness"], 80)

    def test_get_missing_device(self):
        info = self.dm.get_device_info("MISSING")
        self.assertIsNone(info)

    def test_list_models(self):
        models = DeviceManager.list_supported_models()
        self.assertTrue(len(models) > 0)
        model_names = [m["model"] for m in models]
        self.assertIn("Stream Deck MK.2", model_names)


class TestOutputFormatter(unittest.TestCase):
    def test_human_mode(self):
        out = OutputFormatter(json_mode=False)
        # Shouldn't raise
        out.print_result({"key": "value"})
        out.print_success("Done")
        out.print_error("Failed")

    def test_json_mode(self):
        import io
        out = OutputFormatter(json_mode=True)
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            out.print_result({"key": "value"})
            output = sys.stdout.getvalue()
            parsed = json.loads(output)
            self.assertEqual(parsed["key"], "value")
        finally:
            sys.stdout = old_stdout


import sys

if __name__ == "__main__":
    unittest.main()
